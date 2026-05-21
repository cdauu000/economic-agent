import unittest

from backend.rag.update.strategy import (
    build_update_plan,
    content_fingerprint,
    stamp_update_metadata,
)


def _record(i: int, text: str, doc_id: str = "doc-1") -> dict:
    return {
        "text": text,
        "chunk_id": f"chunk-{i}",
        "doc_id": doc_id,
        "company": "Acme",
        "sector": "Tech",
        "source_type": "pdf",
        "document_type": "annual_report",
        "raw_ref": "/raw/report.pdf",
        "processed_file": "report.json",
    }


class VectorUpdateTests(unittest.TestCase):
    def test_content_fingerprint_stable(self):
        a = content_fingerprint("revenue up", "c1")
        b = content_fingerprint("revenue up", "c1")
        self.assertEqual(a, b)

    def test_stamp_update_metadata_lineage(self):
        meta = stamp_update_metadata(_record(1, "x" * 60))
        self.assertIn("updated_at", meta)
        self.assertIn("source_ref", meta)
        self.assertEqual(meta["metadata_link"], "doc-1")

    def test_build_update_plan_skips_duplicates(self):
        records = [_record(1, "Revenue increased twelve percent in twenty twenty four.")]
        entries, _ = __import__(
            "backend.rag.indexing.strategy", fromlist=["prepare_index_entries"]
        ).prepare_index_entries(records)
        fp = content_fingerprint(entries[0].embedding_text, entries[0].chunk_id)

        plan, _ = build_update_plan(records, existing_hashes={fp}, stale_ids_by_doc={})
        self.assertEqual(len(plan.to_index), 0)
        self.assertEqual(len(plan.duplicate_skipped), 1)

    def test_build_update_plan_marks_stale_doc_chunks(self):
        records = [
            _record(1, "Revenue increased twelve percent in twenty twenty four.", "doc-1"),
            _record(2, "Costs rose moderately in the same reporting period.", "doc-1"),
        ]
        stale = {"doc-1": ["chunk-old"]}
        plan, _ = build_update_plan(records, existing_hashes=set(), stale_ids_by_doc=stale)
        self.assertIn("chunk-old", plan.stale_ids_to_remove)
        self.assertEqual(len(plan.to_index), 2)


if __name__ == "__main__":
    unittest.main()
