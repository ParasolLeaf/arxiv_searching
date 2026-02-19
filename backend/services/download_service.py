import os
import re
import httpx
from models.schemas import DownloadResponse

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip()[:100]  # Limit length
    return name


async def download_paper(arxiv_id: str, title: str, pdf_url: str) -> DownloadResponse:
    """Download a paper PDF from arXiv."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    safe_title = sanitize_filename(title)
    safe_id = arxiv_id.replace("/", "_").replace(".", "_")
    filename = f"{safe_id}_{safe_title}.pdf"
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    # Skip if already downloaded
    if os.path.exists(file_path):
        return DownloadResponse(
            success=True,
            message="论文已存在，无需重复下载。",
            file_path=file_path,
        )

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)

        return DownloadResponse(
            success=True,
            message=f"下载成功：{filename}",
            file_path=file_path,
        )

    except httpx.HTTPError as e:
        return DownloadResponse(
            success=False,
            message=f"下载失败：{str(e)}",
            file_path=None,
        )


def list_downloaded_papers() -> list[dict]:
    """List all downloaded PDFs."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    papers = []
    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            papers.append({
                "filename": filename,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
            })
    return papers
