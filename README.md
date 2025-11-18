# Local LLM Serve

**로컬 무료 LLM을 인터넷 연결 없이 확장성 높게 사용하는 프로젝트**

오프라인 환경에서 무료 LLM을 사용할 수 있는 확장 가능한 서빙 플랫폼입니다. 코딩 어시스턴트와 일상 로직 에이전트로 활용할 수 있습니다.

## 주요 특징

- **완전 오프라인**: 인터넷 연결 없이 로컬에서 실행
- **다중 백엔드 지원**: Ollama, llama.cpp, vLLM
- **OpenAI 호환 API**: 기존 OpenAI 클라이언트와 호환
- **확장 가능**: Docker Compose와 nginx 로드 밸런싱 지원
- **다중 언어 클라이언트**: Python, Go 클라이언트 라이브러리 제공
- **실전 예제**: 코딩 어시스턴트 및 일상 로직 에이전트

## 빠른 시작

### 1. Docker Compose로 실행 (권장)

```bash
# 저장소 클론
git clone https://github.com/mustzee/serve.git
cd serve

# Docker Compose로 실행
docker-compose up -d

# 서버 상태 확인
curl http://localhost:8000/health
```

### 2. 모델 다운로드 (Ollama 사용 시)

```bash
# Ollama 컨테이너에서 모델 다운로드
docker exec -it llm-ollama ollama pull llama2
docker exec -it llm-ollama ollama pull codellama

# 사용 가능한 모델 목록
curl http://localhost:8000/v1/models
```

### 3. 예제 실행

```bash
# Python 코딩 어시스턴트
python examples/coding_assistant.py

# Python 일상 로직 에이전트
python examples/daily_agent.py

# Go 코딩 어시스턴트
cd examples && go run coding_assistant.go
```

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    클라이언트 레이어                      │
│  Python Client  │  Go Client  │  직접 HTTP 호출         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  API 서버 (FastAPI)                      │
│  OpenAI 호환 엔드포인트 (/v1/chat/completions)          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    백엔드 레이어                         │
│  Ollama  │  llama.cpp  │  vLLM                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  LLM 모델 (로컬)                         │
│  Llama 2  │  CodeLlama  │  Mistral  │  기타...         │
└─────────────────────────────────────────────────────────┘
```

## 설치 방법

### Option 1: Docker (권장)

Docker와 Docker Compose만 있으면 됩니다:

```bash
docker-compose up -d
```

### Option 2: 로컬 설치

#### 서버 설치

```bash
# Python 의존성 설치
cd server
pip install -r requirements.txt

# Ollama 백엔드 사용 시
# Ollama를 별도로 설치: https://ollama.ai/

# llama.cpp 백엔드 사용 시
pip install llama-cpp-python

# vLLM 백엔드 사용 시 (고성능, GPU 권장)
pip install vllm

# 서버 실행
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
```

#### 클라이언트 설치

**Python:**
```bash
cd clients/python
pip install -r requirements.txt
```

**Go:**
```bash
cd clients/go
go mod download
```

## 설정

`config.yaml` 파일을 수정하여 설정을 변경할 수 있습니다:

```yaml
# 백엔드 선택
backend_type: "ollama"  # ollama, llamacpp, vllm

# 기본 모델
default_model: "llama2"

# Ollama 설정
ollama_base_url: "http://localhost:11434"

# llama.cpp 설정
llamacpp_model_path: "/models"
llamacpp_n_ctx: 4096
llamacpp_n_gpu_layers: 0  # GPU 사용 시 -1

# vLLM 설정 (고성능)
vllm_model_path: "/models/llama-2-7b"
vllm_tensor_parallel_size: 1
```

환경 변수로도 설정 가능:
```bash
export LLM_BACKEND_TYPE=ollama
export LLM_DEFAULT_MODEL=llama2
export LLM_OLLAMA_BASE_URL=http://localhost:11434
```

## 사용 예제

### Python 클라이언트

```python
from clients.python.client import LLMClient, Message

# 클라이언트 생성
client = LLMClient("http://localhost:8000")

