# Vector Indexing Strategy Rules

## Purpose
Optimize retrieval latency, relevance, and memory scalability.

## Implementation
- `backend/rag/indexing/`
- `docs/vector-indexing-strategy.md`

## Indexing Flow
Chunk → Embedding → Metadata Association → Vector Indexing

## Requirements
- preserve metadata linkage (`chunk_id`, `doc_id`, `index_namespace`)
- support fast retrieval via HNSW cosine index
- support scalable batched indexing

## Optimization Goals
- retrieval latency: tuned `hnsw:search_ef`
- retrieval relevance: normalized embedding text + required metadata
- memory scalability: batch upserts and namespace partitioning
