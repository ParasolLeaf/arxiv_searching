import arxiv
from datetime import datetime, timedelta
from models.schemas import Paper

# Default time window: papers from the last 2 years
DEFAULT_DATE_WINDOW_DAYS = 730


def _build_date_query(query: str, days_back: int = DEFAULT_DATE_WINDOW_DAYS) -> str:
    """Append a submittedDate range filter to an arXiv query string."""
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)
    date_range = (
        f"submittedDate:[{start.strftime('%Y%m%d')}0000"
        f" TO {end.strftime('%Y%m%d')}2359]"
    )
    return f"({query}) AND {date_range}"


async def search_arxiv(
    query: str,
    max_results: int = 50,
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
            comment=result.comment,
        )
        papers.append(paper)

    return papers


async def dual_strategy_search(
    query: str,
    max_per_strategy: int = 50,
) -> list[Paper]:
    """Search with dual strategy: relevance-sorted + date-sorted, merged and deduplicated."""
    seen_ids: set[str] = set()
    all_papers: list[Paper] = []

    # Strategy 1: Recent papers sorted by relevance
    date_query = _build_date_query(query)
    relevance_papers = await search_arxiv(
        query=date_query,
        max_results=max_per_strategy,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    for paper in relevance_papers:
        if paper.arxiv_id not in seen_ids:
            seen_ids.add(paper.arxiv_id)
            all_papers.append(paper)

    # Strategy 2: Latest papers sorted by submission date
    date_papers = await search_arxiv(
        query=query,
        max_results=max_per_strategy,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    for paper in date_papers:
        if paper.arxiv_id not in seen_ids:
            seen_ids.add(paper.arxiv_id)
            all_papers.append(paper)

    return all_papers


async def multi_query_search(
    queries: list[str],
    max_per_query: int = 50,
) -> list[Paper]:
    """Search arXiv with multiple queries using dual strategy and merge deduplicated results."""
    seen_ids: set[str] = set()
    all_papers: list[Paper] = []

    for query in queries:
        papers = await dual_strategy_search(
            query=query,
            max_per_strategy=max_per_query,
        )
        for paper in papers:
            if paper.arxiv_id not in seen_ids:
                seen_ids.add(paper.arxiv_id)
                all_papers.append(paper)

    return all_papers
