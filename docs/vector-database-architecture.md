# Vector Database Architecture

## Purpose
Store and retrieve semantic embeddings for financial intelligence retrieval.

## Components

### Embedding Store
`backend/rag/architecture/embedding_store.py`

Stores:
- vector embeddings
- semantic representations

Backed by Chroma + embedding pipeline.

### Metadata Store
`backend/rag/architecture/metadata_store.py`

Stores:
- company
- industry
- year
- source
- document type
- chunk id and lineage fields

### Retrieval Engine
`backend/rag/architecture/retrieval_engine.py`

Performs:
- similarity search
- metadata filtering
- hybrid keyword + semantic blending
- governance reranking

## Facade
`backend/rag/architecture/vector_database.py`

## Supported Retrieval

| Mode | Behavior |
|------|----------|
| `semantic` | embedding similarity only |
| `hybrid` | semantic + keyword + metadata scores |
| `metadata` | metadata-weighted semantic retrieval |

## API
`POST /ask` accepts `retrieval_mode`: `semantic`, `hybrid`, `metadata`.
