import unittest

from backend.rag.indexing.strategy import (
    batch_entries,
    build_index_namespace,
    prepare_index_entries,
)


class VectorIndexingTests(unittest.TestCase):
    def test_build_index_namespace(self):
        ns = build_index_namespace(
            {"company": "Acme", "year": "2024", "source": "pdf"}
        )
        self.assertEqual(ns, "Acme:2024:pdf")

    def test_prepare_index_entries(self):
        records = [
            {
                "text": "Revenue increased 12 percent in 2024 with stable cash flow metrics.",
                "chunk_id": "chunk-1",
                "doc_id": "doc-1",
                "company": "Acme",
                "sector": "Tech",
                "source_type": "pdf",
                "document_type": "annual_report",
                "raw_ref": "/raw/report.pdf",
                "processed_file": "report.json",
            }
        ]
        entries, skipped = prepare_index_entries(records)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].chunk_id, "chunk-1")
        self.assertEqual(entries[0].metadata["index_id"], "chunk-1")
        self.assertEqual(entries[0].metadata["metadata_link"], "doc-1")
        self.assertIn("Acme:2024:pdf", entries[0].index_namespace)

    def test_batch_entries(self):
        records = [
            {
                "text": f"Financial metric sample text segment number {i} with enough length.",
                "chunk_id": f"c{i}",
                "doc_id": "doc",
                "company": "Acme",
                "sector": "Tech",
                "source_type": "text",
                "raw_ref": "inline",
                "processed_file": "f.json",
            }
            for i in range(5)
        ]
        entries, _ = prepare_index_entries(records)
        batches = batch_entries(entries, batch_size=2)
        self.assertEqual(len(batches), 3)
        self.assertEqual(sum(len(b) for b in batches), 5)


if __name__ == "__main__":
    unittest.main()
