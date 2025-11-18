"""
vLLM backend implementation (for high-throughput serving)
"""
import json
import time
from typing import List, Dict, Any, AsyncIterator, Optional
from .base import BaseBackend
from ..config import settings


class VLLMBackend(BaseBackend):
    """Backend for vLLM high-performance serving"""

    def __init__(self):
        self.engine = None
        self.model_path = settings.vllm_model_path

    async def initialize(self) -> None:
        """Initialize vLLM engine"""
        try:
            from vllm import AsyncLLMEngine
            from vllm.engine.arg_utils import AsyncEngineArgs

            engine_args = AsyncEngineArgs(
                model=self.model_path,
                tensor_parallel_size=settings.vllm_tensor_parallel_size,
                dtype=settings.vllm_dtype,
            )

            self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        except ImportError:
            raise ImportError(
                "vLLM not installed. Install with: pip install vllm"
            )

    async def cleanup(self) -> None:
        """Cleanup vLLM engine"""
        if self.engine:
            # vLLM cleanup if needed
            pass

    async def list_models(self) -> List[str]:
        """List loaded model"""
        return [settings.vllm_model_path] if self.engine else []

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to prompt"""
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
        """Generate completion using vLLM"""
        from vllm import SamplingParams

        prompt = self._messages_to_prompt(messages)

        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop
        )

        request_id = f"chatcmpl-{int(time.time())}"

        # Generate
        results_generator = self.engine.generate(
            prompt,
            sampling_params,
            request_id
        )

        final_output = None
        async for request_output in results_generator:
            final_output = request_output

        text = final_output.outputs[0].text

        return {
            "id": request_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(text.split()),
                "total_tokens": len(prompt.split()) + len(text.split())
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
        """Generate streaming completion using vLLM"""
        from vllm import SamplingParams

        prompt = self._messages_to_prompt(messages)

        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop
        )

        request_id = f"chatcmpl-{int(time.time())}"

        results_generator = self.engine.generate(
            prompt,
            sampling_params,
            request_id
        )

        previous_text = ""
        async for request_output in results_generator:
            text = request_output.outputs[0].text
            delta = text[len(previous_text):]
            previous_text = text

            if delta:
                chunk = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": delta},
                            "finish_reason": None
                        }
                    ]
                }
                yield json.dumps(chunk)
