from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse, ChatMessage
from services import llm_service, arxiv_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main conversation endpoint for paper recommendation."""
    # Step 1: Parse user intent
    intent_result = await llm_service.parse_intent(
        message=request.message,
        history=request.history,
        current_papers=request.current_papers,
    )

    intent = intent_result.get("intent", "general")
    arxiv_query = intent_result.get("arxiv_query", "")
    filter_criteria = intent_result.get("filter_criteria", {})
    paper_index = intent_result.get("paper_index")
    explanation = intent_result.get("explanation", "")

    # Step 2: Execute based on intent
    if intent in ("new_search", "refine") and request.search_mode == "abstract":
        # Abstract-based precision recommendation
        return await _handle_abstract_search(request, filter_criteria, explanation)

    if intent == "new_search" and arxiv_query:
        # Dual-strategy search: relevance + recency
        candidates = await arxiv_service.dual_strategy_search(query=arxiv_query)

        # Rank papers using LLM
        ranked_papers = await llm_service.rank_papers(
            user_need=request.message,
            papers=candidates,
            filter_criteria=filter_criteria,
        )

        count = len(ranked_papers)
        total = len(candidates)
        reply = (
            f"根据你的需求「{explanation}」，我从arXiv双轨搜索了 {total} 篇候选论文"
            f"（关键词: {arxiv_query}），为你推荐了 {count} 篇最相关的论文，"
            f"已按相关性排序。你可以继续描述需求来细化筛选。"
        )

        return ChatResponse(
            reply=reply,
            papers=ranked_papers,
            search_query=arxiv_query,
        )

    elif intent == "refine":
        if arxiv_query and arxiv_query.strip():
            # Dual-strategy search with refined query
            candidates = await arxiv_service.dual_strategy_search(query=arxiv_query)
            all_papers = candidates + request.current_papers
            # Deduplicate by arxiv_id
            seen = set()
            unique = []
            for p in all_papers:
                if p.arxiv_id not in seen:
                    seen.add(p.arxiv_id)
                    unique.append(p)
            papers_to_rank = unique
        else:
            papers_to_rank = request.current_papers

        # Re-rank with updated criteria
        ranked_papers = await llm_service.rank_papers(
            user_need=request.message,
            papers=papers_to_rank,
            filter_criteria=filter_criteria,
        )

        count = len(ranked_papers)
        reply = f"已根据你的要求重新筛选，当前展示 {count} 篇论文。"

        return ChatResponse(
            reply=reply,
            papers=ranked_papers,
            search_query=arxiv_query if arxiv_query else None,
        )

    elif intent == "detail" and paper_index is not None:
        # Get detail for a specific paper
        idx = paper_index - 1  # Convert to 0-based
        if 0 <= idx < len(request.current_papers):
            paper = request.current_papers[idx]
            # Extract user need from history
            user_need = request.message
            for msg in reversed(request.history):
                if msg.role == "user":
                    user_need = msg.content
                    break
            detail = await llm_service.generate_detail(paper, user_need)
            return ChatResponse(
                reply=detail,
                papers=request.current_papers,
            )
        else:
            return ChatResponse(
                reply=f"没有找到第 {paper_index} 篇论文，当前列表共 {len(request.current_papers)} 篇。",
                papers=request.current_papers,
            )

    else:
        # General conversation
        reply = await llm_service.generate_reply(request.message, request.history)
        return ChatResponse(
            reply=reply,
            papers=request.current_papers,
        )


async def _handle_abstract_search(
    request: ChatRequest,
    filter_criteria: dict,
    explanation: str,
) -> ChatResponse:
    """Handle abstract-based precision recommendation with multi-query strategy."""
    # Step 1: LLM extracts multiple targeted search queries
    query_result = await llm_service.extract_search_queries(
        message=request.message,
        history=request.history,
    )

    queries = query_result.get("queries", [])
    llm_explanation = query_result.get("explanation", explanation)

    if not queries:
        return ChatResponse(
            reply="无法从你的描述中提取有效的搜索方向，请尝试提供更具体的研究描述或论文摘要。",
            papers=request.current_papers,
        )

    # Step 2: Execute multiple queries with dual strategy and merge results
    candidates = await arxiv_service.multi_query_search(
        queries=queries,
        max_per_query=50,
    )

    if not candidates:
        query_display = "、".join(queries[:3])
        return ChatResponse(
            reply=f"使用多策略搜索（{query_display}）未找到结果，请尝试换一种方式描述你的研究方向。",
            papers=request.current_papers,
        )

    # Step 3: Merge with existing papers if refining
    if request.current_papers:
        seen = {p.arxiv_id for p in candidates}
        for p in request.current_papers:
            if p.arxiv_id not in seen:
                seen.add(p.arxiv_id)
                candidates.append(p)

    # Step 4: LLM ranks all candidates
    ranked_papers = await llm_service.rank_papers(
        user_need=request.message,
        papers=candidates,
        filter_criteria=filter_criteria,
    )

    count = len(ranked_papers)
    total_candidates = len(candidates)
    query_display = "、".join(queries[:3])
    suffix = f"等{len(queries)}个搜索策略" if len(queries) > 3 else ""
    reply = (
        f"根据你的研究描述「{llm_explanation}」，"
        f"我使用了多角度搜索策略（{query_display}{suffix}），"
        f"从 {total_candidates} 篇候选论文中为你精选了 {count} 篇最相关的论文。"
        f"你可以继续描述需求来细化筛选。"
    )

    return ChatResponse(
        reply=reply,
        papers=ranked_papers,
        search_query=query_display,
    )
