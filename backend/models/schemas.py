from pydantic import BaseModel
from datetime import datetime


class Paper(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published: str
    categories: list[str]
    pdf_url: str
    relevance_score: float | None = None
    relevance_reason: str | None = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    current_papers: list[Paper] = []


class ChatResponse(BaseModel):
    reply: str
    papers: list[Paper] = []
    search_query: str | None = None


class DownloadResponse(BaseModel):
    success: bool
    message: str
    file_path: str | None = None


class DownloadedPaper(BaseModel):
    arxiv_id: str
    title: str
    file_path: str
    file_size: int
