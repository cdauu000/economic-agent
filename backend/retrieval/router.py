from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .schemas import FilteredSearchRequest, RetrievalResponse, SearchRequest
from .service import RetrievalAPI

router = APIRouter(prefix="/retrieval", tags=["retrieval"])

_api: RetrievalAPI | None = None


def bind_retrieval_api(api: RetrievalAPI) -> None:
    global _api
    _api = api


def _get_api() -> RetrievalAPI:
    if _api is None:
        raise HTTPException(status_code=503, detail="retrieval api not initialized")
    return _api


@router.post("/search", response_model=RetrievalResponse)
def search(payload: SearchRequest) -> RetrievalResponse:
    return _get_api().search(
        payload.query,
        top_k=payload.top_k,
        filters=payload.filters,
    )


@router.post("/filtered", response_model=RetrievalResponse)
def filtered_search(payload: FilteredSearchRequest) -> RetrievalResponse:
    try:
        return _get_api().filtered_search(
            payload.query,
            top_k=payload.top_k,
            filters=payload.to_filters(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
