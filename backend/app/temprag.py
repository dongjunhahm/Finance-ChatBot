import bs4
import os
import asyncio
import requests
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4.filter import SoupStrainer
from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document

#wtf is this 
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

#specific to yahoo finance main page -> need to figure out how to access individual articles 
#or maybe article titles are enough? need to rethink
docs = []
async def main(): 
  global docs
  async with async_playwright() as p: 
    browser = await p.firefox.launch(
      headless=False,
    )
    page = await browser.new_page()
    await page.goto('https://finance.yahoo.com')
    await page.wait_for_timeout(5000)

    article_links = await page.query_selector_all(
      'a.subtle-link'
    )
    
    urls = set()
    for link in article_links:
      href = await link.get_attribute("href")
      if href and href.startswith("https://finance.yahoo.com/news"):
        urls.add(href)
    print(f"found {len(urls)} articles")

    for url in urls:
      await page.goto(url)
      print(f"\n {url}")
      content = ""
      paragraphs = await page.query_selector_all("article p")
      if not paragraphs:
        paragraphs = await page.query_selector_all("div[class*='caas-body'] p")
      for p in paragraphs:
        content += await p.inner_text() + "\n"
      
      docs.append(Document(page_content=content, metadata={"source": url}))

    await browser.close()

print("here you go", type(docs))
print("testing", docs)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1200, chunk_overlap=100, add_start_index=True
)
#splitting everything contained in the docs into manageable chunks
all_splits = text_splitter.split_documents(docs)


#translator for words into numerical format 
local_embeddings = OllamaEmbeddings(model="all-minilm")
#vectorstore
vectorstore = Chroma.from_documents(documents=all_splits,
                                    embedding = local_embeddings)

#implementing retrieval system 
#looking for the most similar documents in our vector store to the query given
#k = 3 gives top 3 most similar documents to question
retriever = vectorstore.as_retriever(search_type="similarity",
                                    search_kwargs={"k": 3})

def generate_answer(question): 
  global retriever
  if retriever is None:
    raise RuntimeError("retriever not initialized yet")
  #must now actually call the retriever on the given query, which in thsi case is question 
  retrieved_docs = retriever.invoke(question)

  #formatting the retrieved relevant page contents into formatted context for the llm 
  #might have to change page_content here to whatever is actually scraped from on yahoo finance 
  context = ' '.join([doc.page_content for doc in retrieved_docs])


  #generating response with LLM 
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
  return(response)

if __name__ == "__main__":
    asyncio.run(main())
