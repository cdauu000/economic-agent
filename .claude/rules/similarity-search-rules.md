# Similarity Search Rules

## Purpose
Retrieve semantically relevant chunks for financial Q&A.

## Implementation
- `backend/rag/search/`
- `docs/similarity-search.md`

## Search Flow
User Query → Embedding → Vector Search → Candidates → Reranking → Final Context

## Similarity Factors
- semantic similarity (vector distance)
- metadata alignment (company, industry, year, source, document_type)
- source trust (pdf > excel > text > news)
- recency (year-based freshness)

## Requirements
- Apply retrieval governance after similarity reranking.
- Return `INSUFFICIENT_DATA` when candidate quality is below threshold.
