from pydantic import BaseModel, Field


class Study(BaseModel):
    """Unified study representation across all data sources."""

    title: str = Field(description="Title of the study or article")
    authors: list[str] = Field(default_factory=list, description="List of author names")
    abstract: str = Field(default="", description="Study abstract text")
    source: str = Field(description="Data source: PubMed, ClinicalTrials, EuropePMC, OpenAlex")
    url: str = Field(default="", description="Link to the original study")
    publication_date: str = Field(default="", description="Publication or posting date")
    journal: str = Field(default="", description="Journal or registry name")
    doi: str = Field(default="", description="Digital Object Identifier")


class SearchRequest(BaseModel):
    """Incoming search query from the frontend."""

    query: str = Field(min_length=1, max_length=500, description="Medical search query")
    max_results: int = Field(default=10, ge=1, le=50, description="Max results per source")


class SearchResponse(BaseModel):
    """Full response returned to the frontend."""

    query: str
    corrected_query: str = Field(default="", description="Spell-corrected query (empty if no correction)")
    total_results: int
    studies: list[Study]
    summary: str = Field(default="", description="AI-generated evidence summary")
    sources_queried: list[str] = Field(default_factory=list)
