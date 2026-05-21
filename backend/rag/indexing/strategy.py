from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from ..embedding.normalizer import normalize_chunk_text
from ..storage.metadata import normalize_storage_metadata, validate_storage_metadata
from .constants import INDEX_BATCH_SIZE, INDEX_VERSION, MIN_INDEX_CHARS


@dataclass(frozen=True)
class IndexEntry:
    chunk_id: str
    embedding_text: str
    display_text: str
    metadata: Dict[str, str]
    index_namespace: str


@dataclass
class IndexingBatchResult:
    indexed_count: int
    skipped_count: int
    batch_count: int
    latency_ms: float
    index_version: str = INDEX_VERSION


def build_index_namespace(metadata: Dict[str, str]) -> str:
    company = metadata.get("company", "unknown")
    year = metadata.get("year", "unknown")
    source = metadata.get("source", "unknown")
    return f"{company}:{year}:{source}"


def prepare_index_entry(record: Dict[str, str]) -> IndexEntry | None:
    display_text = str(record.get("text", "")).strip()
    if len(display_text) < MIN_INDEX_CHARS:
        return None

    metadata = normalize_storage_metadata(record)
    errors = validate_storage_metadata(metadata)
    if errors:
        return None

    embedding_text = normalize_chunk_text(display_text, metadata)
    if len(embedding_text) < MIN_INDEX_CHARS:
        return None

    chunk_id = metadata["chunk_id"]
    namespace = build_index_namespace(metadata)
    metadata["index_namespace"] = namespace
    metadata["index_version"] = INDEX_VERSION
    metadata["indexed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["index_id"] = chunk_id
    metadata["metadata_link"] = metadata.get("doc_id", chunk_id)
    metadata["text"] = display_text

    return IndexEntry(
        chunk_id=chunk_id,
        embedding_text=embedding_text,
        display_text=display_text,
        metadata=metadata,
        index_namespace=namespace,
    )


def prepare_index_entries(records: List[Dict[str, str]]) -> tuple[List[IndexEntry], int]:
    entries: List[IndexEntry] = []
    skipped = 0
    for record in records:
        entry = prepare_index_entry(record)
        if entry is None:
            skipped += 1
            continue
        entries.append(entry)
    return entries, skipped


def batch_entries(entries: List[IndexEntry], batch_size: int = INDEX_BATCH_SIZE) -> List[List[IndexEntry]]:
    if not entries:
        return []
    return [entries[i : i + batch_size] for i in range(0, len(entries), batch_size)]


def entries_to_records(entries: List[IndexEntry]) -> List[Dict[str, str]]:
    return [{**entry.metadata, "text": entry.display_text} for entry in entries]


@dataclass
class IndexingRunResult:
    indexed_count: int
    skipped_count: int
    batch_count: int
    latency_ms: float
    namespaces: List[str] = field(default_factory=list)
    index_version: str = INDEX_VERSION


def summarize_indexing(
    *,
    indexed_count: int,
    skipped_count: int,
    batch_count: int,
    started_at: float,
    namespaces: List[str],
) -> IndexingRunResult:
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    return IndexingRunResult(
        indexed_count=indexed_count,
        skipped_count=skipped_count,
        batch_count=batch_count,
        latency_ms=round(elapsed_ms, 2),
        namespaces=sorted(set(namespaces)),
        index_version=INDEX_VERSION,
    )
