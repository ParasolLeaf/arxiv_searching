# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
# Activate conda environment (required before running backend commands)
conda activate paperreading

# Start backend (from backend/)
uvicorn main:app --reload --port 8000

# Run with the env's Python directly (no conda activate needed)
D:/Anaconda/envs/paperreading/python.exe -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
# Install dependencies (from frontend/)
npm install --cache "e:/sigma/paperreading/.npm-cache"

# Start dev server (from frontend/, proxies /api to localhost:8000)
npm run dev

# Build for production
npm run build
```

## Architecture

This is a two-process application: a FastAPI backend and a Vite dev server. The frontend proxies all `/api/*` requests to the backend at `http://localhost:8000`.

### Request Flow

```
User message (ChatPanel)
  → POST /api/chat  (routers/chat.py)
    → llm_service.parse_intent()       # OpenAI: classify intent as new_search / refine / detail / general
    → arxiv_service.search_arxiv()     # arxiv lib: fetch up to 25 candidate papers
    → llm_service.rank_papers()        # OpenAI: score each paper 0–10 + one-line reason
  → ChatResponse { reply, papers[] }
  → App.tsx updates messages + papers state
```

The four intents in `routers/chat.py`:
- **new_search**: fresh arXiv query, full rank cycle
- **refine**: optionally re-queries arXiv then re-ranks `current_papers` with new filters
- **detail**: calls `llm_service.generate_detail()` for a specific paper index; papers list unchanged
- **general**: plain conversational reply, papers list unchanged

### Key Files

- `backend/services/llm_service.py` — all OpenAI calls; three system prompts (`INTENT_SYSTEM_PROMPT`, `RANK_SYSTEM_PROMPT`, `DETAIL_SYSTEM_PROMPT`); uses `response_format={"type": "json_object"}` for structured outputs
- `backend/routers/chat.py` — orchestrates the intent → search → rank pipeline
- `backend/models/schemas.py` — shared Pydantic models (`Paper`, `ChatRequest`, `ChatResponse`)
- `frontend/src/App.tsx` — owns all state (`messages`, `papers`, `selectedPaper`, `loading`); passes callbacks down to `ChatPanel` and `PaperList`
- `frontend/src/services/api.ts` — thin axios wrapper for all backend calls

### Environment

Backend config lives in `backend/.env`:
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` — used directly in `llm_service.py` via `python-dotenv`

Downloaded PDFs are saved to `backend/downloads/` as `{arxiv_id}_{title}.pdf`.
