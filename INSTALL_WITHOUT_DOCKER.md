# Docker 없이 설치하기

Docker를 사용하지 않고 로컬에 직접 설치하는 방법입니다. 오히려 더 간단하고 빠릅니다!

## 🎯 가장 쉬운 방법: Ollama만 사용

### 1단계: Ollama 설치 (1분)

#### macOS / Linux
```bash
# 한 줄로 설치
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
1. https://ollama.ai/download 방문
2. Windows용 설치 프로그램 다운로드
3. 실행하고 설치

### 2단계: 모델 다운로드

```bash
# 일반 대화용
ollama pull llama2

# 코딩용
ollama pull codellama
```

### 3단계: 바로 사용!

```bash
# 대화 시작
ollama run llama2

# 코딩 도움
ollama run codellama
```

**끝! 이게 전부입니다!** 🎉

---

## 📚 Python/Go 클라이언트 사용하려면?

Ollama는 자체 API를 제공하므로, 이 프로젝트의 서버 없이도 바로 사용 가능합니다.

### Python으로 바로 사용

```bash
# Python 클라이언트 라이브러리 설치
pip install ollama
```

```python
import ollama

# 간단한 대화
response = ollama.chat(model='llama2', messages=[
  {
    'role': 'user',
    'content': 'Python으로 피보나치 수열 만드는 법?',
  },
])
print(response['message']['content'])

# 스트리밍
for chunk in ollama.chat(
    model='codellama',
    messages=[{'role': 'user', 'content': '웹 서버 만들기'}],
    stream=True,
):
  print(chunk['message']['content'], end='', flush=True)
```

### Go로 바로 사용

```bash
go get github.com/ollama/ollama/api
```

```go
package main

import (
    "context"
    "fmt"
    "github.com/ollama/ollama/api"
)

func main() {
    client, _ := api.ClientFromEnvironment()

    req := &api.ChatRequest{
        Model: "llama2",
        Messages: []api.Message{
            {Role: "user", Content: "안녕하세요!"},
        },
    }

    client.Chat(context.Background(), req, func(resp api.ChatResponse) error {
        fmt.Print(resp.Message.Content)
        return nil
    })
}
```

---

## 🔧 이 프로젝트의 서버도 사용하려면?

OpenAI 호환 API가 필요한 경우에만 서버를 실행하면 됩니다.

### Python 서버 로컬 실행

```bash
# 1. Python 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
cd server
pip install -r requirements.txt

# 3. Ollama가 실행 중인지 확인
ollama list

# 4. 서버 실행
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000

# 또는 간단히
cd ..
python -m server.main
```

### 백그라운드에서 실행

```bash
# Linux/macOS
nohup python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 &

# Windows (PowerShell)
Start-Process python -ArgumentList "-m","uvicorn","server.main:app","--host","0.0.0.0","--port","8000" -WindowStyle Hidden
```

---

## 🎮 llama.cpp 직접 사용 (최고 성능)

더 세밀한 제어가 필요하다면 llama.cpp를 직접 사용할 수 있습니다.

### 설치

```bash
# 1. llama.cpp 클론
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# 2. 빌드
make

# GPU 가속 (NVIDIA)
make LLAMA_CUBLAS=1

# macOS (Metal 가속)
make LLAMA_METAL=1
```

### 모델 다운로드

```bash
# Hugging Face에서 GGUF 모델 다운로드
# 예: https://huggingface.co/TheBloke/Llama-2-7B-GGUF

mkdir models
cd models
wget https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf
```

### 실행

```bash
# 대화형 모드
./main -m models/llama-2-7b.Q4_K_M.gguf --color -i

# 서버 모드
./server -m models/llama-2-7b.Q4_K_M.gguf --host 0.0.0.0 --port 8080
```

### Python에서 사용

```bash
pip install llama-cpp-python
```

```python
from llama_cpp import Llama

llm = Llama(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    n_ctx=2048,
    n_gpu_layers=-1  # GPU 사용
)

output = llm(
    "Python으로 웹 서버 만드는 법?",
    max_tokens=512,
    temperature=0.7,
)
print(output['choices'][0]['text'])
```

---

## 📊 방법 비교

| 방법 | 설치 난이도 | 성능 | 사용성 | 추천 |
|------|-------------|------|--------|------|
| **Ollama** | ⭐ 매우 쉬움 | 좋음 | 최고 | ✅ 초보자 |
| **Ollama + 이 프로젝트 서버** | ⭐⭐ 쉬움 | 좋음 | 높음 | OpenAI API 필요시 |
| **llama.cpp** | ⭐⭐⭐ 보통 | 최고 | 보통 | 고급 사용자 |
| **Docker** | ⭐⭐ 쉬움 | 좋음 | 높음 | 배포/격리 필요시 |

---

## 🎯 추천 방법

### 처음 시작이라면
```bash
# Ollama만 설치하고 바로 사용
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
ollama run llama2
```

### OpenAI API 호환성이 필요하면
```bash
# Ollama + 이 프로젝트 서버
ollama pull llama2
cd server && pip install -r requirements.txt
python -m uvicorn server.main:app --port 8000
```

### 최고 성능이 필요하면
```bash
# llama.cpp 직접 사용
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make LLAMA_CUBLAS=1
./server -m models/your-model.gguf
```

---

## ⚡ 빠른 시작 스크립트

로컬 설치를 위한 스크립트를 만들었습니다:

```bash
./setup_local.sh
```

이 스크립트가 자동으로:
1. Ollama 설치 확인/설치
2. Python 환경 설정
3. 의존성 설치
4. 모델 다운로드 안내

---

## 🤔 Docker vs 로컬, 언제 뭘 쓸까?

### Docker를 쓰면 좋은 경우
- ✅ 여러 사람과 공유/배포
- ✅ 프로덕션 환경
- ✅ 격리된 환경 필요
- ✅ 여러 버전 관리

### 로컬 설치가 좋은 경우
- ✅ 개인 사용
- ✅ 빠른 시작
- ✅ 최대 성능 필요
- ✅ 간단한 설정
- ✅ Docker 설치 안 됨/싫음

---

## 💡 결론

**추천: Ollama 로컬 설치**

가장 간단하고, 빠르고, 관리하기 쉽습니다. Docker는 필요 없습니다!

```bash
# macOS/Linux 한 줄 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull llama2
ollama pull codellama

# 바로 사용
ollama run codellama "Python으로 웹 서버 만드는 법?"
```

**이게 전부입니다!** 🚀
