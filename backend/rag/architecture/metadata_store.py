from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..storage.metadata import (
    REQUIRED_STORAGE_FIELDS,
    build_chroma_filter,
    normalize_storage_metadata,
    validate_storage_metadata,
)


@dataclass(frozen=True)
class MetadataFilter:
    company: str | None = None
    industry: str | None = None
    year: str | None = None
    source: str | None = None
    document_type: str | None = None

    def to_chroma(self) -> Dict[str, object] | None:
        return build_chroma_filter(
            company=self.company,
            industry=self.industry,
            year=self.year,
            source=self.source,
            document_type=self.document_type,
        )

    def is_restrictive(self) -> bool:
        return any(
            [
                self.company,
                self.industry,
                self.year,
                self.source,
                self.document_type,
            ]
        )


class MetadataStore:
    required_fields = REQUIRED_STORAGE_FIELDS

    def normalize(self, record: Dict[str, str]) -> Dict[str, str]:
        return normalize_storage_metadata(record)

    def validate(self, metadata: Dict[str, str]) -> List[str]:
        return validate_storage_metadata(metadata)

    def prepare_records(self, records: List[Dict[str, str]]) -> List[Dict[str, str]]:
        prepared: List[Dict[str, str]] = []
        for record in records:
            meta = self.normalize(record)
            if self.validate(meta):
                continue
            prepared.append(meta)
        return prepared

    def matches_filter(self, metadata: Dict[str, str], filters: MetadataFilter) -> bool:
        if filters.company and metadata.get("company") != filters.company:
            return False
        if filters.industry and metadata.get("industry") != filters.industry:
            return False
        if filters.year and metadata.get("year") != filters.year:
            return False
        if filters.source and metadata.get("source") != filters.source:
            return False
        if filters.document_type and metadata.get("document_type") != filters.document_type:
            return False
        return True

    def metadata_match_score(self, metadata: Dict[str, str], filters: MetadataFilter) -> float:
        if not filters.is_restrictive():
            return 0.5
        checks = [
            (filters.company, "company"),
            (filters.industry, "industry"),
            (filters.year, "year"),
            (filters.source, "source"),
            (filters.document_type, "document_type"),
        ]
        active = [(expected, key) for expected, key in checks if expected]
        if not active:
            return 0.5
        hits = sum(1 for expected, key in active if metadata.get(key) == expected)
        return hits / len(active)
