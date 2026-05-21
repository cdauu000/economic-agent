Task: Answer a financial query using orchestrated retrieval and layered reasoning.

Steps:
1. Classify intent and build query plan with metadata filters.
2. Retrieve governed evidence chunks.
3. Extract facts and derive signals from evidence only.
4. Evaluate grounding before final answer.
5. Return structured output with citations and confidence.

Output layers:
- facts (cited)
- signals (financial, sentiment, macro)
- interpretation
- assumptions
