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
                        'source': 'tavily_search',
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

response = await search_web("recent foreign trade news")
print(response)
print(type(response))

# %%
