import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import router

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _check_environment() -> None:
    """Verify critical environment variables at startup."""
    warnings: list[str] = []
    if not settings.openai_api_key:
        warnings.append("OPENAI_API_KEY is not set — AI summarization will be disabled")
    if not settings.ncbi_api_key:
        warnings.append("NCBI_API_KEY is not set — PubMed rate limits may apply")
    for w in warnings:
        logger.warning(w)


app = FastAPI(
    title="Plato Evidence API",
    description="Medical evidence search across PubMed, ClinicalTrials.gov, Europe PMC, and OpenAlex",
    version="1.0.0",
)

# CORS — allow the frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include search routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    _check_environment()
    logger.info("Plato Evidence API started")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
