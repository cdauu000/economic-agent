from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

from ...services.retrieval_governance import RetrievalAssessment, apply_retrieval_governance
from ..architecture.metadata_store import MetadataFilter
from ..embedding.normalizer import normalize_query_text
from .similarity_scoring import SimilarityFactors, compute_similarity_factors

if TYPE_CHECKING:
    from ..architecture.embedding_store import EmbeddingStore


@dataclass(frozen=True)
class SimilarityCandidate:
    text: str
    metadata: Dict[str, str]
    distance: float
    chunk_id: str
    factors: SimilarityFactors


@dataclass
class SimilaritySearchResult:
    query: str
    candidates: List[SimilarityCandidate] = field(default_factory=list)
    final_context: List[Dict[str, str]] = field(default_factory=list)
    assessment: RetrievalAssessment | None = None


class SimilaritySearchService:
    def __init__(self, embedding_store: "EmbeddingStore") -> None:
        self._embeddings = embedding_store

    def search(
        self,
        query: str,
        *,
        top_k: int = 4,
        filters: MetadataFilter | None = None,
        fetch_k: int | None = None,
        apply_governance: bool = True,
    ) -> SimilaritySearchResult:
        filters = filters or MetadataFilter()
        normalized_query = normalize_query_text(query)
        search_k = fetch_k or max(top_k * 3, top_k)

        filter_clause = filters.to_chroma() if filters.is_restrictive() else None
        vector_hits = self._embeddings.similarity_search(
            normalized_query,
            top_k=search_k,
            filter_clause=filter_clause,
        )
        if not vector_hits and filters.is_restrictive():
            vector_hits = self._embeddings.similarity_search(normalized_query, top_k=search_k)

        candidates: List[SimilarityCandidate] = []
        for hit in vector_hits:
            if filters.is_restrictive():
                from ..architecture.metadata_store import MetadataStore

                if not MetadataStore().matches_filter(hit.metadata, filters):
                    continue
            factors = compute_similarity_factors(
                distance=hit.distance,
                metadata=hit.metadata,
                filters=filters,
            )
            candidates.append(
                SimilarityCandidate(
                    text=hit.text,
                    metadata=hit.metadata,
                    distance=hit.distance,
                    chunk_id=hit.chunk_id,
                    factors=factors,
                )
            )

        candidates.sort(key=lambda c: c.factors.final_score, reverse=True)
        candidates = candidates[:top_k]

        result = SimilaritySearchResult(query=query, candidates=candidates)
        if not candidates:
            return result

        contexts = [{"text": c.text, **c.metadata} for c in candidates]
        distances = [c.distance for c in candidates]

        if apply_governance:
            governed, assessment = apply_retrieval_governance(
                question=query,
                contexts=contexts,
                distances=distances,
            )
            result = SimilaritySearchResult(
                query=query,
                candidates=candidates,
                final_context=governed,
                assessment=assessment,
            )
        else:
            result = SimilaritySearchResult(
                query=query,
                candidates=candidates,
                final_context=contexts,
            )

        return result
