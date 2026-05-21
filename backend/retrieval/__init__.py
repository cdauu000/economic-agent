from .schemas import FilteredSearchRequest, RetrievalFilters, RetrievalResponse, SearchRequest
from .service import RetrievalAPI

__all__ = [
    "RetrievalAPI",
    "RetrievalFilters",
    "RetrievalResponse",
    "SearchRequest",
    "FilteredSearchRequest",
    "bind_retrieval_api",
    "router",
]


def __getattr__(name: str):
    if name == "bind_retrieval_api":
        from .router import bind_retrieval_api

        return bind_retrieval_api
    if name == "router":
        from .router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
