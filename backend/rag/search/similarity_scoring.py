from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

from ...services.retrieval_governance import source_trust
from ..architecture.metadata_store import MetadataFilter
from ..architecture.retrieval_scoring import semantic_score


@dataclass(frozen=True)
class SimilarityFactors:
    semantic: float
    metadata_alignment: float
    source_trust: float
    recency: float
    final_score: float


def _parse_year(value: str) -> int | None:
    value = (value or "").strip()
    if value.isdigit() and len(value) == 4:
        return int(value)
    return None


def recency_score(metadata: Dict[str, str]) -> float:
    year = _parse_year(str(metadata.get("year", "")))
    if year is None:
        return 0.5
    age = datetime.now(timezone.utc).year - year
    if age <= 0:
        return 1.0
    if age == 1:
        return 0.9
    if age <= 3:
        return 0.75
    if age <= 5:
        return 0.55
    return 0.35


def metadata_alignment_score(metadata: Dict[str, str], filters: MetadataFilter) -> float:
    if not filters.is_restrictive():
        return 0.5
    checks = [
        (filters.company, "company"),
        (filters.industry, "industry"),
        (filters.year, "year"),
        (filters.source, "source"),
        (filters.document_type, "document_type"),
    ]
    active = [(expected, key) for expected, key in checks if expected]
    if not active:
        return 0.5
    hits = sum(1 for expected, key in active if metadata.get(key) == expected)
    return hits / len(active)


def trust_score(metadata: Dict[str, str]) -> float:
    source = str(metadata.get("source", metadata.get("source_type", "unknown")))
    return source_trust(source)


def compute_similarity_factors(
    *,
    distance: float,
    metadata: Dict[str, str],
    filters: MetadataFilter,
) -> SimilarityFactors:
    sem = semantic_score(distance)
    meta = metadata_alignment_score(metadata, filters)
    trust = trust_score(metadata)
    rec = recency_score(metadata)
    final = round((0.50 * sem) + (0.20 * meta) + (0.20 * trust) + (0.10 * rec), 4)
    return SimilarityFactors(
        semantic=round(sem, 4),
        metadata_alignment=round(meta, 4),
        source_trust=round(trust, 4),
        recency=round(rec, 4),
        final_score=final,
    )
