import unittest

from backend.retrieval.schemas import FilteredSearchRequest, RetrievalFilters, SearchRequest


class RetrievalApiSchemaTests(unittest.TestCase):
    def test_search_request_defaults(self):
        req = SearchRequest(query="revenue trend")
        self.assertEqual(req.top_k, 4)
        self.assertTrue(req.filters.is_empty())

    def test_filters_applied(self):
        filt = RetrievalFilters(company="Acme", year="2024")
        self.assertEqual(filt.applied(), {"company": "Acme", "year": "2024"})

    def test_filtered_request_requires_filter(self):
        with self.assertRaises(ValueError):
            FilteredSearchRequest(query="test")

    def test_filtered_request_valid(self):
        req = FilteredSearchRequest(query="test", company="Acme", year="2024")
        self.assertEqual(req.to_filters().company, "Acme")


if __name__ == "__main__":
    unittest.main()
