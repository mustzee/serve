# 문제 해결 가이드

프로젝트 사용 중 발생할 수 있는 문제와 해결 방법을 정리했습니다.

## 🔧 일반적인 문제

### 1. "Connection refused" 오류

**증상:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**원인:** Ollama 서비스가 실행되지 않음

**해결:**
```bash
# Ollama 서비스 시작
ollama serve

# 백그라운드 실행
nohup ollama serve > /dev/null 2>&1 &

# macOS (앱 실행)
open -a Ollama
```

---

### 2. "Model not found" 오류

**증상:**
```
Error: model 'llama2' not found
```

**원인:** 모델이 다운로드되지 않음

**해결:**
```bash
# 모델 다운로드
ollama pull llama2

# 설치된 모델 확인
ollama list

# 모델이 없으면 다운로드
ollama pull qwen2.5:7b
ollama pull codellama:7b
```

---

### 3. "Out of memory" 오류

**증상:**
```
RuntimeError: CUDA out of memory
또는
killed (메모리 부족으로 프로세스 종료)
```

**원인:** 시스템 메모리 부족

**해결:**

**방법 1: 더 작은 모델 사용**
```bash
# 7B 모델 사용
ollama pull llama2:7b

# 양자화 버전 사용
ollama pull llama2:7b-chat-q4_0
```

**방법 2: 설정 조정 (config.yaml)**
```yaml
llamacpp_n_ctx: 2048     # 4096에서 줄임
llamacpp_n_gpu_layers: 0 # GPU 사용 안 함
```

**방법 3: 저사양 설정 사용**
```bash
cp config-low-memory.yaml config.yaml
```

---

### 4. 서버가 시작되지 않음

**증상:**
```
Error starting server
```

**진단:**
```bash
# 1. Python 패키지 확인
pip list | grep fastapi

# 2. 포트 사용 확인
lsof -i :8000
netstat -an | grep 8000

# 3. 로그 확인
python -m uvicorn server.main:app --log-level debug
```

**해결:**

**패키지 없음:**
```bash
pip install -r server/requirements.txt
```

**포트 사용 중:**
```bash
# 다른 포트 사용
python -m uvicorn server.main:app --port 8001

# 또는 기존 프로세스 종료
kill $(lsof -t -i:8000)
```

---

### 5. Docker 관련 문제

**증상:** Docker 컨테이너가 시작되지 않음

**진단:**
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs llm-serve
docker-compose logs ollama
```

**해결:**

**컨테이너 재시작:**
```bash
docker-compose down
docker-compose up -d
```

**이미지 재빌드:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**권한 문제:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### 6. 느린 응답 속도

**증상:** 응답이 매우 느림 (30초 이상)

**원인:** CPU 전용 실행, 큰 모델, 높은 컨텍스트

**해결:**

**방법 1: GPU 사용**
```yaml
# config.yaml
llamacpp_n_gpu_layers: -1  # 모든 레이어 GPU로
```

**방법 2: 더 작은 모델**
```bash
# 13B → 7B로 변경
ollama pull llama2:7b
```

**방법 3: 설정 최적화**
```yaml
llamacpp_n_ctx: 2048       # 컨텍스트 줄임
llamacpp_n_threads: 8      # CPU 쓰레드 늘림
```

---

### 7. Python import 오류

**증상:**
```
ModuleNotFoundError: No module named 'server'
```

**원인:** Python 경로 문제

**해결:**
```bash
# 프로젝트 루트에서 실행
cd /path/to/serve

# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 또는 패키지로 실행
python -m server.main
```

---

### 8. Ollama API 타임아웃

**증상:**
```
TimeoutError: Request timed out
```

**원인:** 모델 로딩 시간이 길거나 응답 생성이 느림

**해결:**

**타임아웃 늘리기:**
```python
# clients/python/client.py
response = self.session.post(
    url,
    json=payload,
    timeout=120  # 60에서 120으로 늘림
)
```

**첫 요청은 느릴 수 있음:**
```bash
# 모델 미리 로드
ollama run llama2 ""  # 빈 프롬프트로 로드만
```

---

### 9. GPU가 인식되지 않음

**증상:** GPU가 있는데 CPU로만 실행됨

**진단:**
```bash
# NVIDIA GPU 확인
nvidia-smi

