from __future__ import annotations

from typing import Dict


def format_citation(metadata: Dict[str, str], chunk_id: str = "") -> str:
    source = metadata.get("source_type") or metadata.get("source", "unknown")
    company = metadata.get("company", "unknown")
    period = metadata.get("year") or metadata.get("reporting_period", "unknown")
    ref = chunk_id or metadata.get("chunk_id", metadata.get("doc_id", "unknown"))
    return f"[{source} | {company} | {period} | {ref}]"
