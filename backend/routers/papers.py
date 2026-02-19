from fastapi import APIRouter
from models.schemas import Paper, DownloadResponse
from services.download_service import download_paper, list_downloaded_papers

router = APIRouter(tags=["papers"])


class DownloadRequest(Paper):
    pass


@router.post("/papers/download", response_model=DownloadResponse)
async def download(paper: DownloadRequest):
    """Download a paper PDF to local storage."""
    return await download_paper(
        arxiv_id=paper.arxiv_id,
        title=paper.title,
        pdf_url=paper.pdf_url,
    )


@router.get("/downloads")
async def get_downloads():
    """List all downloaded papers."""
    return list_downloaded_papers()
