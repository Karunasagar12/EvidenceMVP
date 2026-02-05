import logging

import httpx

from app.models.schemas import Study

logger = logging.getLogger(__name__)

EPMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


async def search_europe_pmc(query: str, max_results: int = 10) -> list[Study]:
    """Search Europe PMC REST API and return unified Study objects."""
    studies: list[Study] = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "query": query,
                "format": "json",
                "pageSize": max_results,
                "resultType": "core",
            }
            resp = await client.get(EPMC_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            result_list = data.get("resultList", {}).get("result", [])
            for item in result_list:
                studies.append(_parse_epmc_result(item))

    except Exception:
        logger.exception("Europe PMC search failed for query: %s", query)

    return studies


def _parse_epmc_result(item: dict) -> Study:
    """Parse a single Europe PMC result into a Study."""
    title = item.get("title", "")
    abstract = item.get("abstractText", "")

    # Authors
    authors: list[str] = []
    author_list = item.get("authorList", {}).get("author", [])
    for author in author_list:
        full_name = author.get("fullName", "")
        if full_name:
            authors.append(full_name)

    # Journal — field is nested inside journalInfo.journal.title
    journal_info = item.get("journalInfo", {})
    journal_obj = journal_info.get("journal", {})
    journal = journal_obj.get("title", "") or item.get("journalTitle", "")

    # Date
    pub_date = item.get("firstPublicationDate", "")

    # DOI
    doi = item.get("doi", "")

    # URL — use pmid or pmcid
    pmid = item.get("pmid", "")
    pmcid = item.get("pmcid", "")
    if pmid:
        url = f"https://europepmc.org/article/med/{pmid}"
    elif pmcid:
        url = f"https://europepmc.org/article/pmc/{pmcid}"
    else:
        url = ""

    return Study(
        title=title,
        authors=authors,
        abstract=abstract,
        source="EuropePMC",
        url=url,
        publication_date=pub_date,
        journal=journal,
        doi=doi,
    )
