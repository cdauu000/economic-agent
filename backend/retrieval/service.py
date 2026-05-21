from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..services.retrieval_governance import apply_retrieval_governance
from .schemas import (
    ChunkScores,
    ConfidenceScores,
    RankedChunk,
    RetrievalFilters,
    RetrievalResponse,
)

if TYPE_CHECKING:
    from ..rag.vector_store import VectorStoreService


class RetrievalAPI:
    def __init__(self, vector_store: "VectorStoreService") -> None:
        self._store = vector_store

    def search(
        self,
        query: str,
        *,
        top_k: int = 4,
        filters: RetrievalFilters | None = None,
    ) -> RetrievalResponse:
        started = time.perf_counter()
        filters = filters or RetrievalFilters()
        result = self._store.similarity_search(
            query,
            top_k=top_k,
            company=filters.company,
            industry=filters.industry,
            year=filters.year,
            source=filters.source,
            document_type=filters.document_type,
        )

        return self._build_response(
            query=query,
            result=result,
            filters=filters,
            started=started,
        )

    def filtered_search(
        self,
        query: str,
        *,
        top_k: int = 4,
        filters: RetrievalFilters,
    ) -> RetrievalResponse:
        if filters.is_empty():
            raise ValueError("filtered retrieval requires at least one metadata filter")
        return self.search(query, top_k=top_k, filters=filters)

    def _build_response(
        self,
        *,
        query: str,
        result,
        filters: RetrievalFilters,
        started: float,
    ) -> RetrievalResponse:
        assessment = result.assessment
        contexts = result.final_context

        if assessment is None and result.candidates:
            contexts, assessment = apply_retrieval_governance(
                question=query,
                contexts=[{"text": c.text, **c.metadata} for c in result.candidates],
                distances=[c.distance for c in result.candidates],
            )

        ranked: list[RankedChunk] = []
        candidate_by_id = {c.chunk_id: c for c in result.candidates}

        for idx, ctx in enumerate(contexts, start=1):
            chunk_id = str(ctx.get("chunk_id", ""))
            candidate = candidate_by_id.get(chunk_id)
            if candidate:
                scores = ChunkScores(
                    semantic=candidate.factors.semantic,
                    metadata_alignment=candidate.factors.metadata_alignment,
                    source_trust=candidate.factors.source_trust,
                    recency=candidate.factors.recency,
                    final_score=candidate.factors.final_score,
                    distance=candidate.distance,
                )
            else:
                scores = ChunkScores(
                    semantic=0.0,
                    metadata_alignment=0.0,
                    source_trust=0.0,
                    recency=0.0,
                    final_score=0.0,
                    distance=1.0,
                )
            ranked.append(
                RankedChunk(
                    rank=idx,
                    chunk_id=chunk_id,
                    text=str(ctx.get("text", "")),
                    metadata={k: str(v) for k, v in ctx.items() if k != "text"},
                    scores=scores,
                )
            )

        if assessment:
            confidence = ConfidenceScores(
                value=assessment.confidence_value,
                band=assessment.confidence_band,
                status=assessment.status,
                reasoning=assessment.confidence_reasoning,
                warnings=list(assessment.warnings),
                chunk_count=assessment.chunk_count,
                trusted_chunk_count=assessment.trusted_chunk_count,
            )
        else:
            confidence = ConfidenceScores(
                value=0.25,
                band="INSUFFICIENT",
                status="INSUFFICIENT_DATA",
                reasoning="No retrieval assessment available.",
                warnings=["No relevant chunks retrieved."],
                chunk_count=0,
                trusted_chunk_count=0,
            )

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return RetrievalResponse(
            query=query,
            chunks=ranked,
            confidence=confidence,
            filters_applied=filters.applied(),
            latency_ms=elapsed_ms,
        )
