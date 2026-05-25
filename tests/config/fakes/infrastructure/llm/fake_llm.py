class DummyLLM:
    def __init__(self, result=None, fail=False):
        self.result = result
        self.fail = fail
        self.calls = []

    async def generate(self, request):
        if self.fail:
            raise Exception("boom")
        self.calls.append(request)
        default_text = "You open the door and enter carefully."
        return type("LLMResponse", (), {"content": self.result or default_text})()

    async def classify(self, text):
        if self.fail:
            raise Exception("boom")
        self.calls.append({"prompt": text})  # Compatibilidade com testes de intent
        return self.result
