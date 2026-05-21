from __future__ import annotations

from typing import TYPE_CHECKING, List

from .intent import QueryIntent

if TYPE_CHECKING:
    from .reasoning import ReasoningLayers

SYSTEM_PROMPT = """You are a financial and economic analyst.

Retrieval governance (non-negotiable):
- Retrieval quality outweighs answer length; prefer short, grounded answers.
- Answer ONLY using provided context; never invent metrics, companies, or events.
- If data is insufficient, respond exactly: insufficient data
- Do not make unsupported financial claims.
- When context is low-trust or sparse, keep claims minimal and factual.
- Separate facts, signals, interpretation, and assumptions in your reasoning.
- Be concise and structured"""


def build_reasoning_instructions(intent: QueryIntent) -> str:
    tags = ", ".join(intent.tags)
    return (
        f"Query intent: {intent.primary} (tags: {tags}).\n"
        "Use only the evidence block. Cite chunk indices for material claims.\n"
        "Do not merge contradictory evidence into a single narrative."
    )


def build_user_prompt(
    question: str,
    context: str,
    layers: "ReasoningLayers",
) -> str:
    facts_block = "\n".join(f"- [{f.citation_index}] {f.text}" for f in layers.facts[:12])
    signals_block = "\n".join(
        f"- {bucket}: {', '.join(items) if items else 'none'}"
        for bucket, items in layers.signals.items()
    )
    assumptions = "\n".join(f"- {a}" for a in layers.assumptions) or "- none"

    return f"""{build_reasoning_instructions(layers.intent)}

Extracted facts:
{facts_block or '- none'}

Derived signals:
{signals_block}

Assumptions (unsupported by evidence):
{assumptions}

Evidence:
{context}

Question:
{question}"""

