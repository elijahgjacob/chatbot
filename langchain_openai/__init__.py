class ChatOpenAI:  # type: ignore
    """Stub replacement that mimics the openai ChatOpenAI interface."""
    def __init__(self, *args, **kwargs):
        pass

    class _DummyResponse:
        def __init__(self, content: str):
            self.content = content

    def invoke(self, _messages):  # type: ignore
        # Always return a dummy deterministic response for tests
        return self._DummyResponse("CONVERSATION")