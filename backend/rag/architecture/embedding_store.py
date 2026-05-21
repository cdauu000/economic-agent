from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from langchain_core.documents import Document

from ..embedding.pipeline import EmbeddingBatchResult, EmbeddingPipeline


@dataclass(frozen=True)
class VectorHit:
    text: str
    metadata: Dict[str, str]
    distance: float
    chunk_id: str


class EmbeddingStore:
    def __init__(self, persist_directory: str, collection_name: str = "economic_agent_docs") -> None:
        self._pipeline = EmbeddingPipeline(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )
        self.collection_name = collection_name
        self.persist_directory = persist_directory

    @property
    def model_name(self) -> str:
        return self._pipeline.model_name

    @property
    def model_version(self) -> str:
        return self._pipeline.model_version

    def upsert(
        self,
        *,
        ids: List[str],
        embedding_texts: List[str],
        metadatas: List[Dict[str, str]],
    ) -> EmbeddingBatchResult:
        records = []
        for chunk_id, text, meta in zip(ids, embedding_texts, metadatas, strict=True):
            row = dict(meta)
            row["chunk_id"] = chunk_id
            row["text"] = meta.get("text", text)
            records.append(row)
        return self._pipeline.embed_and_store(records)

    def embed_and_store_records(self, records: List[Dict[str, str]]) -> EmbeddingBatchResult:
        return self._pipeline.embed_and_store(records)

    def similarity_search(
        self,
        query: str,
        *,
        top_k: int = 4,
        filter_clause: Optional[Dict[str, object]] = None,
    ) -> List[VectorHit]:
        if filter_clause:
            pairs = self._similarity_with_filter(query, filter_clause, top_k=top_k)
        else:
            pairs = self._pipeline.query_normalized(query, top_k=top_k)

        hits: List[VectorHit] = []
        for doc, score in pairs:
            metadata = {k: str(v) for k, v in doc.metadata.items()}
            hits.append(
                VectorHit(
                    text=str(metadata.get("text") or doc.page_content),
                    metadata=metadata,
                    distance=float(score),
                    chunk_id=str(metadata.get("chunk_id", "")),
                )
            )
        return hits

    def get_by_chunk_id(self, chunk_id: str) -> VectorHit | None:
        try:
            data = self._pipeline._store._collection.get(  # noqa: SLF001
                ids=[chunk_id],
                include=["metadatas", "documents"],
            )
            ids = data.get("ids") or []
            if not ids:
                return None
            metadata = {k: str(v) for k, v in (data.get("metadatas") or [{}])[0].items()}
            text = str((data.get("documents") or [""])[0] or metadata.get("text", ""))
            return VectorHit(text=text, metadata=metadata, distance=0.0, chunk_id=chunk_id)
        except Exception:
            return None

    def delete_ids(self, ids: List[str]) -> None:
        if not ids:
            return
        try:
            self._pipeline._store._collection.delete(ids=ids)  # noqa: SLF001
        except Exception:
            pass

    def existing_ids(self, ids: List[str]) -> set[str]:
        try:
            data = self._pipeline._store._collection.get(ids=ids)  # noqa: SLF001
            return set(data.get("ids") or [])
        except Exception:
            return set()

    def get_ids_by_doc_id(self, doc_id: str) -> List[str]:
        if not doc_id:
            return []
        try:
            data = self._pipeline._store._collection.get(where={"doc_id": doc_id})  # noqa: SLF001
            return list(data.get("ids") or [])
        except Exception:
            return []

    def _similarity_with_filter(
        self,
        query: str,
        filter_clause: Dict[str, object],
        *,
        top_k: int,
    ) -> List[tuple[Document, float]]:
        from ..embedding.normalizer import normalize_query_text

        normalized = normalize_query_text(query)
        try:
            return self._pipeline._store.similarity_search_with_score(  # type: ignore[return-value]
                normalized,
                k=top_k,
                filter=filter_clause,
            )
        except Exception:
            return self._pipeline.query_normalized(query, top_k=top_k)
