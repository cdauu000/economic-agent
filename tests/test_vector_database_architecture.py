import unittest

from backend.rag.architecture.metadata_store import MetadataFilter, MetadataStore
from backend.rag.architecture.retrieval_scoring import (
    RetrievalMode,
    blend_scores,
    keyword_score,
    semantic_score,
)


class VectorDatabaseArchitectureTests(unittest.TestCase):
    def test_semantic_score_from_distance(self):
        self.assertGreater(semantic_score(0.2), semantic_score(1.0))

    def test_keyword_score_matches_terms(self):
        score = keyword_score("Acme revenue 2024", "Acme Corp revenue grew in 2024")
        self.assertGreater(score, 0.5)

    def test_hybrid_blend(self):
        combined = blend_scores(semantic=0.8, keyword=0.6, metadata=0.5, mode=RetrievalMode.HYBRID)
        self.assertGreaterEqual(combined, 0.69)

    def test_metadata_filter_match(self):
        store = MetadataStore()
        meta = {
            "company": "Acme",
            "industry": "Tech",
            "year": "2024",
            "source": "pdf",
            "document_type": "annual_report",
            "chunk_id": "c1",
        }
        filt = MetadataFilter(company="Acme", year="2024")
        self.assertTrue(store.matches_filter(meta, filt))
        self.assertEqual(store.metadata_match_score(meta, filt), 1.0)

    def test_metadata_filter_chroma_clause(self):
        clause = MetadataFilter(company="Acme", source="pdf").to_chroma()
        self.assertEqual(clause, {"$and": [{"company": "Acme"}, {"source": "pdf"}]})


if __name__ == "__main__":
    unittest.main()
