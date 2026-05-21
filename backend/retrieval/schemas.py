from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class RetrievalFilters(BaseModel):
    company: Optional[str] = None
    industry: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    document_type: Optional[str] = None

    def is_empty(self) -> bool:
        return not any(
            [
                self.company,
                self.industry,
                self.year,
                self.source,
                self.document_type,
            ]
        )

    def applied(self) -> Dict[str, str]:
        return {
            k: v
            for k, v in {
                "company": self.company,
                "industry": self.industry,
                "year": self.year,
                "source": self.source,
                "document_type": self.document_type,
            }.items()
            if v
        }


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)
    filters: RetrievalFilters = Field(default_factory=RetrievalFilters)


class FilteredSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)
    company: Optional[str] = None
    industry: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    document_type: Optional[str] = None

    @model_validator(mode="after")
    def require_filter(self) -> "FilteredSearchRequest":
        if not any([self.company, self.industry, self.year, self.source, self.document_type]):
            raise ValueError(
                "At least one filter is required: company, industry, year, source, or document_type"
            )
        return self

    def to_filters(self) -> RetrievalFilters:
        return RetrievalFilters(
            company=self.company,
            industry=self.industry,
            year=self.year,
            source=self.source,
            document_type=self.document_type,
        )


class ChunkScores(BaseModel):
    semantic: float
    metadata_alignment: float
    source_trust: float
    recency: float
    final_score: float
    distance: float


class RankedChunk(BaseModel):
    rank: int
    chunk_id: str
    text: str
    metadata: Dict[str, str]
    scores: ChunkScores


class ConfidenceScores(BaseModel):
    value: float
    band: str
    status: str
    reasoning: str
    warnings: List[str] = Field(default_factory=list)
    chunk_count: int = 0
    trusted_chunk_count: int = 0


class RetrievalResponse(BaseModel):
    query: str
    chunks: List[RankedChunk]
    confidence: ConfidenceScores
    filters_applied: Dict[str, str] = Field(default_factory=dict)
    latency_ms: float = 0.0