# 간단한 완성
response = client.complete("Python에서 피보나치 수열을 구현하는 방법은?")
print(response)

# 채팅 (대화 형식)
messages = [
    Message(role="system", content="당신은 Python 전문가입니다."),
    Message(role="user", content="리스트 컴프리헨션을 설명해주세요.")
]
response = client.chat(messages=messages, model="llama2")
print(response['choices'][0]['message']['content'])

# 스트리밍
for chunk in client.chat(messages=messages, stream=True):
    print(chunk, end="", flush=True)
```

### Go 클라이언트

```go
package main

import (
    "context"
    "fmt"
    llmclient "github.com/mustzee/serve/clients/go"
)

func main() {
    client := llmclient.NewClient("http://localhost:8000")
    ctx := context.Background()

    // 간단한 완성
    response, err := client.Complete(
        ctx,
        "Go에서 고루틴을 사용하는 방법은?",
        "llama2",
        0.7,
        2048,
    )
    if err != nil {
        panic(err)
    }
    fmt.Println(response)

    // 스트리밍
    req := &llmclient.ChatCompletionRequest{
        Model: "llama2",
        Messages: []llmclient.Message{
            {Role: "user", Content: "채널에 대해 설명해주세요."},
        },
        Temperature: 0.7,
    }

    contentChan, errorChan := client.StreamChat(ctx, req)
    for content := range contentChan {
        fmt.Print(content)
    }
    if err := <-errorChan; err != nil {
        panic(err)
    }
}
```

### cURL로 직접 호출

```bash
# 채팅 완성
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "안녕하세요!"}
    ],
    "temperature": 0.7
  }'

# 스트리밍
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "Python으로 웹 서버 만드는 법"}
    ],
    "stream": true
  }'
```

## 백엔드 비교

| 백엔드 | 설치 난이도 | 성능 | 오프라인 | GPU 지원 | 추천 용도 |
|--------|-------------|------|----------|----------|----------|
| **Ollama** | ⭐ 쉬움 | 중 | ✅ | ✅ | 일반 사용, 빠른 시작 |
| **llama.cpp** | ⭐⭐ 보통 | 중-고 | ✅ | ✅ | 커스터마이징, 저메모리 |
| **vLLM** | ⭐⭐⭐ 어려움 | 매우 높음 | ✅ | ✅ 필수 | 고성능, 프로덕션 |

### Ollama (권장)
- 가장 쉬운 설치 및 사용
- 자동 모델 다운로드 관리
- CPU/GPU 자동 감지
- 완전 오프라인 작동

### llama.cpp
- 경량 C++ 구현
- 낮은 메모리 사용량
- GGUF 모델 형식 지원
- 세밀한 설정 가능

### vLLM
- 최고 성능 (PagedAttention)
- GPU 필수
- 높은 처리량 (throughput)
- 프로덕션 환경 적합

## 권장 모델

### 코딩 작업
- **CodeLlama 7B/13B**: 코드 생성 및 이해
- **Phind CodeLlama 34B**: 더 높은 품질 (더 많은 리소스 필요)
- **DeepSeek Coder**: 다국어 코드 지원

### 일반 대화 및 추론
- **Llama 2 7B/13B**: 균형잡힌 성능
- **Mistral 7B**: 우수한 추론 능력
- **Mixtral 8x7B**: 고품질 응답 (더 많은 리소스 필요)

### 다운로드 (Ollama 사용 시)
```bash
# 코딩
ollama pull codellama:7b
ollama pull codellama:13b

# 일반
ollama pull llama2:7b
ollama pull mistral:7b
```

## 확장성

### 수평 확장 (Multiple Servers)

`docker-compose.yml` 수정:

```yaml
services:
  llm-serve-1:
    build: .
    # ... 설정 ...

  llm-serve-2:
    build: .
    # ... 설정 ...

  llm-serve-3:
    build: .
    # ... 설정 ...

  nginx:
    # nginx.conf에서 모든 서버를 업스트림에 추가
