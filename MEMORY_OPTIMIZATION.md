# 메모리 최적화 가이드

## 리소스 요구사항 상세

### 1. 모델별 메모리 사용량

#### 소형 모델 (7B 파라미터)
- **디스크 용량**:
  - Q2: ~2 GB (품질 낮음, 비추천)
  - Q4: ~3.8 GB (권장 ⭐)
  - Q5: ~4.6 GB
  - Q8: ~7.2 GB (고품질)
  - FP16: ~14 GB (원본)

- **실행 메모리 (RAM)**:
  - Q4: 6-8 GB
  - Q8: 10-12 GB

#### 중형 모델 (13B 파라미터)
- **디스크**: 7-14 GB (양자화에 따라)
- **RAM**: 14-20 GB

#### 대형 모델 (30B+ 파라미터)
- **디스크**: 20-60 GB
- **RAM**: 32-64 GB
- GPU 거의 필수

### 2. 시스템별 권장 설정

#### 💻 저사양 (8GB RAM)
```yaml
# config.yaml
backend_type: "llamacpp"
default_model: "llama2-7b-q4"

llamacpp_n_ctx: 2048        # 컨텍스트 줄임
llamacpp_n_gpu_layers: 0    # CPU만 사용
```

**권장 모델**:
```bash
# 가장 작은 모델
ollama pull llama2:7b-chat-q4_0

# 디스크: ~3.8 GB
# 메모리: ~6 GB
# 속도: 느림 (5-10 토큰/초)
```

#### 🖥️ 중사양 (16GB RAM)
```yaml
backend_type: "ollama"
default_model: "llama2"

llamacpp_n_ctx: 4096
llamacpp_n_gpu_layers: 0
```

**권장 모델**:
```bash
ollama pull llama2:7b          # 일반 대화
ollama pull codellama:7b       # 코딩

# 총 디스크: ~8 GB
# 동시 실행 메모리: ~12 GB
# 속도: 보통 (10-20 토큰/초)
```

#### 🚀 고사양 (32GB RAM + GPU)
```yaml
backend_type: "vllm"  # 또는 ollama
default_model: "llama2"

llamacpp_n_ctx: 8192
llamacpp_n_gpu_layers: -1    # 전체 GPU 사용
```

**권장 모델**:
```bash
ollama pull llama2:13b
ollama pull codellama:13b
ollama pull mistral:7b

# 총 디스크: ~20 GB
# 메모리: 24+ GB
# 속도: 빠름 (40-60 토큰/초)
```

### 3. 메모리 절약 전략

#### A. 컨텍스트 크기 줄이기
```yaml
# config.yaml
llamacpp_n_ctx: 2048  # 기본 4096에서 줄임
```
- 메모리 사용량 ~40% 감소
- 긴 대화 기록 제한됨

#### B. CPU 전용 모드
```yaml
llamacpp_n_gpu_layers: 0  # GPU 사용 안 함
```
- VRAM 불필요
- 속도는 느림

#### C. 더 작은 양자화
```bash
# Q4 대신 Q2/Q3 사용 (비추천, 품질 저하)
ollama pull llama2:7b-chat-q3_K_S
```

#### D. 단일 모델만 로드
```yaml
# 한 번에 하나의 모델만 사용
default_model: "llama2"
```

### 4. 실전 최적화 설정 파일

#### 저사양 설정 (8GB RAM)
```yaml
# config-low-memory.yaml
host: "0.0.0.0"
port: 8000
workers: 1

backend_type: "llamacpp"
default_model: "llama2-7b-q4_0"

llamacpp_model_path: "./models"
llamacpp_n_ctx: 1024        # 매우 작은 컨텍스트
llamacpp_n_gpu_layers: 0
llamacpp_n_threads: 4       # CPU 쓰레드

model_cache_dir: "./cache"
```

#### GPU 가속 설정
```yaml
# config-gpu.yaml
backend_type: "ollama"
default_model: "codellama"

ollama_base_url: "http://localhost:11434"

# Ollama는 자동으로 GPU 감지
```

