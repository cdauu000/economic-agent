# Phase 2 — Prompt Orchestration & Reasoning Layer

## Components
- `backend/orchestration/intent.py`
- `backend/orchestration/entities.py`
- `backend/orchestration/query_plan.py`
- `backend/orchestration/prompts.py`
- `backend/orchestration/reasoning.py`
- `backend/orchestration/evaluation.py`
- `backend/orchestration/pipeline.py`

## Flow
User Query → Intent → Query Plan → Retrieval → Reasoning Layers → Evaluation → Prompt → LLM → Structured Output

## Integration
- `RetrievalAPI`
- `generate_llm_response`
- `predict_trend`
- `POST /ask`
