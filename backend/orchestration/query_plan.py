from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .constants import DEFAULT_TOP_K, STRATEGIC_TOP_K, STRATEGIC_INTENTS
from .entities import QueryEntities
from .intent import QueryIntent


@dataclass(frozen=True)
class PlanFilters:
    company: Optional[str] = None
    industry: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    document_type: Optional[str] = None

    def is_empty(self) -> bool:
        return not any(
            [self.company, self.industry, self.year, self.source, self.document_type]
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


@dataclass(frozen=True)
class QueryPlan:
    intent: QueryIntent
    filters: PlanFilters
    top_k: int
    retrieval_mode: str
    metadata_first: bool
    sufficiency_threshold: int


def build_query_plan(
    intent: QueryIntent,
    entities: QueryEntities,
    *,
    top_k: int | None = None,
    retrieval_mode: str = "hybrid",
) -> QueryPlan:
    filters = PlanFilters(
        company=entities.company,
        industry=entities.industry,
        year=entities.year,
        source=entities.source,
        document_type=entities.document_type,
    )
    metadata_first = not filters.is_empty()
    planned_top_k = top_k or (STRATEGIC_TOP_K if intent.primary in STRATEGIC_INTENTS else DEFAULT_TOP_K)
    threshold = 2 if intent.requires_strategic_depth else 1

    return QueryPlan(
        intent=intent,
        filters=filters,
        top_k=planned_top_k,
        retrieval_mode=retrieval_mode,
        metadata_first=metadata_first,
        sufficiency_threshold=threshold,
    )
