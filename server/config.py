"""
Configuration management
"""
from pydantic_settings import BaseSettings
from typing import List
import yaml
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    cors_origins: List[str] = ["*"]

    # Backend configuration
    backend_type: str = "ollama"  # ollama, llamacpp, vllm
    default_model: str = "llama2"

    # Ollama backend settings
    ollama_base_url: str = "http://localhost:11434"

    # llama.cpp backend settings
    llamacpp_model_path: str = "/models"
    llamacpp_n_ctx: int = 4096
    llamacpp_n_gpu_layers: int = 0

    # vLLM backend settings
    vllm_model_path: str = "/models"
    vllm_tensor_parallel_size: int = 1
    vllm_dtype: str = "auto"

    # Model cache
    model_cache_dir: str = "./model_cache"

    class Config:
        env_prefix = "LLM_"
        env_file = ".env"


def load_config(config_path: str = "config.yaml") -> Settings:
    """Load configuration from YAML file"""
    config_file = Path(config_path)

    if config_file.exists():
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
            return Settings(**config_data)

    return Settings()


settings = load_config()
