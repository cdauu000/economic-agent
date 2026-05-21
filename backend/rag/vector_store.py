from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .architecture.vector_database import VectorDatabase
from .architecture.retrieval_scoring import RetrievalMode
from .embedding.pipeline import EmbeddingBatchResult
from .indexing.strategy import IndexingRunResult
from .update.strategy import VectorUpdateResult


@dataclass(frozen=True)
class RetrievalResult:
    text: str
    metadata: Dict[str, str]
    distance: float = 1.0
    chunk_id: str = ""
    retrieval_mode: str = "hybrid"
    combined_score: float = 0.0


class VectorStoreService:
    def __init__(self, persist_directory: str) -> None:
        self._db = VectorDatabase(persist_directory=persist_directory)

    def add_documents(self, records: List[Dict[str, str]]) -> EmbeddingBatchResult:
        return self._db.upsert_chunks(records)

    def index_records(self, records: List[Dict[str, str]]) -> IndexingRunResult:
        return self._db.index_records(records)

    def update_records(self, records: List[Dict[str, str]]) -> VectorUpdateResult:
        return self._db.update_records(records)

    def query(
        self,
        question: str,
        top_k: int = 4,
        *,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        year: Optional[str] = None,
        source: Optional[str] = None,
        document_type: Optional[str] = None,
        retrieval_mode: RetrievalMode | str = RetrievalMode.HYBRID,
    ) -> List[RetrievalResult]:
        hits = self._db.query(
            question,
            top_k=top_k,
            mode=retrieval_mode,
            company=company,
            industry=industry,
            year=year,
            source=source,
            document_type=document_type,
        )
        return [
            RetrievalResult(
                text=item.text,
                metadata=item.metadata,
                distance=item.distance,
                chunk_id=item.chunk_id,
                retrieval_mode=str(retrieval_mode),
                combined_score=item.combined_score,
            )
            for item in hits
        ]

    def get_by_chunk_id(self, chunk_id: str) -> RetrievalResult | None:
        hit = self._db.get_by_chunk_id(chunk_id)
        if hit is None:
            return None
        return RetrievalResult(
            text=hit.text,
            metadata=hit.metadata,
            distance=hit.distance,
            chunk_id=hit.chunk_id,
            combined_score=hit.combined_score,
        )

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
        return self._db.similarity_search(
            question,
            top_k=top_k,
            company=company,
            industry=industry,
            year=year,
            source=source,
            document_type=document_type,
        )

    @property
    def embedding_model(self) -> str:
        return self._db.embedding_model
