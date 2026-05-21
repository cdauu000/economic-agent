from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class QueryEntities:
    company: Optional[str] = None
    industry: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    document_type: Optional[str] = None
    metrics: list[str] = field(default_factory=list)


_YEAR_RE = re.compile(r"\b(20\d{2})\b")
_METRIC_RE = re.compile(
    r"\b(revenue|profit|margin|eps|ebitda|roe|roa|debt|cash flow|valuation)\b",
    re.I,
)


def extract_entities(question: str, overrides: Optional[Dict[str, Optional[str]]] = None) -> QueryEntities:
    overrides = overrides or {}
    year_match = _YEAR_RE.search(question or "")
    metrics = [m.lower() for m in _METRIC_RE.findall(question or "")]

    return QueryEntities(
        company=overrides.get("company"),
        industry=overrides.get("industry") or overrides.get("sector"),
        year=overrides.get("year") or (year_match.group(1) if year_match else None),
        source=overrides.get("source"),
        document_type=overrides.get("document_type"),
        metrics=metrics,
    )
