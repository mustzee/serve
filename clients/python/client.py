"""
Python client for Local LLM Serve API
"""
import requests
import json
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass


@dataclass
class Message:
    """Chat message"""
    role: str  # system, user, assistant
    content: str


class LLMClient:
    """Client for interacting with Local LLM Serve"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client

        Args:
            base_url: Base URL of the LLM server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def health(self) -> Dict[str, Any]:
        """Check server health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def list_models(self) -> List[str]:
        """List available models"""
        response = self.session.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        models = response.json()
        return [model["id"] for model in models]

    def chat(
        self,
        messages: List[Message],
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Any:
        """
        Send chat completion request

        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Response dict or iterator for streaming
        """
        payload = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        if stream:
            return self._stream_chat(payload)
        else:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    def _stream_chat(self, payload: Dict) -> Iterator[str]:
        """Stream chat response"""
        response = self.session.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    def complete(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Simple completion method

        Args:
            prompt: The prompt text
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Completion text
        """
        messages = [Message(role="user", content=prompt)]
        response = self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']

    def embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Create embeddings for texts

        Args:
            texts: List of texts to embed
            model: Model to use (optional)

        Returns:
            List of embedding vectors
        """
        payload = {
            "input": texts,
            "model": model
        }

        response = self.session.post(
            f"{self.base_url}/v1/embeddings",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]


# Convenience function
def create_client(base_url: str = "http://localhost:8000") -> LLMClient:
    """Create a new LLM client"""
    return LLMClient(base_url)
