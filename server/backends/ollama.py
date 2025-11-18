"""
Ollama backend implementation
"""
import aiohttp
import json
import time
from typing import List, Dict, Any, AsyncIterator, Optional
from .base import BaseBackend
from ..config import settings


class OllamaBackend(BaseBackend):
    """Backend for Ollama (easiest for offline use)"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.session = None

    async def initialize(self) -> None:
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def list_models(self) -> List[str]:
        """List available models from Ollama"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as resp:
                data = await resp.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            return []

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate completion using Ollama"""

        # Convert messages to Ollama format
        payload = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            }
        }

        if stop:
            payload["options"]["stop"] = stop

        async with self.session.post(
            f"{self.base_url}/api/chat",
            json=payload
        ) as resp:
            data = await resp.json()

            # Convert to OpenAI format
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
                            "content": data["message"]["content"]
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
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
        """Generate streaming completion using Ollama"""

        payload = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            }
        }

        if stop:
            payload["options"]["stop"] = stop

        async with self.session.post(
            f"{self.base_url}/api/chat",
            json=payload
        ) as resp:
            async for line in resp.content:
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data:
                            # Convert to OpenAI streaming format
                            chunk = {
                                "id": f"chatcmpl-{int(time.time())}",
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": model,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {
                                            "content": data["message"].get("content", "")
                                        },
                                        "finish_reason": None
                                    }
                                ]
                            }
                            yield json.dumps(chunk)
                    except json.JSONDecodeError:
                        continue

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Create embeddings using Ollama"""
        embeddings = []

        for text in texts:
            payload = {
                "model": model or settings.default_model,
                "prompt": text
            }

            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as resp:
                data = await resp.json()
                embeddings.append(data["embedding"])

        return embeddings
