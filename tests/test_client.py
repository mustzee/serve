"""
간단한 통합 테스트
"""
import pytest
import time
from clients.python.client import LLMClient, Message


def test_client_creation():
    """클라이언트 생성 테스트"""
    client = LLMClient("http://localhost:8000")
    assert client.base_url == "http://localhost:8000"


def test_message_creation():
    """메시지 생성 테스트"""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_health_endpoint():
    """Health 엔드포인트 테스트 (서버 실행 필요)"""
    client = LLMClient("http://localhost:8000")

    try:
        health = client.health()
        assert "status" in health
        assert "backend" in health
    except Exception as e:
        pytest.skip(f"Server not running: {e}")


def test_list_models():
    """모델 목록 테스트 (서버 실행 필요)"""
    client = LLMClient("http://localhost:8000")

    try:
        models = client.list_models()
        assert isinstance(models, list)
    except Exception as e:
        pytest.skip(f"Server not running: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
