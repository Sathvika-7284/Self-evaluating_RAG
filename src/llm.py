from ollama import chat


class LessonLLM:
    """Small adapter for a locally installed Ollama model."""

    def __init__(self, model: str | None = None):
        self.model = model or "llama3.2:3b"

    def text(self, prompt: str) -> str:
        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3},
        )
        return response.message.content.strip()
