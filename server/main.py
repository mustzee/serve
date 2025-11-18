"""
Local LLM Serving API
Scalable, offline-capable LLM inference server
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import asyncio
import logging
from contextlib import asynccontextmanager

from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelInfo,
    HealthResponse
)
from .config import settings
from .backends import get_backend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backend instance
backend = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup backend on startup/shutdown"""
    global backend
    logger.info(f"Initializing backend: {settings.backend_type}")
    backend = get_backend(settings.backend_type)
    await backend.initialize()
    logger.info("Backend initialized successfully")
    yield
    logger.info("Shutting down backend")
    await backend.cleanup()


app = FastAPI(
    title="Local LLM Serve",
    description="Offline-capable, scalable LLM inference API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        backend=settings.backend_type,
        models_loaded=await backend.list_models()
    )


@app.get("/v1/models", response_model=List[ModelInfo])
async def list_models():
    """List available models"""
    try:
        models = await backend.list_models()
        return [
            ModelInfo(id=model, object="model", owned_by="local")
            for model in models
        ]
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """OpenAI-compatible chat completion endpoint"""
    try:
        if request.stream:
            async def generate():
                async for chunk in backend.generate_stream(
                    messages=request.messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    stop=request.stop
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            response = await backend.generate(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                stop=request.stop
            )
            return response
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/embeddings")
async def create_embeddings(
    input: List[str],
    model: Optional[str] = None
):
    """Create embeddings for text (if backend supports it)"""
    try:
        embeddings = await backend.create_embeddings(input, model)
        return {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": emb,
                    "index": i
                }
                for i, emb in enumerate(embeddings)
            ],
            "model": model or settings.default_model,
            "usage": {
                "prompt_tokens": sum(len(text.split()) for text in input),
                "total_tokens": sum(len(text.split()) for text in input)
            }
        }
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail="Embeddings not supported by this backend"
        )
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level="info"
    )
