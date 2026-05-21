__all__ = ["PromptOrchestrationPipeline", "classify_intent", "QueryIntent"]


def __getattr__(name: str):
    if name == "PromptOrchestrationPipeline":
        from .pipeline import PromptOrchestrationPipeline
        return PromptOrchestrationPipeline
    if name == "classify_intent":
        from .intent import classify_intent
        return classify_intent
    if name == "QueryIntent":
        from .intent import QueryIntent
        return QueryIntent
    raise AttributeError(name)
