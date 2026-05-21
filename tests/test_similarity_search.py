import unittest
from datetime import datetime, timezone

from backend.rag.architecture.metadata_store import MetadataFilter
from backend.rag.search.similarity_scoring import (
    compute_similarity_factors,
    recency_score,
    trust_score,
)


class SimilaritySearchTests(unittest.TestCase):
    def test_recency_current_year(self):
        year = str(datetime.now(timezone.utc).year)
        self.assertEqual(recency_score({"year": year}), 1.0)

    def test_recency_old_year(self):
        self.assertLess(recency_score({"year": "2010"}), 0.4)

    def test_trust_pdf_over_news(self):
        self.assertGreater(
            trust_score({"source": "pdf"}),
            trust_score({"source": "news"}),
        )

    def test_compute_similarity_factors(self):
        factors = compute_similarity_factors(
            distance=0.3,
            metadata={
                "company": "Acme",
                "industry": "Tech",
                "year": str(datetime.now(timezone.utc).year),
                "source": "pdf",
                "document_type": "annual_report",
                "source_type": "pdf",
            },
            filters=MetadataFilter(company="Acme", year=str(datetime.now(timezone.utc).year)),
        )
        self.assertGreater(factors.semantic, 0.5)
        self.assertEqual(factors.metadata_alignment, 1.0)
        self.assertGreater(factors.final_score, factors.semantic * 0.4)


if __name__ == "__main__":
    unittest.main()
