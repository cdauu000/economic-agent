from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OrchestrationResult:
    answer: str
    summary: str
    intent: str
    intent_tags: List[str]
    evidence_snapshot: List[str]
    signals: Dict[str, List[str]]
    trend: str
    risks: List[str]
    opportunities: List[str]
    confidence: Dict[str, Any]
    retrieval_quality: Dict[str, Any]
    assumptions: List[str]
    citations: List[str]
    reasoning_layers: Dict[str, Any]
    evaluation: Dict[str, Any]
    retrieval: Optional[Dict[str, Any]] = None
