from __future__ import annotations

INDEX_VERSION = "1.0.0"
INDEX_BATCH_SIZE = 64
MIN_INDEX_CHARS = 50

HNSW_COLLECTION_METADATA = {
    "hnsw:space": "cosine",
    "hnsw:construction_ef": 128,
    "hnsw:M": 16,
    "hnsw:search_ef": 64,
}

INDEX_METADATA_FIELDS = (
    "chunk_id",
    "doc_id",
    "company",
    "industry",
    "year",
    "source",
    "document_type",
    "index_namespace",
    "index_version",
    "indexed_at",
)
