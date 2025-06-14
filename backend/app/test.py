#%%
import os
import requests 
from typing import List
from langchain_core.documents.base import Document
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/dongj/MarketBuddy/.env.local")

class ParsedDocument:
    def __init__(self, page_content: str, url: str):
        self.page_content = page_content
        self.url = url

async def search_web(query : str) -> List[Document]:
    tavily_client = TavilyClient(api_key=(os.getenv("TAVILY_API_KEY")))
    response = tavily_client.search(query)
    print(response, type(response))
    parsed_responses = fit_to_document(response)
    print(parsed_responses)

    return parsed_responses

def fit_to_document (search_results):
    parsed_documents = []

    results = search_results['results']
    for result in results:

        content = result.get('content', '')
        url = result.get('url', '')

        if content and url:
            parsed_document = ParsedDocument(page_content = content, url=url)
            document = Document(page_content=parsed_document.page_content, 
                    metadata={'url': parsed_document.url})
            parsed_documents.append(document)

    return parsed_documents 

response = await search_web("recent foreign trade news")
print(response)
print(type(response))

# %%
