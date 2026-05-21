# Retrieval API

## Purpose
Expose retrieval functionality to agent pipelines.

## Endpoints

### `POST /retrieval/search`
General semantic search with optional metadata filters.

**Input**
```json
{
  "query": "revenue outlook for Acme",
  "top_k": 4,
  "filters": {
    "company": "Acme Corp",
    "industry": "Manufacturing",
    "year": "2024",
    "source": "pdf",
    "document_type": "annual_report"
  }
}
```

### `POST /retrieval/filtered`
Requires at least one of: `company`, `industry`, `year`, `source`, `document_type`.

**Input**
```json
{
  "query": "cash flow risks",
  "top_k": 4,
  "company": "Acme Corp",
  "industry": "Manufacturing",
  "year": "2024"
}
```

**Output**
```json
{
  "query": "string",
  "chunks": [
    {
      "rank": 1,
      "chunk_id": "string",
      "text": "string",
      "metadata": {},
      "scores": {
        "semantic": 0.0,
        "metadata_alignment": 0.0,
        "source_trust": 0.0,
        "recency": 0.0,
        "final_score": 0.0,
        "distance": 0.0
      }
    }
  ],
  "confidence": {
    "value": 0.0,
    "band": "HIGH",
    "status": "OK",
    "reasoning": "string",
    "warnings": [],
    "chunk_count": 0,
    "trusted_chunk_count": 0
  },
  "filters_applied": {},
  "latency_ms": 0.0
}
```

## Implementation
- `backend/retrieval/service.py`
- `backend/retrieval/router.py`
- `backend/retrieval/schemas.py`

## Goals
- low latency (`latency_ms` in response)
- high relevance (similarity factor reranking)
- grounded evidence (governance + confidence scores)
