import unittest

from backend.orchestration.entities import extract_entities
from backend.orchestration.evaluation import evaluate_grounding
from backend.orchestration.intent import INTENT_METRIC, INTENT_TREND, classify_intent
from backend.orchestration.query_plan import build_query_plan
from backend.orchestration.reasoning import build_reasoning_layers


class OrchestrationTests(unittest.TestCase):
    def test_classify_metric_intent(self):
        intent = classify_intent("What was FPT revenue in 2024?")
        self.assertEqual(intent.primary, INTENT_METRIC)

    def test_classify_trend_intent(self):
        intent = classify_intent("EV market trend next year")
        self.assertEqual(intent.primary, INTENT_TREND)

    def test_extract_entities_year(self):
        entities = extract_entities("FPT revenue 2024", {"company": "FPT"})
        self.assertEqual(entities.year, "2024")
        self.assertEqual(entities.company, "FPT")

    def test_query_plan_strategic_top_k(self):
        intent = classify_intent("Analyze banking sector risks")
        entities = extract_entities("Analyze banking sector risks", {})
        plan = build_query_plan(intent, entities)
        self.assertGreaterEqual(plan.top_k, 4)
        self.assertEqual(plan.sufficiency_threshold, 2)

    def test_reasoning_layers_extract_facts(self):
        contexts = [
            {
                "text": "Revenue increased twelve percent year over year in the reporting period.",
                "chunk_id": "c1",
                "company": "Acme",
                "source_type": "pdf",
                "year": "2024",
            }
        ]
        layers = build_reasoning_layers("Acme revenue", contexts)
        self.assertGreaterEqual(len(layers.facts), 1)

    def test_evaluate_grounding_insufficient(self):
        intent = classify_intent("test")
        layers = build_reasoning_layers("test", [])
        ev = evaluate_grounding("insufficient data", layers, chunk_count=0, sufficiency_threshold=1)
        self.assertFalse(ev.passed)


if __name__ == "__main__":
    unittest.main()