### 5. Docker 메모리 제한

#### docker-compose.yml (저사양)
```yaml
services:
  llm-serve:
    build: .
    deploy:
      resources:
        limits:
          memory: 6G        # 최대 6GB
        reservations:
          memory: 4G        # 최소 4GB
    environment:
      - LLM_BACKEND_TYPE=llamacpp
      - LLM_LLAMACPP_N_CTX=2048
```

### 6. 모델 다운로드 크기

```bash
# 다운로드 전 크기 확인
ollama show llama2:7b

# 각 모델 크기:
llama2:7b-chat-q4_0    → 3.8 GB
llama2:7b-chat-q4_K_M  → 4.1 GB
llama2:7b-chat-q5_K_M  → 4.7 GB
llama2:7b              → 3.8 GB (기본 Q4)
llama2:13b             → 7.4 GB

codellama:7b           → 3.8 GB
codellama:13b          → 7.4 GB

mistral:7b             → 4.1 GB
mixtral:8x7b           → 26 GB (!)
```

### 7. 런타임 메모리 모니터링

```bash
# 서버 실행 중 메모리 사용량 확인
docker stats llm-serve
docker stats llm-ollama

# 리눅스
htop
watch -n 1 free -h

# 로그에서 메모리 확인
docker-compose logs llm-serve | grep -i memory
```

### 8. 성능 vs 메모리 트레이드오프

| 설정 | 메모리 | 속도 | 품질 |
|------|--------|------|------|
| Q4 + ctx:1024 | 5 GB | 느림 | 중 |
| Q4 + ctx:2048 | 7 GB | 보통 | 중 |
| Q4 + ctx:4096 | 10 GB | 보통 | 좋음 |
| Q8 + ctx:4096 | 14 GB | 빠름 | 우수 |
| 13B Q4 + ctx:4096 | 18 GB | 느림 | 우수 |

### 9. 권장 사항 요약

#### 내 PC 사양이 이거라면?

**8GB RAM**
- ✅ Llama 2 7B Q4
- ✅ ctx: 2048
- ❌ 여러 모델 동시 실행 불가
- CPU 전용, 느림

**16GB RAM**
- ✅ Llama 2 7B + CodeLlama 7B (순차 실행)
- ✅ ctx: 4096
- ✅ 일반적인 작업 가능
- GPU 권장

**32GB RAM**
- ✅ 13B 모델 사용 가능
- ✅ 여러 모델 동시 로드
- ✅ ctx: 8192
- ✅ 프로덕션 레벨

**64GB RAM + GPU**
- ✅ 모든 모델
- ✅ 매우 빠른 응답
- ✅ 여러 사용자 동시 지원

### 10. 시작 추천

**처음 시작이라면**:
```bash
# 1. 가장 작은 모델로 시작
ollama pull llama2:7b

# 2. 메모리 사용량 확인
htop 또는 Activity Monitor

# 3. 괜찮으면 추가
ollama pull codellama:7b

# 4. 여유 있으면 13B 시도
ollama pull llama2:13b
```

### 11. 문제 발생 시

**"Out of memory" 에러**:
```yaml
# config.yaml
llamacpp_n_ctx: 1024  # 더 줄임
llamacpp_n_gpu_layers: 0
```

**너무 느림**:
```bash
# GPU 사용 확인
nvidia-smi

# GPU 레이어 활성화
llamacpp_n_gpu_layers: -1
```

**디스크 공간 부족**:
```bash
# 사용하지 않는 모델 삭제
ollama rm llama2:13b

# 캐시 정리
rm -rf model_cache/*
```

## 결론

**최소 시작 요구사항**:
- 디스크: 10 GB 여유 공간
- RAM: 8 GB
- 모델: Llama 2 7B Q4

**실용적 권장**:
- 디스크: 30 GB
- RAM: 16 GB
- GPU: 선택사항 (하지만 매우 권장)
- 모델: 7B 모델 2-3개

**비용**: $0 (완전 무료!)
