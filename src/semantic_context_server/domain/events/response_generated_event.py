class ResponseGeneratedEvent:
    def __init__(self, prompt: str, response: str):
        self.prompt = prompt
        self.response = response
