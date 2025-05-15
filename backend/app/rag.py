import bs4
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4.filter import SoupStrainer
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama.llms import OllamaLLM

#wtf is this 
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

#specific to yahoo finance main page -> need to figure out how to access individual articles 
#or maybe article titles are enough? need to rethink
bs4_strainer = bs4.filter.SoupStrainer(class_="module-hero hero-3-col yf-36pijq")
loader = WebBaseLoader(
    web_paths=("https://finance.yahoo.com/",),
    #specifies how you want to look at the things in the bs4_strainer var
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1200, chunk_overlap=100, add_start_index=True
)
#splitting everything contained in the docs into manageable chunks
all_splits = text_splitter.split_documents(docs)
print(all_splits)


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
    - If a specific stock/sector is mentioned, focus on how the provided context may affect the stock/sector mentioned.
    - If a specific stock/sector is mentioned but the context does not discuss the stock/sector, respond with "No significant impact on [stock/sector]" or similar phrasing. 
    - If a general and open ended question about the market is asked, instead give a summary about the most important or key events. 

    - You are to provide a direct answer to the question. 

    ----- QUESTION ------ 
    {question}

    ----- CONTEXT -------
    {context}
    """
  response = llm.invoke(prompt)
  print(response)
  return(response)