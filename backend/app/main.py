import sys
import asyncio
from typing import Optional

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app import rag
from contextlib import asynccontextmanager



vectorstore = None
initial_docs = []

@asynccontextmanager
async def lifespan(app: FastAPI):
  global vectorstore, initial_docs

  initial_docs = await rag.main()
  vectorstore = rag.initialize_vectorstore(initial_docs)

  yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.post("/api/ask")
async def ask_question(request: Request):
  global vectorstore



  data = await request.json()
  question = data["question"]

  web_results = await rag.search_web(question)

  if vectorstore is not None:
    vectorstore.add_documents(web_results)
  else:
    # Handle the case where vectorstore is not initialized
    return {"error": "Vectorstore not initialized"}
  vectorstore.add_documents(web_results)

  retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
  answer = rag.generate_answer(question, retriever)
  return {"answer": answer}


