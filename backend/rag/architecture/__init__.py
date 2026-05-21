__all__ = [
    "EmbeddingStore",
    "MetadataFilter",
    "MetadataStore",
    "RetrievalEngine",
    "RetrievalHit",
    "RetrievalMode",
    "VectorDatabase",
    "VectorDatabaseStats",
    "VectorHit",
]


def __getattr__(name: str):
    if name in {"EmbeddingStore", "VectorHit"}:
        from .embedding_store import EmbeddingStore, VectorHit

        return {"EmbeddingStore": EmbeddingStore, "VectorHit": VectorHit}[name]
    if name in {"MetadataFilter", "MetadataStore"}:
        from .metadata_store import MetadataFilter, MetadataStore

        return {"MetadataFilter": MetadataFilter, "MetadataStore": MetadataStore}[name]
    if name == "RetrievalMode":
        from .retrieval_scoring import RetrievalMode

        return RetrievalMode
    if name in {"RetrievalEngine", "RetrievalHit"}:
        from .retrieval_engine import RetrievalEngine, RetrievalHit

        return {"RetrievalEngine": RetrievalEngine, "RetrievalHit": RetrievalHit}[name]
    if name in {"VectorDatabase", "VectorDatabaseStats"}:
        from .vector_database import VectorDatabase, VectorDatabaseStats

        return {"VectorDatabase": VectorDatabase, "VectorDatabaseStats": VectorDatabaseStats}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
