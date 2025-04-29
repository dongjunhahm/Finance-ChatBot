from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.rag import generate_answer

app = FastAPI()

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
  question = data.get("question", "")
  answer = generate_answer(question) #rag logic here
  return {"answer": answer}


