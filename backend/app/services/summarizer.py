import logging

from openai import AsyncOpenAI

from app.config import settings
from app.models.schemas import Study

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a medical evidence summarizer. Given a list of study titles and abstracts "
    "from a search query, provide a strictly 2-3 sentence evidence-based summary. "
    "Focus on the consensus findings, note any conflicting evidence, and mention the "
    "strength of the evidence (e.g., number of studies, study types). "
    "Do not provide medical advice. Be objective and concise."
)


async def summarize_studies(query: str, studies: list[Study]) -> str:
    """Generate a 2-3 sentence AI summary of the retrieved studies."""
    if not studies:
        return ""

    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured — skipping summarization")
        return ""

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Build context from top studies (limit to avoid token overflow)
        study_texts: list[str] = []
        for i, study in enumerate(studies[:15], 1):
            snippet = study.abstract[:500] if study.abstract else "No abstract available."
            study_texts.append(
                f"{i}. [{study.source}] {study.title}\n   {snippet}"
            )
        context = "\n\n".join(study_texts)

        user_message = (
            f"Search query: \"{query}\"\n\n"
            f"Studies found ({len(studies)} total):\n\n{context}\n\n"
            "Provide a 2-3 sentence evidence-based summary."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        logger.exception("OpenAI summarization failed for query: %s", query)
        return ""
