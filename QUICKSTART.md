# 빠른 시작 가이드

## 5분 안에 시작하기

### 1. 서비스 시작

```bash
# 설정 스크립트 실행
chmod +x setup.sh
./setup.sh

# 또는 직접:
docker-compose up -d
```

### 2. 모델 다운로드

```bash
# Llama 2 (일반 대화)
docker exec -it llm-ollama ollama pull llama2

# CodeLlama (코딩)
docker exec -it llm-ollama ollama pull codellama
```

### 3. 테스트

```bash
# API 테스트
curl http://localhost:8000/health

# 채팅 테스트
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "안녕하세요!"}
    ]
  }'
```

### 4. 예제 실행

```bash
# Python 클라이언트 설치
pip install requests

# 코딩 어시스턴트 실행
python examples/coding_assistant.py

# 일상 에이전트 실행
python examples/daily_agent.py
```

## 일반적인 사용 사례

### 코드 생성

```python
from clients.python.client import LLMClient

client = LLMClient("http://localhost:8000")
code = client.complete(
    "Python으로 이진 탐색 트리를 구현해줘",
    model="codellama"
)
print(code)
```

### 코드 리뷰

```python
code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total
"""

review = client.complete(
    f"다음 코드를 리뷰해줘:\n{code}",
    model="codellama"
)
print(review)
```

### 논리 추론

```python
problem = "3명이 사과를 똑같이 나눠 먹는데, 사과가 10개 있다면 몇 개씩 먹을 수 있을까?"

answer = client.complete(problem, model="llama2")
print(answer)
```

### 일정 계획

```python
tasks = """
오늘 해야 할 일:
1. 프로젝트 보고서 작성 (2시간)
2. 팀 미팅 참석 (오후 2시, 1시간)
3. 코드 리뷰 (1.5시간)
4. 운동 (1시간)

최적의 일정을 계획해줘.
"""

plan = client.complete(tasks, model="llama2")
print(plan)
```

## Go로 사용하기

```go
package main

import (
    "context"
    "fmt"
    llmclient "github.com/mustzee/serve/clients/go"
)

func main() {
    client := llmclient.NewClient("http://localhost:8000")

    response, err := client.Complete(
        context.Background(),
        "Go로 웹 서버 만드는 법을 알려줘",
        "codellama",
        0.7,
        2048,
    )

    if err != nil {
        panic(err)
    }

    fmt.Println(response)
}
```

## 문제 해결

### "Connection refused" 오류

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs llm-serve
docker-compose logs ollama

# 재시작
docker-compose restart
```

### 모델이 느림

1. GPU 사용 확인:
```bash
# nvidia-docker가 설치되어 있다면
docker-compose.yml에서 GPU 설정 주석 해제
```

2. 더 작은 모델 사용:
```bash
# 7B 모델 대신 더 작은 모델
ollama pull llama2:7b-chat-q4_0
```

### 메모리 부족

```bash
# config.yaml 수정
llamacpp_n_ctx: 2048  # 컨텍스트 크기 감소
```

## 다음 단계

- [전체 문서 읽기](README.md)
- [API 문서 확인](http://localhost:8000/docs)
- 예제 코드 살펴보기
- 자신만의 에이전트 만들기

## 도움이 필요하신가요?

- GitHub Issues에 질문 올리기
- README.md의 상세 문서 참조
