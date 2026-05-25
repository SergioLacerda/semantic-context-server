class FakeResponseOpenAI:
    def __init__(
        self,
        content: str,
        *,
        prompt_tokens: int | None = 10,
        completion_tokens: int | None = 5,
    ):
        self.choices = [
            type(
                "Choice",
                (),
                {
                    "message": type("Message", (), {"content": content})(),
                },
            )()
        ]
        self.usage = type(
            "Usage",
            (),
            {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        )()


class FakeResponseEmpty:
    def __init__(self):
        self.choices = []
        self.usage = type(
            "Usage",
            (),
            {
                "prompt_tokens": None,
                "completion_tokens": None,
            },
        )()


class FakeOllamaResponse:
    def __init__(self, content: str):
        self._content = content

    def json(self):
        return {"response": self._content}
