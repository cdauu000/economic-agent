from .constants import HNSW_COLLECTION_METADATA, INDEX_BATCH_SIZE, INDEX_VERSION
from .strategy import IndexEntry, IndexingRunResult, build_index_namespace, prepare_index_entries

__all__ = [
    "HNSW_COLLECTION_METADATA",
    "INDEX_BATCH_SIZE",
    "INDEX_VERSION",
    "IndexEntry",
    "IndexingRunResult",
    "VectorIndexingPipeline",
    "build_index_namespace",
    "prepare_index_entries",
]


def __getattr__(name: str):
    if name == "VectorIndexingPipeline":
        from .pipeline import VectorIndexingPipeline

        return VectorIndexingPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
