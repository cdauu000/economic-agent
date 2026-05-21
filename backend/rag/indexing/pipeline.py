from __future__ import annotations

import time
from typing import Dict, List, TYPE_CHECKING

from ..embedding.pipeline import EmbeddingBatchResult
from .constants import HNSW_COLLECTION_METADATA, INDEX_BATCH_SIZE
from .strategy import (
    IndexingRunResult,
    batch_entries,
    entries_to_records,
    prepare_index_entries,
    summarize_indexing,
)

if TYPE_CHECKING:
    from ..architecture.embedding_store import EmbeddingStore


class VectorIndexingPipeline:
    def __init__(self, embedding_store: "EmbeddingStore") -> None:
        self._store = embedding_store
        self._apply_hnsw_settings()

    def _apply_hnsw_settings(self) -> None:
        try:
            collection = self._store._pipeline._store._collection  # noqa: SLF001
            if collection and hasattr(collection, "modify"):
                collection.modify(metadata=HNSW_COLLECTION_METADATA)
        except Exception:
            pass

    def index_records(self, records: List[Dict[str, str]]) -> IndexingRunResult:
        started = time.perf_counter()
        entries, skipped = prepare_index_entries(records)
        if not entries:
            return summarize_indexing(
                indexed_count=0,
                skipped_count=skipped or len(records),
                batch_count=0,
                started_at=started,
                namespaces=[],
            )

        ids = [entry.chunk_id for entry in entries]
        existing = self._store.existing_ids(ids)
        if existing:
            self._store.delete_ids(list(existing))

        batches = batch_entries(entries, INDEX_BATCH_SIZE)
        indexed_total = 0
        namespaces: List[str] = []

        for batch in batches:
            batch_records = entries_to_records(batch)
            result: EmbeddingBatchResult = self._store.embed_and_store_records(batch_records)
            indexed_total += result.embedded_count
            namespaces.extend(entry.index_namespace for entry in batch)

        return summarize_indexing(
            indexed_count=indexed_total,
            skipped_count=skipped + max(0, len(entries) - indexed_total),
            batch_count=len(batches),
            started_at=started,
            namespaces=namespaces,
        )
