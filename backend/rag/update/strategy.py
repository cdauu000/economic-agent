from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Dict, List, Set

from ..indexing.strategy import IndexEntry, prepare_index_entries
from ..storage.metadata import normalize_storage_metadata, validate_storage_metadata
from .constants import LINEAGE_FIELDS, UPDATE_VERSION


@dataclass
class UpdatePlan:
    to_index: List[IndexEntry] = field(default_factory=list)
    duplicate_skipped: List[str] = field(default_factory=list)
    stale_ids_to_remove: List[str] = field(default_factory=list)
    doc_ids_updated: List[str] = field(default_factory=list)


@dataclass
class VectorUpdateResult:
    updated_count: int
    skipped_count: int
    duplicate_count: int
    replaced_count: int
    batch_count: int
    latency_ms: float
    update_version: str = UPDATE_VERSION
    doc_ids: List[str] = field(default_factory=list)


def content_fingerprint(embedding_text: str, chunk_id: str) -> str:
    payload = f"{UPDATE_VERSION}:{chunk_id}:{embedding_text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stamp_update_metadata(metadata: Dict[str, str], *, source_ref: str = "") -> Dict[str, str]:
    meta = normalize_storage_metadata(metadata)
    meta["update_version"] = UPDATE_VERSION
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta["source_ref"] = meta.get("source_ref") or source_ref or meta.get("raw_ref", "")
    meta["metadata_link"] = meta.get("doc_id", meta.get("chunk_id", ""))
    for key in LINEAGE_FIELDS:
        meta.setdefault(key, meta.get(key, ""))
    return meta


def validate_metadata_consistency(metadata: Dict[str, str]) -> List[str]:
    return validate_storage_metadata(metadata)


def build_update_plan(
    records: List[Dict[str, str]],
    *,
    existing_hashes: Set[str],
    stale_ids_by_doc: Dict[str, List[str]],
) -> tuple[UpdatePlan, int]:
    entries, skipped = prepare_index_entries(records)
    plan = UpdatePlan()
    seen_fingerprints: Set[str] = set()

    doc_ids_in_batch: Set[str] = set()
    for entry in entries:
        doc_id = entry.metadata.get("doc_id", "")
        if doc_id:
            doc_ids_in_batch.add(doc_id)

    for doc_id in doc_ids_in_batch:
        stale = stale_ids_by_doc.get(doc_id, [])
        for chunk_id in stale:
            if chunk_id not in plan.stale_ids_to_remove:
                plan.stale_ids_to_remove.append(chunk_id)
        if stale:
            plan.doc_ids_updated.append(doc_id)

    for entry in entries:
        fingerprint = content_fingerprint(entry.embedding_text, entry.chunk_id)
        meta = stamp_update_metadata(entry.metadata)
        meta["content_fingerprint"] = fingerprint
        stamped = replace(entry, metadata=meta)

        if fingerprint in existing_hashes or fingerprint in seen_fingerprints:
            plan.duplicate_skipped.append(stamped.chunk_id)
            continue

        seen_fingerprints.add(fingerprint)
        plan.to_index.append(stamped)

    return plan, skipped


def entries_to_update_records(entries: List[IndexEntry]) -> List[Dict[str, str]]:
    return [{**entry.metadata, "text": entry.display_text} for entry in entries]
