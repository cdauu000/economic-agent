# Retrieval API Rules

## Purpose
Expose retrieval to agent pipelines with ranked chunks and confidence scores.

## Implementation
- `backend/retrieval/`
- `docs/retrieval-api.md`

## Operations

### Search
- `POST /retrieval/search`
- optional metadata filters

### Filtered Retrieval
- `POST /retrieval/filtered`
- requires company, industry, year, source, or document_type

## Output Contract
- ranked chunks with factor scores
- confidence value, band, status, warnings
- `latency_ms` for performance monitoring

## Goals
- low latency
- high relevance
- grounded evidence only