# CUDA 확인
nvcc --version
```

**해결:**

**Ollama (자동):**
```bash
# Ollama는 자동으로 GPU 감지
# 로그에서 확인
ollama run llama2 --verbose
```

**llama.cpp:**
```bash
# GPU 버전으로 재설치
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

**Docker:**
```yaml
# docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

### 10. 설정 파일이 적용되지 않음

**증상:** config.yaml 수정했는데 변경 안 됨

**원인:** 환경 변수가 우선순위 높음, 또는 캐시

**해결:**

**환경 변수 확인:**
```bash
# 환경 변수가 설정 파일보다 우선
env | grep LLM_

# 환경 변수 제거
unset LLM_BACKEND_TYPE
```

**서버 재시작:**
```bash
# 프로세스 종료 후 재시작
pkill -f "uvicorn server.main"
python -m uvicorn server.main:app
```

---

## 🐛 디버깅 팁

### 로그 레벨 높이기

```bash
# 상세 로그
python -m uvicorn server.main:app --log-level debug

# Python 로깅
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 단계별 테스트

```bash
# 1. Ollama 테스트
curl http://localhost:11434/api/tags

# 2. 서버 health check
curl http://localhost:8000/health

# 3. 간단한 요청
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama2","messages":[{"role":"user","content":"hi"}]}'
```

### 검증 스크립트 실행

```bash
# 전체 프로젝트 검증
python verify_project.py
```

---

## 📱 플랫폼별 문제

### macOS

**문제:** Ollama 서비스 시작 안 됨
```bash
# 해결: 앱으로 실행
open -a Ollama

# 또는 brew로 재설치
brew reinstall ollama
```

**문제:** 권한 오류
```bash
# 해결: 권한 부여
chmod +x setup_local.sh
xattr -d com.apple.quarantine setup_local.sh
```

---

### Linux

**문제:** systemd 서비스 설정
```bash
# Ollama를 systemd 서비스로
sudo systemctl enable ollama
sudo systemctl start ollama
```

**문제:** 방화벽
```bash
# 포트 열기
sudo ufw allow 8000/tcp
sudo ufw allow 11434/tcp
```

---

### Windows

**문제:** PowerShell 실행 정책
```powershell
# 해결: 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**문제:** 경로 문제
```powershell
# Windows 경로 사용
python -m uvicorn server.main:app --host 0.0.0.0
```

---

## 🆘 여전히 문제가 해결되지 않는다면

### 1. 로그 수집

```bash
# 시스템 정보
python check_requirements.py > system_info.txt

# 서버 로그
python -m uvicorn server.main:app --log-level debug > server.log 2>&1

# Ollama 로그
ollama list >> system_info.txt
```

### 2. 이슈 리포트

다음 정보와 함께 GitHub Issues에 올려주세요:
- 운영체제 및 버전
- Python 버전
- 실행한 명령어
- 에러 메시지 전문
- system_info.txt
- server.log (관련 부분)

### 3. 커뮤니티 도움

- Ollama Discord: https://discord.gg/ollama
- Ollama GitHub: https://github.com/ollama/ollama/issues

---

## ✅ 체크리스트

문제가 발생하면 다음을 순서대로 확인하세요:

- [ ] Ollama 설치되어 있는가?
- [ ] Ollama 서비스 실행 중인가? (`ollama list`)
- [ ] 모델이 다운로드되어 있는가?
- [ ] Python 패키지가 설치되어 있는가?
- [ ] 포트가 사용 가능한가? (8000, 11434)
- [ ] 메모리가 충분한가? (최소 8GB)
- [ ] 디스크 공간이 충분한가? (최소 10GB)
- [ ] 방화벽이 포트를 차단하지 않는가?
- [ ] 올바른 디렉토리에서 실행하는가?

모두 확인했다면 `verify_project.py`를 실행하세요!
