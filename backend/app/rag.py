import os
import requests 
from typing import List
import anthropic
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents.base import Document
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/dongj/MarketBuddy/.env.local")

os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

async def main() -> List[Document]:  
    docs = []

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://finance.yahoo.com')
        await page.wait_for_timeout(5000)

        article_links = await page.query_selector_all('a.subtle-link')
        urls = set()
        for link in article_links:
            href = await link.get_attribute("href")
            if href == "https://finance.yahoo.com/news/":
                continue
            elif href and href.startswith("https://finance.yahoo.com/news/"):
                urls.add(href)
        print(f"found {len(urls)} articles")

        for url in urls:
            try:
                await page.goto(url)
                print(f"\n {url}")
                await page.wait_for_selector("div.atoms-wrapper", timeout=10000)
                paragraphs = await page.query_selector_all("div.atoms-wrapper > p")
                content = "\n".join([await p.inner_text() for p in paragraphs])
                docs.append(Document(page_content=content, metadata={"source": "Playwright", "url": url}))
            except Exception as e:
                print(f"failed to read page {url} : {e} \n Likely a premium article.. ")    
                continue
            

        await browser.close()
    return docs

def initialize_vectorstore(docs: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100, add_start_index=True)
    all_splits = text_splitter.split_documents(docs)
    local_embeddings = OllamaEmbeddings(model="all-minilm")

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)
    return vectorstore

class ParsedDocument:
    def __init__(self, page_content: str, url: str):
        self.page_content = page_content
        self.url = url

async def search_web(query : str) -> List[Document]:
    tavily_client = TavilyClient(api_key=(os.getenv("TAVILY_API_KEY")))
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        include_raw_content=True,
        max_result=5,

    )
    print(response, type(response))
    parsed_responses = fit_to_document(response)
    print(parsed_responses)

    return parsed_responses

def fit_to_document (search_results):
    parsed_documents = []

    results = search_results['results']
    for i, result in enumerate(results):

        try:
            content = ""
            url = result.get('url', '')
            title = result.get('title', '')

            if result.get('raw_content') and len(result['raw_content'].strip()) > 100:
                content = result['raw_content']
            elif result.get('content') and len(result['content'].strip()) > 50:
                content = result['content']
            else:
                print(f"skipping result {i + 1} -- insufficient material")
                continue

            cleaned_content = clean_content(content, title)
            if len(cleaned_content.strip()) > 100:
                document = Document(
                    page_content=cleaned_content,
                    metadata={
                        'url': url,
                        'title': title,
                        'source': 'Tavily',
                        'score': result.get('score', 0)
                    }
                )
                parsed_documents.append(document) 
            else:
                print(f"content too short, skipped for: {i+1}")
        except Exception as a:
            print(f"error proccessing result {i+1}: {a} ")
            continue
        
    return parsed_documents 

def clean_content(content: str, title: str = "") -> str:
    """
    Clean and format content for better LLM consumption
    """
    # Remove common unwanted patterns
    unwanted_patterns = [
        "Subscribe to our newsletter",
        "Sign up for",
        "Follow us on",
        "Click here",
        "Read more",
        "Advertisement",
        "Cookie Policy",
        "Privacy Policy",
        "Terms of Service",
        "© 2024",
        "© 2025"
    ]
    
    # Split into lines and filter
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines, very short lines, or unwanted patterns
        if len(line) < 10:
            continue
            
        # Check for unwanted patterns
        if any(pattern.lower() in line.lower() for pattern in unwanted_patterns):
            continue
            
        # Skip lines that are mostly non-alphabetic (likely navigation/UI elements)
        alpha_ratio = sum(c.isalpha() for c in line) / len(line) if line else 0
        if alpha_ratio < 0.6:
            continue
            
        cleaned_lines.append(line)
    
    # Join and add title if available
    cleaned_content = '\n'.join(cleaned_lines)
    
    if title and title.lower() not in cleaned_content.lower()[:200]:
        cleaned_content = f"{title}\n\n{cleaned_content}"
    
    return cleaned_content

def generate_answer(question: str, retriever) -> str:
    if retriever is None:
        raise RuntimeError("Retriever not initialized yet")

    retrieved_docs = retriever.invoke(question)
    source_counts = {"Playwright": 0, "Tavily": 0}

    for doc in retrieved_docs:
        source = doc.metadata.get("source")
        source_counts[source] += 1

    context = ' '.join([doc.page_content for doc in retrieved_docs])

    

    llm = OllamaLLM(model="llama3.2:1b")
    prompt = f"""
    ------ Instructions ------
     Follow these instructions sequentially. 
    
     You are a helpful seasoned financial analyst at a Fortune 500 company.
     Prioritize recent information, with the current year in mind.

    - Given the question regarding finance, 
    - Check if the question asks about a specific stock or sector
    - Check if the question asks a general question about the market state or things to look out for
    - Check if the question asks about a specific event that has occured.
    - If a specific stock/sector is mentioned, based on the latest financial reports and market news from multiple sources, summarize how today's events are likely to affect the stock mentioned.
    - Focus on earnings, regulartory events, analyst forecasts, and market sentiment. 
    - If a specific stock/sector is mentioned but the context does not discuss the stock/sector, respond with "No significant impact on [stock/sector]" or similar phrasing. 
    - If a specific event is mentioned, focus on how the provided context describes the event, and mention any possible impacts from that event in financial sectors.
    - If a general and open ended question about the market is asked, instead give a summary about the most important or key events. 
    - If a general financial question is asked that would not require the context, instead reply to the best of your ability, acting as a financial analyst expert.
    - If the question is along the lines of "What stock should I invest in", give your best reccomendation assuming you are a financial analyst. Stray away from recent events, and instead give general advice. 
    - Format your response in a markdown friendly format.
    - Create spaces via newlines in between each section of text you create.

    - You are to provide a direct answer ONLY to the question. 

    """

    client = anthropic.Anthropic(api_key=(os.getenv("ANTHROPIC_API_KEY")))

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens = 1000,
        temperature = 1,
        system = f"{prompt}",
        messages=[
        {
            "role": "user", 
            "content": f"""
            The user has asked you a financial question. Answer the question to the best of your ability using the context given. Give your professional opinion.
            
            <question>
            {question}
            </question>

            <context>
            {context}
            </context>
            """
        }
        ]
    )

    response_text = "failed to generate output."

    if response.content[0].type == "text":
        response_text = response.content[0].text
    print(response_text)
    print(f"TESTING PURPOSES : Playwright - {source_counts['Playwright']}, Tavily - {source_counts['Tavily']}")
    return response_text

    
