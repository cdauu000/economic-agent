from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from ..trend_engine import SIGNAL_SCORES
from .reasoning import ReasoningLayers

_NUMERIC_CLAIM = re.compile(r"\b\d+[\d.,]*\s*%|\b\d{1,3}(?:,\d{3})+\b|\$\d")


@dataclass
class GroundingEvaluation:
    passed: bool
    grounding_coverage: float
    hallucination_risk: str
    evidence_consistency: str
    warnings: List[str] = field(default_factory=list)
    reasoning: str = ""


def evaluate_grounding(
    answer: str,
    layers: ReasoningLayers,
    *,
    chunk_count: int,
    sufficiency_threshold: int,
) -> GroundingEvaluation:
    warnings: List[str] = []
    if chunk_count < sufficiency_threshold:
        warnings.append(f"Evidence count {chunk_count} below threshold {sufficiency_threshold}.")

    fact_count = len(layers.facts)
    coverage = min(1.0, fact_count / max(sufficiency_threshold, 1)) if chunk_count else 0.0

    numeric_in_answer = bool(_NUMERIC_CLAIM.search(answer or ""))
    cited_indices = {f.citation_index for f in layers.facts}
    has_citations_in_answer = any(f"[{i}]" in (answer or "") for i in cited_indices)

    if numeric_in_answer and not has_citations_in_answer:
        hallucination_risk = "HIGH"
        warnings.append("Numeric claims without chunk citations.")
    elif not layers.facts:
        hallucination_risk = "HIGH"
    elif coverage < 0.5:
        hallucination_risk = "MEDIUM"
    else:
        hallucination_risk = "LOW"

    buckets = [layers.signals.get("financial", []), layers.signals.get("sentiment", []), layers.signals.get("macro", [])]
    non_empty = [b for b in buckets if b]
    if len(non_empty) >= 2:
        pos = sum(1 for b in non_empty if any(SIGNAL_SCORES.get(s, 0) > 0 for s in b))
        neg = sum(1 for b in non_empty if any(SIGNAL_SCORES.get(s, 0) < 0 for s in b))
        consistency = "CONFLICTING" if pos and neg else "ALIGNED"
    else:
        consistency = "SPARSE"

    if consistency == "CONFLICTING":
        warnings.append("Conflicting signal directions across evidence buckets.")

    passed = (
        answer.strip().lower() != "insufficient data"
        and hallucination_risk != "HIGH"
        and chunk_count >= sufficiency_threshold
        and coverage >= 0.5
    )

    return GroundingEvaluation(
        passed=passed,
        grounding_coverage=round(coverage, 3),
        hallucination_risk=hallucination_risk,
        evidence_consistency=consistency,
        warnings=warnings,
        reasoning="Grounding evaluation over retrieved evidence and layered reasoning.",
    )
