import logging
import xml.etree.ElementTree as ET

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ESPELL_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/espell.fcgi"


async def correct_query(query: str) -> str:
    """Use NCBI ESpell API to correct misspelled medical/scientific terms.

    Returns the corrected query string, or the original query if no
    correction is available or the API call fails.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params: dict[str, str] = {
                "db": "pubmed",
                "term": query,
            }
            if settings.ncbi_api_key:
                params["api_key"] = settings.ncbi_api_key

            resp = await client.get(ESPELL_URL, params=params)
            resp.raise_for_status()

            root = ET.fromstring(resp.text)
            corrected_elem = root.find("CorrectedQuery")

            if corrected_elem is not None and corrected_elem.text:
                corrected = corrected_elem.text.strip()
                if corrected and corrected.lower() != query.lower():
                    logger.info(
                        "Spell correction: '%s' -> '%s'", query, corrected
                    )
                    return corrected

    except Exception:
        logger.exception("ESpell spell-check failed for query: %s", query)

    return query
