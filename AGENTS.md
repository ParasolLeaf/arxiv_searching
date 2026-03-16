# AGENTS.md

Guidance for AI coding agents working in this repository.
This is a full-stack arXiv paper search/recommendation app: React/Vite/TypeScript frontend + Python/FastAPI backend.

## Build & Run Commands

### Backend (from `backend/` directory)

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server (port 8000, auto-reload)
python -m uvicorn main:app --reload --port 8000

# API docs (Swagger UI)
# http://localhost:8000/docs
```

### Frontend (from `frontend/` directory)

```bash
# Install dependencies
npm install

# Dev server (http://localhost:5173, proxies /api/* to backend)
npm run dev

# Production build (runs tsc then vite build)
npm run build

# Type-check only (no emit)
npx tsc -b
```

### Tests

There are no tests, test frameworks, or test configurations in this repository.
No pytest, vitest, or jest is set up. If adding tests:
- Backend: use `pytest` with `httpx` for async FastAPI testing.
- Frontend: use `vitest` (already Vite-based) with `@testing-library/react`.

### Linting / Formatting

No linters or formatters are configured (no eslint, prettier, ruff, mypy).
Follow the conventions documented below to stay consistent with existing code.

## Architecture Overview

```
User message (ChatPanel)
  -> POST /api/chat  (routers/chat.py)
      -> llm_service.parse_intent()   -- classifies into 4 intents
      |
      new_search: arxiv_service.search_arxiv() -> llm_service.rank_papers()
      refine:     optionally re-search + merge dedup -> llm_service.rank_papers()
      detail:     llm_service.generate_detail() for paper[index-1]
      general:    llm_service.generate_reply()
  -> ChatResponse { reply, papers[], search_query }
      -> App.tsx updates messages + papers state
```

Key files:
- `backend/services/llm_service.py` -- All OpenAI calls, system prompts, 4 async functions
- `backend/routers/chat.py` -- Orchestrates intent -> search -> rank pipeline
- `backend/models/schemas.py` -- Pydantic models (Paper, ChatRequest, ChatResponse, etc.)
- `frontend/src/App.tsx` -- Global state owner (messages, papers, loading, selectedPaper)
- `frontend/src/services/api.ts` -- Axios wrapper for /api/chat and /api/papers/download
- `frontend/src/types/index.ts` -- TypeScript interfaces mirroring backend schemas

## Environment

- Config in `backend/.env`: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`
- `.env` is gitignored; copy `.env.example` to `.env` and fill in values
- Vite proxy: `/api/*` requests forwarded to `http://localhost:8000` (see `vite.config.ts`)

## Code Style -- Python (Backend)

### Imports
- Three groups: stdlib, third-party, local. **No blank lines** between groups.
- `import X` for stdlib modules (`import os`, `import json`, `import re`).
- `from X import Y` for third-party and local imports.
- Keep multi-name imports on one line: `from models.schemas import ChatRequest, ChatResponse, ChatMessage`.

### Naming
- Functions/variables: `snake_case` (`search_arxiv`, `filter_criteria`)
- Classes (Pydantic models): `PascalCase` (`ChatRequest`, `DownloadResponse`)
- Module-level constants: `UPPER_SNAKE_CASE` (`MODEL`, `DOWNLOAD_DIR`, `INTENT_SYSTEM_PROMPT`)
- Singletons: lowercase (`client`, `router`, `app`)

### Type Annotations
- **Required on every function** (parameters and return type).
- Use Python 3.10+ built-in generics: `list[Paper]`, not `List[Paper]`.
- Use union pipe syntax: `float | None = None`, not `Optional[float]`.
- Do not import from `typing`.

### Async/Await
- All I/O functions must be `async def`.
- Pure computation/utility functions remain `def`.
- `AsyncOpenAI` client is a module-level singleton in `llm_service.py`.
- Use simple sequential `await` calls (no `asyncio.gather` patterns currently).

### Docstrings
- Single-line, imperative sentence, triple-double-quotes on every function.
- Example: `"""Download a paper PDF from arXiv."""`
- No multi-line docstrings, no `:param:` or Google/NumPy sections.

### Error Handling
- Catch specific exceptions, never bare `except`.
- Prefer graceful degradation over raising (e.g., ranking fallback returns unranked papers).
- No logging module is used; do not add `print()` for debugging.
- Pydantic handles request validation automatically.

### Pydantic Models
- All models in `models/schemas.py`, inheriting `BaseModel` directly.
- Simple field declarations: `field_name: type` or `field_name: type = default`.
- No `Field()`, no validators, no `model_config`.
- Optional fields: `X | None = None`. List fields default to `[]`.

### FastAPI Patterns
- Routers define `router = APIRouter(tags=["..."])` at module level.
- Prefix `/api` is applied at `include_router()` time in `main.py`, not on routers.
- Use `response_model=` on route decorators.
- Services are imported as modules or functions directly (no dependency injection).

### Strings & Comments
- f-strings exclusively for interpolation.
- User-facing messages in Chinese; code comments/docstrings in English.
- Trailing commas in multi-line constructs.

## Code Style -- TypeScript/React (Frontend)

### Imports
- Three groups (no blank lines between): React/libraries, type-only imports, local modules.
- Use `import type { X }` for type-only imports.
- Single quotes for all import paths.

### Components
- Named function declarations with `export default`: `export default function ChatPanel({ ... }: Props) { ... }`
- No arrow-function components, no `React.FC`, no class components.
- Destructure props in the function signature.
- Define a file-scoped `interface Props` (not exported, always named `Props`).

### TypeScript
- Use `interface` (not `type` aliases) for data models and props.
- Generic `useState`: `useState<Paper[]>([])`, `useState<Paper | null>(null)`.
- Infer primitive state: `useState(false)`, `useState('')`.
- `catch (err: any)` for error handling.
- Data interfaces use snake_case field names to match the Python API (e.g., `arxiv_id`, `pdf_url`).

### Formatting (no tooling enforced -- follow manually)
- **No semicolons** at end of statements.
- **Single quotes** for strings and imports.
- **2-space indentation**.
- **Trailing commas** in multi-line objects/params.

### State Management
- All global state lives in `App.tsx` via `useState`.
- Props drilling only (no context, no external state libraries).
- Immutable updates: `setMessages([...messages, newMsg])`.

### Error Handling
- `try/catch/finally` in async event handlers.
- `finally` always resets loading state.
- Errors surfaced in UI (as chat messages or status text), never silently swallowed.
- API layer (`api.ts`) does not catch errors -- they propagate to components.

### CSS
- Single global stylesheet: `src/styles/index.css`.
- CSS custom properties on `:root` for theming.
- BEM-like kebab-case class names: `.paper-card`, `.chat-panel`, `.modal-overlay`.
- Template literals for conditional classes: `` className={`message ${isUser ? 'user' : 'assistant'}`} ``.
- No CSS modules, no CSS-in-JS, no Tailwind.

### API Calls
- Centralized Axios instance in `services/api.ts` with `baseURL: '/api'`.
- Each endpoint is a named export: `sendChat()`, `downloadPaper()`, `getDownloads()`.
- Explicit return types: `Promise<ChatResponse>`.
- Calls made directly in component event handlers (no custom hooks).
