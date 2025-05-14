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
print(docs)
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
question = "What is going on in the stock market today?"
#looking for the most similar documents in our vector store to the query given
#k = 3 gives top 3 most similar documents to question
retriever = vectorstore.as_retriever(search_type="similarity",
                                     search_kwargs={"k": 3})
#must now actually call the retriever on the given query, which in thsi case is question 
retrieved_docs = retriever.invoke(question)

#formatting the retrieved relevant page contents into formatted context for the llm 
#might have to change page_content here to whatever is actually scraped from on yahoo finance 
context = ' '.join([doc.page_content for doc in retrieved_docs])







def generate_answer(question): 
    #generating response with LLM 
  llm = OllamaLLM(model="llama3.2:1b")
  response = llm.invoke(f"""Answer the question according to the context given very briefly:
    Question : {question}.
    Context : {context}
    """)
  return(response)