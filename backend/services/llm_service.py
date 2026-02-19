import os
import json
from openai import AsyncOpenAI
from models.schemas import Paper, ChatMessage

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

INTENT_SYSTEM_PROMPT = """你是一个学术论文搜索助手。根据用户的消息和对话历史，判断用户的意图并输出结构化JSON。

可能的意图：
1. "new_search" - 用户想搜索新的论文主题
2. "refine" - 用户想在当前论文列表基础上细化筛选（如过滤时间、增加关键词、排除某些方向）
3. "detail" - 用户想了解某篇论文的详细信息
4. "general" - 闲聊或其他

输出格式（严格JSON）：
{
  "intent": "new_search" | "refine" | "detail" | "general",
  "arxiv_query": "用于arXiv搜索的英文查询词（仅new_search和refine时需要）",
  "filter_criteria": {
    "date_from": "YYYY-MM-DD或null",
    "date_to": "YYYY-MM-DD或null",
    "categories": ["分类列表或空"],
    "exclude_keywords": ["需排除的关键词"],
    "include_keywords": ["需包含的关键词"]
  },
  "paper_index": null,  // detail意图时，用户提到的论文编号（从1开始）
  "explanation": "对用户意图的简短理解"
}"""

RANK_SYSTEM_PROMPT = """你是一个学术论文推荐专家。根据用户的研究需求，对候选论文列表进行相关性评分和排序。

对每篇论文给出：
- relevance_score: 0-10的相关性分数
- relevance_reason: 一句话推荐理由（中文）

输出格式（严格JSON数组）：
[
  {
    "index": 0,
    "relevance_score": 8.5,
    "relevance_reason": "该论文直接研究了..."
  }
]

只输出JSON，不要其他内容。按relevance_score降序排列。"""

DETAIL_SYSTEM_PROMPT = """你是一个学术论文解读专家。请用中文对给定论文进行详细解读，包括：
1. 研究问题和动机
2. 核心方法/贡献
3. 主要结论
4. 与用户研究兴趣的关联

保持简洁但信息丰富，约200-300字。"""


async def parse_intent(
    message: str,
    history: list[ChatMessage],
    current_papers: list[Paper],
) -> dict:
    """Parse user intent from the message."""
    context_messages = [{"role": "system", "content": INTENT_SYSTEM_PROMPT}]

    for msg in history[-10:]:  # Keep last 10 messages for context
        context_messages.append({"role": msg.role, "content": msg.content})

    # Include current papers summary if available
    papers_context = ""
    if current_papers:
        papers_summary = "\n".join(
            f"{i+1}. {p.title} ({p.published})" for i, p in enumerate(current_papers)
        )
        papers_context = f"\n\n当前论文列表：\n{papers_summary}"

    context_messages.append(
        {"role": "user", "content": message + papers_context}
    )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=context_messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


async def rank_papers(
    user_need: str,
    papers: list[Paper],
    filter_criteria: dict | None = None,
) -> list[Paper]:
    """Rank papers by relevance to user's need."""
    if not papers:
        return []

    # Apply filters first
    filtered = papers
    if filter_criteria:
        date_from = filter_criteria.get("date_from")
        date_to = filter_criteria.get("date_to")
        exclude_kw = filter_criteria.get("exclude_keywords", [])
        include_kw = filter_criteria.get("include_keywords", [])

        if date_from:
            filtered = [p for p in filtered if p.published >= date_from]
        if date_to:
            filtered = [p for p in filtered if p.published <= date_to]
        if exclude_kw:
            filtered = [
                p for p in filtered
                if not any(
                    kw.lower() in p.title.lower() + p.abstract.lower()
                    for kw in exclude_kw
                )
            ]
        if include_kw:
            # Boost papers with include keywords but don't exclude others
            pass  # Handled by LLM ranking

    if not filtered:
        return []

    # Build papers text for LLM
    papers_text = "\n\n".join(
        f"[{i}] Title: {p.title}\nAbstract: {p.abstract[:500]}\nDate: {p.published}\nCategories: {', '.join(p.categories)}"
        for i, p in enumerate(filtered)
    )

    messages = [
        {"role": "system", "content": RANK_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"用户需求：{user_need}\n\n候选论文：\n{papers_text}",
        },
    ]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    try:
        content = response.choices[0].message.content
        # Handle both {"papers": [...]} and direct [...] formats
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            rankings = parsed.get("papers", parsed.get("results", []))
        else:
            rankings = parsed

        # Apply scores to papers
        score_map = {r["index"]: r for r in rankings}
        for i, paper in enumerate(filtered):
            if i in score_map:
                paper.relevance_score = score_map[i]["relevance_score"]
                paper.relevance_reason = score_map[i]["relevance_reason"]
            else:
                paper.relevance_score = 0
                paper.relevance_reason = ""

        # Sort by score descending
        filtered.sort(key=lambda p: p.relevance_score or 0, reverse=True)
        return filtered[:15]  # Return top 15

    except (json.JSONDecodeError, KeyError, TypeError):
        # If LLM output parsing fails, return unranked
        for p in filtered:
            p.relevance_score = None
            p.relevance_reason = None
        return filtered[:15]


async def generate_detail(paper: Paper, user_need: str) -> str:
    """Generate a detailed explanation of a paper."""
    messages = [
        {"role": "system", "content": DETAIL_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"用户研究兴趣：{user_need}\n\n论文标题：{paper.title}\n作者：{', '.join(paper.authors)}\n摘要：{paper.abstract}",
        },
    ]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content


async def generate_reply(message: str, history: list[ChatMessage]) -> str:
    """Generate a general conversational reply."""
    messages = [
        {
            "role": "system",
            "content": "你是一个友好的学术论文搜索助手。用中文简洁回复用户的问题。如果用户想搜索论文，引导他们描述研究兴趣。",
        },
    ]
    for msg in history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content
