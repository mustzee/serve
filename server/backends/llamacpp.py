"""
llama.cpp backend implementation
"""
import json
import time
from typing import List, Dict, Any, AsyncIterator, Optional
from .base import BaseBackend
from ..config import settings


class LlamaCppBackend(BaseBackend):
    """Backend for llama.cpp Python bindings"""

    def __init__(self):
        self.llama = None
        self.model_path = settings.llamacpp_model_path
        self.loaded_models = {}

    async def initialize(self) -> None:
        """Initialize llama.cpp"""
        try:
            from llama_cpp import Llama
            self.llama_class = Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. "
                "Install with: pip install llama-cpp-python"
            )

    async def cleanup(self) -> None:
        """Cleanup loaded models"""
        self.loaded_models.clear()

    def _get_model(self, model_name: str):
        """Load model if not already loaded"""
        if model_name not in self.loaded_models:
            import os
            model_file = os.path.join(self.model_path, f"{model_name}.gguf")

            if not os.path.exists(model_file):
                # Try without .gguf extension
                model_file = os.path.join(self.model_path, model_name)

            self.loaded_models[model_name] = self.llama_class(
                model_path=model_file,
                n_ctx=settings.llamacpp_n_ctx,
                n_gpu_layers=settings.llamacpp_n_gpu_layers,
                verbose=False
            )

        return self.loaded_models[model_name]

    async def list_models(self) -> List[str]:
        """List available GGUF models"""
        import os
        models = []

        if os.path.exists(self.model_path):
            for file in os.listdir(self.model_path):
                if file.endswith('.gguf'):
                    models.append(file.replace('.gguf', ''))

        return models

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a prompt string"""
        prompt_parts = []

        for msg in messages:
            role = msg.role
            content = msg.content

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate completion using llama.cpp"""

        llm = self._get_model(model)
        prompt = self._messages_to_prompt(messages)

        output = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop or [],
            echo=False
        )

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output["choices"][0]["text"]
                    },
                    "finish_reason": output["choices"][0]["finish_reason"]
                }
            ],
            "usage": {
                "prompt_tokens": output["usage"]["prompt_tokens"],
                "completion_tokens": output["usage"]["completion_tokens"],
                "total_tokens": output["usage"]["total_tokens"]
            }
        }

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming completion using llama.cpp"""

        llm = self._get_model(model)
        prompt = self._messages_to_prompt(messages)

        stream = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop or [],
            stream=True
        )

        for output in stream:
            chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": output["choices"][0]["text"]
                        },
                        "finish_reason": output["choices"][0].get("finish_reason")
                    }
                ]
            }
            yield json.dumps(chunk)

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Create embeddings using llama.cpp"""
        llm = self._get_model(model or settings.default_model)
        embeddings = []

        for text in texts:
            embedding = llm.embed(text)
            embeddings.append(embedding)

        return embeddings
