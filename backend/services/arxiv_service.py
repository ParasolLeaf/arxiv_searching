import arxiv
from models.schemas import Paper


async def search_arxiv(
    query: str,
    max_results: int = 25,
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
) -> list[Paper]:
    """Search arXiv for papers matching the query."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers = []
    for result in client.results(search):
        paper = Paper(
            arxiv_id=result.entry_id.split("/abs/")[-1],
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            published=result.published.strftime("%Y-%m-%d"),
            categories=result.categories,
            pdf_url=result.pdf_url,
        )
        papers.append(paper)

    return papers
