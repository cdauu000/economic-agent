from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from ..trend_engine import SIGNAL_SCORES
from .citations import format_citation
from .intent import QueryIntent, classify_intent

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_SIGNAL_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("financial", "revenue_up", re.compile(r"\b(revenue|sales).*(up|increase|grow|rose)\b", re.I)),
    ("financial", "profit_down", re.compile(r"\b(profit|earnings).*(down|decline|fall|drop)\b", re.I)),
    ("financial", "cost_up", re.compile(r"\b(cost|expense).*(up|increase|rise)\b", re.I)),
    ("sentiment", "positive_news", re.compile(r"\b(positive|bullish|optimistic|upgrade)\b", re.I)),
    ("sentiment", "negative_news", re.compile(r"\b(negative|bearish|pessimistic|downgrade)\b", re.I)),
    ("macro", "interest_rate_down", re.compile(r"\b(rate cut|lower rates|easing)\b", re.I)),
    ("macro", "policy_support", re.compile(r"\b(stimulus|policy support|fiscal support)\b", re.I)),
]


@dataclass(frozen=True)
class FactStatement:
    text: str
    citation_index: int
    chunk_id: str
    citation: str


@dataclass
class ReasoningLayers:
    intent: QueryIntent
    facts: List[FactStatement] = field(default_factory=list)
    signals: Dict[str, List[str]] = field(default_factory=lambda: {
        "financial": [],
        "sentiment": [],
        "macro": [],
    })
    interpretation: str = ""
    assumptions: List[str] = field(default_factory=list)


def _extract_sentences(text: str, limit: int = 2) -> List[str]:
    parts = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if len(s.strip()) > 40]
    return parts[:limit]


def build_reasoning_layers(
    question: str,
    contexts: List[Dict[str, str]],
) -> ReasoningLayers:
    intent = classify_intent(question)
    layers = ReasoningLayers(intent=intent)
    seen_facts: set[str] = set()

    for idx, ctx in enumerate(contexts, start=1):
        text = str(ctx.get("text", "")).strip()
        if not text:
            continue
        chunk_id = str(ctx.get("chunk_id", f"chunk-{idx}"))
        for sentence in _extract_sentences(text):
            key = sentence.lower()[:200]
            if key in seen_facts:
                continue
            seen_facts.add(key)
            layers.facts.append(
                FactStatement(
                    text=sentence[:400],
                    citation_index=idx,
                    chunk_id=chunk_id,
                    citation=format_citation(ctx, chunk_id),
                )
            )
            for bucket, signal_name, pattern in _SIGNAL_PATTERNS:
                if pattern.search(sentence) and signal_name in SIGNAL_SCORES:
                    if signal_name not in layers.signals[bucket]:
                        layers.signals[bucket].append(signal_name)

    if not layers.facts and contexts:
        ctx = contexts[0]
        layers.assumptions.append("Evidence chunks lack extractable factual sentences.")
    elif len(contexts) < 2 and intent.requires_strategic_depth:
        layers.assumptions.append("Limited evidence depth for strategic intent.")

    return layers
