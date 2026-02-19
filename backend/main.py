import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import chat, papers

app = FastAPI(title="arXiv Paper Recommender", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(papers.router, prefix="/api")

# Ensure downloads directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "downloads"), exist_ok=True)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
