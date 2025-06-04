import os
from typing import List
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document

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
                docs.append(Document(page_content=content, metadata={"source": url}))
            except Exception as e:
                print(f"failed to read page {url} : {e} \n Likely a premium article.. ")
                continue
            

        await browser.close()
    return docs

def initialize_retriever(docs: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100, add_start_index=True)
    all_splits = text_splitter.split_documents(docs)
    local_embeddings = OllamaEmbeddings(model="all-minilm")

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})  

def generate_answer(question: str, retriever) -> str:
    if retriever is None:
        raise RuntimeError("Retriever not initialized yet")

    retrieved_docs = retriever.invoke(question)
    context = ' '.join([doc.page_content for doc in retrieved_docs])

    llm = OllamaLLM(model="llama3.2:1b")
    prompt = f"""
    ------ Instructions ------
     Follow these instructions sequentially. 

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
    ----- QUESTION ------
    {question}
    ----- CONTEXT -------
    {context}
    """
    response = llm.invoke(prompt)
    print(response)
    return response
