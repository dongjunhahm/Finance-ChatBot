import os
import asyncio
from typing import List
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document

os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

async def main() -> List[Document]:  # Renamed to main
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
            await page.goto(url)
            print(f"\n {url}")
            await page.wait_for_selector("div.atoms-wrapper", timeout=10000)
            paragraphs = await page.query_selector_all("div.atoms-wrapper > p")
            content = "\n".join([await p.inner_text() for p in paragraphs])
            docs.append(Document(page_content=content, metadata={"source": url}))

        await browser.close()
    return docs

def initialize_retriever(docs: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100, add_start_index=True)
    all_splits = text_splitter.split_documents(docs)
    local_embeddings = OllamaEmbeddings(model="all-minilm")

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})  # ✅ return retriever

def generate_answer(question: str, retriever) -> str:
    if retriever is None:
        raise RuntimeError("Retriever not initialized yet")

    retrieved_docs = retriever.invoke(question)
    context = ' '.join([doc.page_content for doc in retrieved_docs])

    llm = OllamaLLM(model="llama3.2:1b")
    prompt = f"""
    ------ Instructions ------
    [Your full instruction prompt here...]
    ----- QUESTION ------
    {question}
    ----- CONTEXT -------
    {context}
    """
    response = llm.invoke(prompt)
    print(response)
    return response
