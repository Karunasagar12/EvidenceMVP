# Open Evidence Project Guide

## Project Overview
A medical evidence search platform querying NCBI/PubMed, ClinicalTrials.gov, Europe PMC, and OpenAlex with AI summarization.

## Tech Stack
- **Backend:** FastAPI (Python 3.10+), httpx for async requests.
- **Frontend:** Next.js 14 (App Router), Tailwind CSS, shadcn/ui, Lucide icons.
- **Structure:** Monorepo with `/backend` and `/frontend`.

## Coding Standards
- **General:** Always use absolute imports. Use async/await for all network operations.
- **Python:** - Follow PEP 8. Use Pydantic v2 for schemas.
  - Implement structured logging instead of print statements.
  - All API clients must be in `backend/app/services/` and inherit a similar interface.
- **TypeScript:** - Use Functional Components with TypeScript interfaces.
  - Strict typing: Avoid `any`. Define shared types in `frontend/lib/api.ts`.
  - Use `use client` directive only for interactive components.

## Common Tasks & Commands
### Backend
- **Install:** `pip install -r backend/requirements.txt`
- **Dev Server:** `uvicorn app.main:app --reload --port 8000`
- **Test:** `pytest backend/`

### Frontend
- **Install:** `npm install`
- **Dev Server:** `npm run dev`
- **Build:** `npm run build`

## Architecture Requirements
- **Deduplication:** The backend `routes.py` must deduplicate studies by title similarity (normalized lower-case first 50 chars).
- **Parallelism:** Use `asyncio.gather` for all external API calls to minimize latency.
- **Error Handling:** External API failures should be caught and returned as empty lists rather than crashing the main search request.
- **Summarization:** OpenAI prompt must be strictly 2-3 sentences and evidence-based.

## Verification Checklist
1. All backend models match the `SearchResponse` schema.
2. CORS is configured to allow `NEXT_PUBLIC_API_URL`.
3. Frontend components handle "No Results" and "Loading" states gracefully.
4. Environment variables are checked at startup.