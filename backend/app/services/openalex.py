import logging

import httpx

from app.config import settings
from app.models.schemas import Study

logger = logging.getLogger(__name__)

OPENALEX_API_URL = "https://api.openalex.org/works"


async def search_openalex(query: str, max_results: int = 10) -> list[Study]:
    """Search OpenAlex works API and return unified Study objects."""
    studies: list[Study] = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params: dict[str, str | int] = {
                "search": query,
                "per_page": max_results,
                "sort": "relevance_score:desc",
            }
            # OpenAlex uses api_key param for polite pool access
            if settings.openalex_api_key:
                params["api_key"] = settings.openalex_api_key
            else:
                params["mailto"] = "openevidence@example.com"
            resp = await client.get(OPENALEX_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            for work in data.get("results", []):
                studies.append(_parse_openalex_work(work))

    except Exception:
        logger.exception("OpenAlex search failed for query: %s", query)

    return studies


def _parse_openalex_work(work: dict) -> Study:
    """Parse a single OpenAlex work into a Study."""
    title = work.get("title", "") or ""

    # Abstract — OpenAlex returns an inverted index; reconstruct it
    abstract = _reconstruct_abstract(work.get("abstract_inverted_index"))

    # Authors
    authors: list[str] = []
    for authorship in work.get("authorships", []):
        author_info = authorship.get("author", {})
        name = author_info.get("display_name", "")
        if name:
            authors.append(name)

    # Journal / source
    primary_location = work.get("primary_location") or {}
    source_info = primary_location.get("source") or {}
    journal = source_info.get("display_name", "")

    # Date
    pub_date = work.get("publication_date", "")

    # DOI
    doi_url = work.get("doi", "") or ""
    doi = doi_url.replace("https://doi.org/", "") if doi_url else ""

    # URL
    url = doi_url or work.get("id", "")

    return Study(
        title=title,
        authors=authors,
        abstract=abstract,
        source="OpenAlex",
        url=url,
        publication_date=pub_date,
        journal=journal,
        doi=doi,
    )


def _reconstruct_abstract(inverted_index: dict | None) -> str:
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in word_positions)
