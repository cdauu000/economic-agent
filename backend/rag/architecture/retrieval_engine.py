from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..search.similarity_search import SimilaritySearchService
from .embedding_store import EmbeddingStore
from .metadata_store import MetadataFilter, MetadataStore
from .retrieval_scoring import RetrievalMode


@dataclass(frozen=True)
class RetrievalHit:
    text: str
    metadata: Dict[str, str]
    distance: float
    chunk_id: str
    semantic_score: float
    keyword_score: float
    metadata_score: float
    combined_score: float
    source_trust_score: float = 0.0
    recency_score: float = 0.0


class RetrievalEngine:
    def __init__(self, embedding_store: EmbeddingStore, metadata_store: MetadataStore) -> None:
        self._embeddings = embedding_store
        self._metadata = metadata_store
        self._similarity = SimilaritySearchService(embedding_store)

    def retrieve(
        self,
        question: str,
        *,
        top_k: int = 4,
        mode: RetrievalMode | str = RetrievalMode.HYBRID,
        filters: MetadataFilter | None = None,
        fetch_k: int | None = None,
        apply_governance: bool = True,
    ) -> List[RetrievalHit]:
        _ = mode
        filters = filters or MetadataFilter()
        result = self._similarity.search(
            question,
            top_k=top_k,
            filters=filters,
            fetch_k=fetch_k,
            apply_governance=apply_governance,
        )

        hits: List[RetrievalHit] = []
        for candidate in result.candidates:
            hits.append(
                RetrievalHit(
                    text=candidate.text,
                    metadata=candidate.metadata,
                    distance=candidate.distance,
                    chunk_id=candidate.chunk_id,
                    semantic_score=candidate.factors.semantic,
                    keyword_score=0.0,
                    metadata_score=candidate.factors.metadata_alignment,
                    combined_score=candidate.factors.final_score,
                    source_trust_score=candidate.factors.source_trust,
                    recency_score=candidate.factors.recency,
                )
            )
        return hits

    @property
    def last_search(self) -> SimilaritySearchService:
        return self._similarity
