# Vector Update Strategy Rules

## Purpose
Maintain up-to-date financial knowledge in the vector index.

## Implementation
- `backend/rag/update/`
- `docs/vector-update-strategy.md`

## Update Flow
New Documents → Processing → Embedding → Index Update

## Requirements
- avoid duplicate embeddings (`content_fingerprint`)
- preserve metadata consistency (required storage fields)
- maintain source traceability (lineage metadata fields)

## API
`POST /upload` response includes `vector_update` stats.
