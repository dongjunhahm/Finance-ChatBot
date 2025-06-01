import sys
import asyncio

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app import rag
from contextlib import asynccontextmanager


retriever = None
docs = []

@asynccontextmanager
async def lifespan(app: FastAPI):
  global retriever, docs

  docs = await rag.main()
  retriever = rag.initialize_retriever(docs)

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
  data = await request.json()
  question = data["question"]
  answer = rag.generate_answer(question, retriever)
  return {"answer": answer}


