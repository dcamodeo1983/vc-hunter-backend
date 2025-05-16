
import tiktoken

class TokenTracker:
    def __init__(self):
        self.usage = {}

    def estimate(self, model: str, text: str) -> int:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    def add(self, agent: str, model: str, text: str):
        tokens = self.estimate(model, text)
        self.usage[agent] = self.usage.get(agent, 0) + tokens

    def report(self):
        return {agent: f"{count} tokens" for agent, count in self.usage.items()}
