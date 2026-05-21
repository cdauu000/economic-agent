from __future__ import annotations

import time
from typing import Dict, List, Set, TYPE_CHECKING

from ..indexing.strategy import batch_entries
from .constants import UPDATE_BATCH_SIZE
from .strategy import (
    VectorUpdateResult,
    build_update_plan,
    content_fingerprint,
    entries_to_update_records,
    stamp_update_metadata,
)

if TYPE_CHECKING:
    from ..architecture.embedding_store import EmbeddingStore


class VectorUpdatePipeline:
    def __init__(self, embedding_store: "EmbeddingStore") -> None:
        self._store = embedding_store

    def _load_existing_hashes(self, chunk_ids: List[str]) -> Set[str]:
        hashes: Set[str] = set()
        if not chunk_ids:
            return hashes
        try:
            data = self._store._pipeline._store._collection.get(  # noqa: SLF001
                ids=chunk_ids,
                include=["metadatas"],
            )
            for meta in data.get("metadatas") or []:
                if not meta:
                    continue
                fp = str(meta.get("content_fingerprint", "")).strip()
                if fp:
                    hashes.add(fp)
                else:
                    text = str(meta.get("text", ""))
                    cid = str(meta.get("chunk_id", ""))
                    if text and cid:
                        hashes.add(content_fingerprint(text, cid))
        except Exception:
            pass
        return hashes

    def _stale_ids_for_doc(self, doc_id: str, incoming_ids: Set[str]) -> List[str]:
        if not doc_id:
            return []
        try:
            data = self._store._pipeline._store._collection.get(  # noqa: SLF001
                where={"doc_id": doc_id},
                include=["metadatas"],
            )
            stale: List[str] = []
            for chunk_id in data.get("ids") or []:
                if chunk_id not in incoming_ids:
                    stale.append(chunk_id)
            return stale
        except Exception:
            return []

    def update_records(self, records: List[Dict[str, str]]) -> VectorUpdateResult:
        started = time.perf_counter()

        normalized: List[Dict[str, str]] = []
        for record in records:
            row = stamp_update_metadata(dict(record))
            if row.get("text"):
                normalized.append(row)

        incoming_doc_ids = {str(r.get("doc_id", "")) for r in normalized if r.get("doc_id")}
        incoming_chunk_ids = {str(r.get("chunk_id", "")) for r in normalized if r.get("chunk_id")}

        stale_by_doc: Dict[str, List[str]] = {}
        for doc_id in incoming_doc_ids:
            stale_by_doc[doc_id] = self._stale_ids_for_doc(doc_id, incoming_chunk_ids)

        existing_hashes = self._load_existing_hashes(list(incoming_chunk_ids))
        plan, prep_skipped = build_update_plan(
            normalized,
            existing_hashes=existing_hashes,
            stale_ids_by_doc=stale_by_doc,
        )

        if plan.stale_ids_to_remove:
            self._store.delete_ids(plan.stale_ids_to_remove)

        if not plan.to_index:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return VectorUpdateResult(
                updated_count=0,
                skipped_count=prep_skipped + len(plan.duplicate_skipped),
                duplicate_count=len(plan.duplicate_skipped),
                replaced_count=len(plan.stale_ids_to_remove),
                batch_count=0,
                latency_ms=elapsed_ms,
                doc_ids=sorted(set(plan.doc_ids_updated)),
            )

        replace_ids = [e.chunk_id for e in plan.to_index]
        existing = self._store.existing_ids(replace_ids)
        replaced_chunk_ids = len(existing)
        if existing:
            self._store.delete_ids(list(existing))

        batches = batch_entries(plan.to_index, UPDATE_BATCH_SIZE)
        updated_total = 0
        for batch in batches:
            batch_records = entries_to_update_records(batch)
            result = self._store.embed_and_store_records(batch_records)
            updated_total += result.embedded_count

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return VectorUpdateResult(
            updated_count=updated_total,
            skipped_count=prep_skipped + len(plan.duplicate_skipped),
            duplicate_count=len(plan.duplicate_skipped),
            replaced_count=len(plan.stale_ids_to_remove) + replaced_chunk_ids,
            batch_count=len(batches),
            latency_ms=elapsed_ms,
            doc_ids=sorted(set(plan.doc_ids_updated)),
        )
