import asyncio
import logging

from fastapi import APIRouter, Query

from app.models.schemas import SearchRequest, SearchResponse, Study
from app.services.clinical_trials import search_clinical_trials
from app.services.europe_pmc import search_europe_pmc
from app.services.openalex import search_openalex
from app.services.pubmed import search_pubmed
from app.services.spellcheck import correct_query
from app.services.summarizer import summarize_studies

logger = logging.getLogger(__name__)

router = APIRouter()

SOURCES_QUERIED = ["PubMed", "ClinicalTrials", "EuropePMC", "OpenAlex"]


def _deduplicate_studies(studies: list[Study]) -> list[Study]:
    """Remove duplicate studies by normalized title (lowercase, first 50 chars)."""
    seen: set[str] = set()
    unique: list[Study] = []
    for study in studies:
        key = study.title.strip().lower()[:50]
        if key and key not in seen:
            seen.add(key)
            unique.append(study)
    return unique


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    max_results: int = Query(default=10, ge=1, le=50, description="Max results per source"),
) -> SearchResponse:
    """Search all medical evidence sources in parallel, deduplicate, and summarize."""
    logger.info("Search request: query=%s, max_results=%d", q, max_results)

    # Step 1: Spell-correct the query via NCBI ESpell
    corrected = await correct_query(q)
    search_query = corrected if corrected else q
    corrected_query = corrected if corrected.lower() != q.lower() else ""

    if corrected_query:
        logger.info("Using corrected query: '%s' (original: '%s')", search_query, q)

    # Step 2: Query all four sources in parallel using asyncio.gather
    pubmed_results, ct_results, epmc_results, oalex_results = await asyncio.gather(
        search_pubmed(search_query, max_results),
        search_clinical_trials(search_query, max_results),
        search_europe_pmc(search_query, max_results),
        search_openalex(search_query, max_results),
        return_exceptions=True,
    )

    # Collect results, treating exceptions as empty lists
    all_studies: list[Study] = []
    for label, result in zip(
        SOURCES_QUERIED,
        [pubmed_results, ct_results, epmc_results, oalex_results],
    ):
        if isinstance(result, BaseException):
            logger.error("Source %s returned an exception: %s", label, result)
        else:
            all_studies.extend(result)

    # Deduplicate by title similarity
    unique_studies = _deduplicate_studies(all_studies)

    logger.info(
        "Search complete: %d total, %d after dedup",
        len(all_studies),
        len(unique_studies),
    )

    # Generate AI summary
    summary = await summarize_studies(search_query, unique_studies)

    return SearchResponse(
        query=q,
        corrected_query=corrected_query,
        total_results=len(unique_studies),
        studies=unique_studies,
        summary=summary,
        sources_queried=SOURCES_QUERIED,
    )


@router.post("/search", response_model=SearchResponse)
async def search_post(request: SearchRequest) -> SearchResponse:
    """POST endpoint — delegates to the GET handler."""
    return await search(q=request.query, max_results=request.max_results)
