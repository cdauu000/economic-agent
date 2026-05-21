from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..services.agent_service import generate_llm_response
from ..trend_engine import predict_trend
from .entities import extract_entities
from .evaluation import evaluate_grounding
from .intent import classify_intent
from .citations import format_citation
from .prompts import build_user_prompt
from .query_plan import build_query_plan
from .reasoning import build_reasoning_layers
from .schemas import OrchestrationResult

if TYPE_CHECKING:
    from ..retrieval.service import RetrievalAPI
    from ..retrieval.schemas import RetrievalFilters


class PromptOrchestrationPipeline:
    def __init__(self, retrieval_api: "RetrievalAPI") -> None:
        self._retrieval = retrieval_api

    def run(
        self,
        question: str,
        *,
        company: Optional[str] = None,
        sector: Optional[str] = None,
        year: Optional[str] = None,
        source: Optional[str] = None,
        document_type: Optional[str] = None,
        top_k: Optional[int] = None,
        retrieval_mode: str = "hybrid",
    ) -> OrchestrationResult:
        intent = classify_intent(question)
        entities = extract_entities(
            question,
            {
                "company": company,
                "industry": sector,
                "year": year,
                "source": source,
                "document_type": document_type,
            },
        )
        plan = build_query_plan(intent, entities, top_k=top_k, retrieval_mode=retrieval_mode)

        from ..retrieval.schemas import RetrievalFilters

        retrieval = self._retrieval.search(
            question,
            top_k=plan.top_k,
            filters=RetrievalFilters(
                company=plan.filters.company,
                industry=plan.filters.industry,
                year=plan.filters.year,
                source=plan.filters.source,
                document_type=plan.filters.document_type,
            ),
        )

        contexts = [{"text": c.text, **c.metadata} for c in retrieval.chunks]
        layers = build_reasoning_layers(question, contexts)

        retrieved_context = "\n\n".join(
            f"[{idx}] source_type={row.get('source_type', 'unknown')}, "
            f"company={row.get('company', 'unknown')}, sector={row.get('sector', 'unknown')}\n"
            f"{row.get('text', '')[:1000]}"
            for idx, row in enumerate(contexts, start=1)
        )

        status = retrieval.confidence.status
        if status == "INSUFFICIENT_DATA" or not contexts:
            return self._insufficient(question, intent, retrieval, layers, plan.sufficiency_threshold)

        user_prompt = build_user_prompt(question, retrieved_context, layers)
        llm_answer = generate_llm_response(
            query=question,
            context=retrieved_context,
            user_prompt=user_prompt,
        )

        evaluation = evaluate_grounding(
            llm_answer,
            layers,
            chunk_count=retrieval.confidence.chunk_count,
            sufficiency_threshold=plan.sufficiency_threshold,
        )

        trend_payload = predict_trend(
            financial_signals=layers.signals.get("financial", []),
            sentiment_signals=layers.signals.get("sentiment", []),
            macro_signals=layers.signals.get("macro", []),
        )

        conf_value = retrieval.confidence.value
        band = retrieval.confidence.band
        if llm_answer == "insufficient data" or evaluation.hallucination_risk == "HIGH":
            conf_value = min(conf_value, 0.35)
            band = "INSUFFICIENT"
        elif evaluation.hallucination_risk == "MEDIUM":
            conf_value = min(conf_value, 0.55)
            band = "LOW" if band == "HIGH" else band

        citations = [f.citation for f in layers.facts] or [
            format_citation(c.metadata, c.chunk_id) for c in retrieval.chunks
        ]

        retrieval_dump = retrieval.model_dump() if hasattr(retrieval, "model_dump") else None

        return OrchestrationResult(
            answer=llm_answer,
            summary=(
                "RAG-based answer generated from governed retrieval."
                if llm_answer != "insufficient data"
                else "insufficient data"
            ),
            intent=intent.primary,
            intent_tags=list(intent.tags),
            evidence_snapshot=[f.text for f in layers.facts[:8]],
            signals=layers.signals,
            trend=trend_payload.trend if llm_answer != "insufficient data" else "INSUFFICIENT_DATA",
            risks=trend_payload.risks,
            opportunities=trend_payload.opportunities,
            confidence={
                "value": conf_value,
                "band": band,
                "reasoning": retrieval.confidence.reasoning,
                "warnings": list(set(retrieval.confidence.warnings + evaluation.warnings)),
            },
            retrieval_quality={
                "status": status,
                "chunk_count": retrieval.confidence.chunk_count,
                "trusted_chunk_count": retrieval.confidence.trusted_chunk_count,
                "warnings": retrieval.confidence.warnings,
            },
            assumptions=layers.assumptions,
            citations=citations,
            reasoning_layers={
                "facts": [{"text": f.text, "citation": f.citation} for f in layers.facts],
                "signals": layers.signals,
                "interpretation": layers.interpretation,
            },
            evaluation={
                "passed": evaluation.passed,
                "grounding_coverage": evaluation.grounding_coverage,
                "hallucination_risk": evaluation.hallucination_risk,
                "evidence_consistency": evaluation.evidence_consistency,
                "warnings": evaluation.warnings,
            },
            retrieval=retrieval_dump,
        )

    def _insufficient(
        self,
        question: str,
        intent,
        retrieval,
        layers,
        threshold: int,
    ) -> OrchestrationResult:
        retrieval_dump = retrieval.model_dump() if hasattr(retrieval, "model_dump") else None
        return OrchestrationResult(
            answer="insufficient data",
            summary="insufficient data",
            intent=intent.primary,
            intent_tags=list(intent.tags),
            evidence_snapshot=[],
            signals={"financial": [], "sentiment": [], "macro": []},
            trend="INSUFFICIENT_DATA",
            risks=[],
            opportunities=[],
            confidence={
                "value": retrieval.confidence.value,
                "band": "INSUFFICIENT",
                "reasoning": retrieval.confidence.reasoning,
                "warnings": retrieval.confidence.warnings,
            },
            retrieval_quality={
                "status": retrieval.confidence.status,
                "chunk_count": retrieval.confidence.chunk_count,
                "warnings": retrieval.confidence.warnings,
            },
            assumptions=layers.assumptions or [f"Minimum {threshold} evidence chunks required."],
            citations=[],
            reasoning_layers={"facts": [], "signals": layers.signals, "interpretation": ""},
            evaluation={
                "passed": False,
                "grounding_coverage": 0.0,
                "hallucination_risk": "HIGH",
                "evidence_consistency": "SPARSE",
                "warnings": ["Insufficient retrieval for answering."],
            },
            retrieval=retrieval_dump,
        )

    def to_response_dict(self, result: OrchestrationResult) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "summary": result.summary,
            "signals": result.signals,
            "score": {},
            "trend": result.trend,
            "risks": result.risks,
            "opportunities": result.opportunities,
            "confidence": result.confidence,
            "retrieval_quality": result.retrieval_quality,
            "answer": result.answer,
            "evidence": [{"text": t} for t in result.evidence_snapshot],
            "citations": result.citations,
            "assumptions": result.assumptions,
            "orchestration": {
                "intent": result.intent,
                "intent_tags": result.intent_tags,
                "reasoning_layers": result.reasoning_layers,
                "evaluation": result.evaluation,
            },
        }
        if result.retrieval is not None:
            payload["retrieval"] = result.retrieval
        return payload
