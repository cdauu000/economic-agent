# Vector Update Strategy

## Purpose
Maintain up-to-date financial knowledge.

## Update Flow

```
New Documents
 ↓
Processing (validation + lifecycle)
 ↓
Embedding (normalized text)
 ↓
Index Update (dedup + stale doc replacement)
```

## Implementation

- `backend/rag/update/strategy.py`
- `backend/rag/update/pipeline.py`

## Rules

- **Avoid duplicate embeddings:** skip when `content_fingerprint` already indexed
- **Preserve metadata consistency:** `normalize_storage_metadata` + `validate_storage_metadata`
- **Maintain source traceability:** `raw_ref`, `source_ref`, `processed_file`, `doc_id`, `chunk_id`, `metadata_link`

## Behavior

- Re-upload same `doc_id` with changed chunks → remove stale chunk ids, index new set
- Unchanged chunk fingerprint → counted as `duplicate_count`, not re-embedded
