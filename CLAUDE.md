# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
# Run backend (from backend/ directory)
D:/Anaconda/envs/paperreading/python.exe -m uvicorn main:app --reload --port 8000

# Install dependencies
D:/Anaconda/envs/paperreading/python.exe -m pip install -r requirements.txt

# API docs available at http://localhost:8000/docs
```

### Frontend
```bash
# Install dependencies (npm cache workaround for Windows EPERM issue)
cd frontend && npm install --cache "e:/sigma/paperreading/.npm-cache"

# Dev server (http://localhost:5173)
cd frontend && npm run dev -- --cache "e:/sigma/paperreading/.npm-cache"

# Build
cd frontend && npm run build
```

## Architecture

### Request Flow

```
User message (ChatPanel)
  → POST /api/chat  (routers/chat.py)
      → llm_service.parse_intent()   — classifies into 4 intents
      ↓
      new_search: arxiv_service.search_arxiv() → llm_service.rank_papers() → new paper list
      refine:     optionally re-search + merge dedup → llm_service.rank_papers()
      detail:     llm_service.generate_detail() for paper[index-1] → text reply, papers unchanged
      general:    llm_service.generate_reply() → text reply, papers unchanged
  → ChatResponse { reply, papers[], search_query }
      → App.tsx updates messages + papers state
```

### Key Design Points

- **Four intents** (`new_search`, `refine`, `detail`, `general`) are classified by `llm_service.parse_intent()` using `response_format={"type": "json_object"}`. All LLM calls are async via `AsyncOpenAI`.
- **State lives in App.tsx**: `messages`, `papers`, `loading`, `selectedPaper`. No external state manager.
- **Vite proxy**: `/api/*` requests from the frontend are proxied to `http://localhost:8000` (see `vite.config.ts`), so `api.ts` uses `baseURL: '/api'` with no hardcoded port.
- **PDF downloads** go to `backend/downloads/` as `{arxiv_id}_{sanitized_title}.pdf`. Files are skipped if they already exist.
- **Ranking fallback**: If `rank_papers()` fails to parse LLM JSON, it returns unranked papers rather than throwing.

### Key Files

| File | Role |
|------|------|
| `backend/services/llm_service.py` | All OpenAI calls; contains 3 system prompts and 4 async functions |
| `backend/routers/chat.py` | Orchestrates intent → search → rank pipeline |
| `backend/models/schemas.py` | Pydantic models: `Paper`, `ChatRequest`, `ChatResponse` |
| `frontend/src/App.tsx` | Global state owner; wires ChatPanel ↔ PaperList ↔ PaperDetail |
| `frontend/src/services/api.ts` | Axios wrapper for `/api/chat` and `/api/papers/download` |

### Environment

- Conda env: `paperreading` at `D:/Anaconda/envs/paperreading/`
- Config in `backend/.env`: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`
- Model currently set to `gpt-5-mini` via `https://api.uniapi.io/v1` (third-party OpenAI-compatible proxy)
