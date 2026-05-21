from __future__ import annotations

import re
from dataclasses import dataclass

from .constants import (
    INTENT_ANALYSIS,
    INTENT_DOCUMENT,
    INTENT_FACTUAL,
    INTENT_MACRO,
    INTENT_METRIC,
    INTENT_RISK,
    INTENT_SENTIMENT,
    INTENT_TREND,
)


@dataclass(frozen=True)
class QueryIntent:
    primary: str
    tags: tuple[str, ...]
    requires_strategic_depth: bool


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (INTENT_METRIC, re.compile(r"\b(revenue|profit|margin|eps|ebitda|roe|roa|debt|cash flow|valuation|p/e)\b", re.I)),
    (INTENT_TREND, re.compile(r"\b(trend|outlook|forecast|direction|next (year|quarter|month))\b", re.I)),
    (INTENT_RISK, re.compile(r"\b(risk|threat|downside|headwind|volatility)\b", re.I)),
    (INTENT_SENTIMENT, re.compile(r"\b(sentiment|news|social|reputation|market mood)\b", re.I)),
    (INTENT_MACRO, re.compile(r"\b(macro|gdp|inflation|interest rate|policy|fed|central bank)\b", re.I)),
    (INTENT_ANALYSIS, re.compile(r"\b(analyze|analysis|evaluate|compare|assess|sector|industry)\b", re.I)),
    (INTENT_DOCUMENT, re.compile(r"\b(report|filing|statement|document|annual|quarterly)\b", re.I)),
]


def classify_intent(question: str) -> QueryIntent:
    q = (question or "").strip()
    tags: list[str] = []
    for name, pattern in _PATTERNS:
        if pattern.search(q):
            tags.append(name)

    if INTENT_METRIC in tags:
        primary = INTENT_METRIC
    elif INTENT_TREND in tags:
        primary = INTENT_TREND
    elif INTENT_RISK in tags:
        primary = INTENT_RISK
    elif INTENT_ANALYSIS in tags:
        primary = INTENT_ANALYSIS
    elif INTENT_DOCUMENT in tags:
        primary = INTENT_DOCUMENT
    elif INTENT_SENTIMENT in tags:
        primary = INTENT_SENTIMENT
    elif INTENT_MACRO in tags:
        primary = INTENT_MACRO
    else:
        primary = INTENT_FACTUAL

    strategic = primary in {INTENT_TREND, INTENT_RISK, INTENT_ANALYSIS, INTENT_SENTIMENT, INTENT_MACRO}
    return QueryIntent(primary=primary, tags=tuple(tags or [primary]), requires_strategic_depth=strategic)