```

`nginx.conf` 업데이트:
```nginx
upstream llm_backend {
    server llm-serve-1:8000;
    server llm-serve-2:8000;
    server llm-serve-3:8000;
}
```

### 로드 밸런싱 전략

nginx를 사용한 다양한 로드 밸런싱:

```nginx
# 라운드 로빈 (기본)
upstream llm_backend {
    server llm-serve-1:8000;
    server llm-serve-2:8000;
}

# 최소 연결
upstream llm_backend {
    least_conn;
    server llm-serve-1:8000;
    server llm-serve-2:8000;
}

# IP 해시 (세션 유지)
upstream llm_backend {
    ip_hash;
    server llm-serve-1:8000;
    server llm-serve-2:8000;
}
```

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 주요 엔드포인트

- `GET /health` - 서버 상태 확인
- `GET /v1/models` - 사용 가능한 모델 목록
- `POST /v1/chat/completions` - 채팅 완성 (OpenAI 호환)
- `POST /v1/embeddings` - 텍스트 임베딩 생성

## 예제 애플리케이션

### 1. 코딩 어시스턴트 (`examples/coding_assistant.py`)

```bash
python examples/coding_assistant.py
```

기능:
- 코드 생성
- 코드 리뷰
- 디버깅 도움
- 코드 설명
- 대화형 코딩 도우미

### 2. 일상 로직 에이전트 (`examples/daily_agent.py`)

```bash
python examples/daily_agent.py
```

기능:
- 논리적 추론 및 문제 해결
- 일정 계획 및 우선순위 지정
- 의사결정 분석
- 주제 연구 및 설명
- 대화형 어시스턴트 모드

## 문제 해결

### 서버가 시작되지 않음

```bash
# 로그 확인
docker-compose logs llm-serve

# 포트 충돌 확인
lsof -i :8000
```

### Ollama 연결 실패

```bash
# Ollama 상태 확인
docker-compose logs ollama

# Ollama API 테스트
curl http://localhost:11434/api/tags
```

### 모델 메모리 부족

- 더 작은 모델 사용 (예: 7B 대신 7B)
- GPU 레이어 수 줄이기 (`n_gpu_layers`)
- 컨텍스트 크기 줄이기 (`n_ctx`)

```yaml
# config.yaml
llamacpp_n_ctx: 2048  # 4096에서 감소
llamacpp_n_gpu_layers: 0  # CPU만 사용
```

### 느린 응답 속도

1. GPU 사용 활성화
2. 더 작은 모델 사용
3. 양자화된 모델 사용 (예: Q4_K_M)
4. vLLM 백엔드로 전환 (고성능)

## 개발

### 프로젝트 구조

```
serve/
├── server/              # FastAPI 서버
│   ├── main.py         # 메인 애플리케이션
│   ├── models.py       # Pydantic 모델
│   ├── config.py       # 설정 관리
│   └── backends/       # LLM 백엔드 구현
│       ├── base.py
│       ├── ollama.py
│       ├── llamacpp.py
│       └── vllm.py
├── clients/            # 클라이언트 라이브러리
│   ├── python/         # Python 클라이언트
│   └── go/             # Go 클라이언트
├── examples/           # 예제 애플리케이션
├── docker/             # Docker 설정
└── config.yaml         # 설정 파일
```

### 새 백엔드 추가

1. `server/backends/`에 새 백엔드 클래스 생성
2. `BaseBackend` 상속 및 메서드 구현
3. `server/backends/__init__.py`의 팩토리에 추가

```python
from .base import BaseBackend

class MyBackend(BaseBackend):
    async def initialize(self):
        # 초기화 로직
        pass

    async def generate(self, messages, model, **kwargs):
        # 생성 로직
        pass
```

## 기여

기여를 환영합니다! Pull Request를 보내주세요.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이선스

MIT License

## 관련 프로젝트

- [Ollama](https://ollama.ai/) - 로컬 LLM 실행 도구
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - C++ LLM 추론
- [vLLM](https://github.com/vllm-project/vllm) - 고성능 LLM 서빙
- [FastAPI](https://fastapi.tiangolo.com/) - 현대적인 Python 웹 프레임워크

## 지원

문제가 있으시면 GitHub Issues에 올려주세요.

---

**Made with ❤️ for offline LLM enthusiasts**
