# test_llm.py
from models.llm_service import LLMService, BaseLLM

class DummyLLM(BaseLLM):
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[DUMMY] {prompt}"

if __name__ == "__main__":
    llm = LLMService(llm_client=DummyLLM())
    out = llm.generate("Hello, world!")
    print(out)  # → [DUMMY] Hello, world!
