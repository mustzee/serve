"""
Backend implementations for different LLM inference engines
"""
from .base import BaseBackend
from .ollama import OllamaBackend
from .llamacpp import LlamaCppBackend
from .vllm import VLLMBackend


def get_backend(backend_type: str) -> BaseBackend:
    """Factory function to get the appropriate backend"""
    backends = {
        "ollama": OllamaBackend,
        "llamacpp": LlamaCppBackend,
        "vllm": VLLMBackend,
    }

    backend_class = backends.get(backend_type.lower())
    if not backend_class:
        raise ValueError(
            f"Unknown backend type: {backend_type}. "
            f"Available: {list(backends.keys())}"
        )

    return backend_class()


__all__ = [
    "BaseBackend",
    "OllamaBackend",
    "LlamaCppBackend",
    "VLLMBackend",
    "get_backend"
]
