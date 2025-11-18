"""
Base backend interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional


class BaseBackend(ABC):
    """Abstract base class for LLM backends"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a completion"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion"""
        pass

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Create embeddings (optional, not all backends support this)"""
        raise NotImplementedError("Embeddings not supported by this backend")
