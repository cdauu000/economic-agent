# Vector Indexing Strategy

## Purpose
Optimize retrieval speed and semantic relevance.

## Indexing Flow

```
Chunk
 ↓
Embedding
 ↓
Metadata Association
 ↓
Vector Indexing
```

## Implementation

- `backend/rag/indexing/strategy.py`
- `backend/rag/indexing/pipeline.py`
- `backend/rag/indexing/constants.py`

## Indexing Requirements

- preserve metadata linkage (`index_id`, `metadata_link`, `index_namespace`)
- support fast retrieval (HNSW cosine, `hnsw:search_ef=64`)
- support scalable indexing (`INDEX_BATCH_SIZE=64`)

## HNSW Settings

- `hnsw:space`: cosine
- `hnsw:M`: 16
- `hnsw:construction_ef`: 128
- `hnsw:search_ef`: 64

## Metadata Fields

- `index_namespace`: `{company}:{year}:{source}`
- `index_version`
- `indexed_at`

## API

`POST /upload` response includes `indexing` stats: `batch_count`, `latency_ms`, `namespaces`.
