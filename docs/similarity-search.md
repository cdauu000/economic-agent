# Similarity Search

## Purpose
Retrieve semantically relevant chunks.

## Search Flow

```
User Query
 ↓
Embedding Generation (normalize_query_text)
 ↓
Vector Similarity Search (Chroma HNSW)
 ↓
Candidate Retrieval
 ↓
Reranking (semantic + metadata + trust + recency)
 ↓
Governance Reranking
 ↓
Final Context
```

## Implementation

- `backend/rag/search/similarity_search.py`
- `backend/rag/search/similarity_scoring.py`

## Similarity Factors

| Factor | Weight |
|--------|--------|
| semantic similarity | 0.50 |
| metadata alignment | 0.20 |
| source trust | 0.20 |
| recency | 0.10 |

## API

`POST /ask` returns `similarity_search` with per-candidate factor scores.
