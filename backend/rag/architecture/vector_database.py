from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..embedding.pipeline import EmbeddingBatchResult
from ..indexing.pipeline import VectorIndexingPipeline
from ..indexing.strategy import IndexingRunResult
from ..update.pipeline import VectorUpdatePipeline
from ..update.strategy import VectorUpdateResult
from .embedding_store import EmbeddingStore
from .metadata_store import MetadataFilter, MetadataStore
from .retrieval_engine import RetrievalEngine, RetrievalHit
from .retrieval_scoring import RetrievalMode


@dataclass(frozen=True)
class VectorDatabaseStats:
    collection_name: str
    persist_directory: str
    embedding_model: str
    embedding_version: str


class VectorDatabase:
    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "economic_agent_docs",
    ) -> None:
        os.makedirs(persist_directory, exist_ok=True)
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_store = EmbeddingStore(persist_directory, collection_name)
        self.metadata_store = MetadataStore()
        self.indexing_pipeline = VectorIndexingPipeline(self.embedding_store)
        self.update_pipeline = VectorUpdatePipeline(self.embedding_store)
        self.retrieval_engine = RetrievalEngine(self.embedding_store, self.metadata_store)

    @property
    def embedding_model(self) -> str:
        return self.embedding_store.model_name

    def upsert_chunks(self, records: List[Dict[str, str]]) -> EmbeddingBatchResult:
        update_result = self.update_records(records)
        return EmbeddingBatchResult(
            embedded_count=update_result.updated_count,
            skipped_count=update_result.skipped_count,
            duplicate_count=update_result.duplicate_count,
            model=self.embedding_store.model_name,
            model_version=update_result.update_version,
        )

    def index_records(self, records: List[Dict[str, str]]) -> IndexingRunResult:
        return self.indexing_pipeline.index_records(records)

    def update_records(self, records: List[Dict[str, str]]) -> VectorUpdateResult:
        return self.update_pipeline.update_records(records)

    def similarity_search(
        self,
        question: str,
        *,
        top_k: int = 4,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        year: Optional[str] = None,
        source: Optional[str] = None,
        document_type: Optional[str] = None,
    ):
        filters = MetadataFilter(
            company=company,
            industry=industry,
            year=year,
            source=source,
            document_type=document_type,
        )
        return self.retrieval_engine.last_search.search(
            question,
            top_k=top_k,
            filters=filters,
        )

    def query(
        self,
        question: str,
        *,
        top_k: int = 4,
        mode: RetrievalMode | str = RetrievalMode.HYBRID,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        year: Optional[str] = None,
        source: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[RetrievalHit]:
        filters = MetadataFilter(
            company=company,
            industry=industry,
            year=year,
            source=source,
            document_type=document_type,
        )
        return self.retrieval_engine.retrieve(
            question,
            top_k=top_k,
            mode=mode,
            filters=filters,
        )

    def get_by_chunk_id(self, chunk_id: str) -> RetrievalHit | None:
        hit = self.embedding_store.get_by_chunk_id(chunk_id)
        if hit is None:
            return None
        return RetrievalHit(
            text=hit.text,
            metadata=hit.metadata,
            distance=hit.distance,
            chunk_id=hit.chunk_id,
            semantic_score=1.0,
            keyword_score=0.0,
            metadata_score=1.0,
            combined_score=1.0,
        )

    def stats(self) -> VectorDatabaseStats:
        return VectorDatabaseStats(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_model=self.embedding_store.model_name,
            embedding_version=self.embedding_store.model_version,
        )
