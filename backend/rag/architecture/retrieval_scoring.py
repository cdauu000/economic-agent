from __future__ import annotations

import re
from enum import Enum


class RetrievalMode(str, Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    METADATA = "metadata"


def semantic_score(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


def keyword_score(query: str, text: str) -> float:
    terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
    if not terms:
        return 0.0
    lower = text.lower()
    hits = sum(1 for term in terms if term in lower)
    return hits / len(terms)


def blend_scores(
    *,
    semantic: float,
    keyword: float,
    metadata: float,
    mode: RetrievalMode,
) -> float:
    if mode == RetrievalMode.SEMANTIC:
        return semantic
    if mode == RetrievalMode.METADATA:
        return (0.45 * semantic) + (0.55 * metadata)
    return (0.55 * semantic) + (0.30 * keyword) + (0.15 * metadata)
