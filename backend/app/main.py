import sys
import asyncio

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.temprag import generate_answer
from app import temprag
from contextlib import asynccontextmanager


retriever = None
docs = []

@asynccontextmanager
async def lifespan(app: FastAPI):
  global retriever, docs

  docs = await temprag.main()
  retriever = temprag.initialize_retriever(docs)

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
  answer = generate_answer(question, retriever)
  return {"answer": answer}


