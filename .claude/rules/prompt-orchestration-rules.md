# Prompt Orchestration Rules

## Implementation
- `backend/orchestration/`
- `.claude/prompts/`

## Flow
Intent Detection → Query Plan → Retrieval → Layered Reasoning → Grounding Evaluation → LLM Answer

## Requirements
- retrieval-first before LLM
- metadata-aware query plans when entities present
- facts/signals/assumptions separation
- grounding evaluation before response
- `INSUFFICIENT_DATA` when evidence threshold fails

## API
`POST /ask` uses `PromptOrchestrationPipeline`.
