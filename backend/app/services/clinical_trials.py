import logging

import httpx

from app.models.schemas import Study

logger = logging.getLogger(__name__)

CTGOV_API_URL = "https://clinicaltrials.gov/api/v2/studies"

# ClinicalTrials.gov requires browser-like headers to avoid WAF blocks
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://clinicaltrials.gov/",
}


async def search_clinical_trials(query: str, max_results: int = 10) -> list[Study]:
    """Search ClinicalTrials.gov v2 API and return unified Study objects."""
    studies: list[Study] = []
    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            headers=_HEADERS,
            follow_redirects=True,
        ) as client:
            params = {
                "query.term": query,
                "pageSize": max_results,
            }
            resp = await client.get(CTGOV_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            for study_data in data.get("studies", []):
                studies.append(_parse_trial(study_data))

    except Exception:
        logger.exception("ClinicalTrials.gov search failed for query: %s", query)

    return studies


def _parse_trial(study_data: dict) -> Study:
    """Parse a single ClinicalTrials.gov study JSON into a Study."""
    protocol = study_data.get("protocolSection", {})
    id_module = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    desc_module = protocol.get("descriptionModule", {})
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    contacts_module = protocol.get("contactsLocationsModule", {})

    nct_id = id_module.get("nctId", "")
    title = id_module.get("briefTitle", "")

    # Abstract from brief summary
    abstract = desc_module.get("briefSummary", "")

    # Dates
    start_date_struct = status_module.get("startDateStruct", {})
    pub_date = start_date_struct.get("date", "")

    # Lead sponsor as author
    authors: list[str] = []
    lead_sponsor = sponsor_module.get("leadSponsor", {})
    if lead_sponsor.get("name"):
        authors.append(lead_sponsor["name"])

    # PI from overall officials
    for official in contacts_module.get("overallOfficials", []):
        name = official.get("name", "")
        if name:
            authors.append(name)

    url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else ""

    return Study(
        title=title,
        authors=authors,
        abstract=abstract,
        source="ClinicalTrials",
        url=url,
        publication_date=pub_date,
        journal="ClinicalTrials.gov",
        doi="",
    )
