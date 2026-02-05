import logging
import xml.etree.ElementTree as ET

import httpx

from app.config import settings
from app.models.schemas import Study

logger = logging.getLogger(__name__)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


async def search_pubmed(query: str, max_results: int = 10) -> list[Study]:
    """Search PubMed/NCBI via E-utilities and return unified Study objects."""
    studies: list[Study] = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: ESearch to get PMIDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance",
            }
            if settings.ncbi_api_key:
                search_params["api_key"] = settings.ncbi_api_key

            search_resp = await client.get(ESEARCH_URL, params=search_params)
            search_resp.raise_for_status()
            search_data = search_resp.json()

            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return studies

            # Step 2: EFetch to get article details in XML
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml",
                "rettype": "abstract",
            }
            if settings.ncbi_api_key:
                fetch_params["api_key"] = settings.ncbi_api_key

            fetch_resp = await client.get(EFETCH_URL, params=fetch_params)
            fetch_resp.raise_for_status()

            root = ET.fromstring(fetch_resp.text)
            for article_elem in root.findall(".//PubmedArticle"):
                studies.append(_parse_pubmed_article(article_elem))

    except Exception:
        logger.exception("PubMed search failed for query: %s", query)

    return studies


def _parse_pubmed_article(article_elem: ET.Element) -> Study:
    """Parse a single PubmedArticle XML element into a Study."""
    medline = article_elem.find(".//MedlineCitation")
    article = medline.find(".//Article") if medline is not None else None

    # Title
    title_elem = article.find(".//ArticleTitle") if article is not None else None
    title = _get_text(title_elem)

    # Abstract
    abstract_parts: list[str] = []
    if article is not None:
        for abs_text in article.findall(".//Abstract/AbstractText"):
            label = abs_text.get("Label", "")
            text = _get_text(abs_text)
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
    abstract = " ".join(abstract_parts)

    # Authors
    authors: list[str] = []
    if article is not None:
        for author in article.findall(".//AuthorList/Author"):
            last = _get_text(author.find("LastName"))
            fore = _get_text(author.find("ForeName"))
            if last:
                authors.append(f"{fore} {last}".strip())

    # Journal
    journal_elem = article.find(".//Journal/Title") if article is not None else None
    journal = _get_text(journal_elem)

    # Publication date
    pub_date_elem = article.find(".//Journal/JournalIssue/PubDate") if article is not None else None
    pub_date = _parse_pub_date(pub_date_elem)

    # PMID
    pmid_elem = medline.find(".//PMID") if medline is not None else None
    pmid = _get_text(pmid_elem)
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

    # DOI
    doi = ""
    if article is not None:
        for eid in article.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi":
                doi = _get_text(eid)
                break

    return Study(
        title=title,
        authors=authors,
        abstract=abstract,
        source="PubMed",
        url=url,
        publication_date=pub_date,
        journal=journal,
        doi=doi,
    )


def _get_text(elem: ET.Element | None) -> str:
    """Safely extract text from an XML element, including mixed content."""
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def _parse_pub_date(elem: ET.Element | None) -> str:
    """Parse a PubDate XML element into a string."""
    if elem is None:
        return ""
    year = _get_text(elem.find("Year"))
    month = _get_text(elem.find("Month"))
    day = _get_text(elem.find("Day"))
    parts = [p for p in [year, month, day] if p]
    return " ".join(parts)
