# 오프라인 모드 완벽 가이드

## 🔌 핵심 답변

**Ollama는 모델 다운로드 후 완전 오프라인으로 작동합니다.**

---

## 📋 단계별 네트워크 요구사항

### 1단계: 설치 (인터넷 필요 ⚠️)

```bash
# Ollama 설치
curl -fsSL https://ollama.ai/install.sh | sh
```
- **인터넷 필요**: ✅ Yes
- **이유**: Ollama 프로그램 다운로드
- **크기**: ~수백 MB
- **횟수**: 단 한 번

### 2단계: 모델 다운로드 (인터넷 필요 ⚠️)

```bash
# 원하는 모델 다운로드
ollama pull llama2        # 3.8 GB
ollama pull codellama     # 3.8 GB
ollama pull mistral       # 4.1 GB
```
- **인터넷 필요**: ✅ Yes
- **이유**: 모델 파일 다운로드
- **크기**: 모델당 3-7 GB
- **횟수**: 모델당 한 번

### 3단계: 사용 (인터넷 불필요 🎉)

```bash
# 오프라인에서 사용
ollama run llama2
```
- **인터넷 필요**: ❌ No
- **완전 오프라인**: ✅ Yes
- **영구적**: ✅ Yes

---

## 🌐 오프라인 시나리오

### ✅ 완전히 가능한 것들

```bash
# WiFi 꺼도 됨
# 비행기 모드 켜도 됨
# 이더넷 뽑아도 됨
# 인터넷 없는 산 속에서도 가능

ollama run llama2 "코드 작성해줘"
ollama run codellama "버그 찾아줘"

# Python에서
import ollama
ollama.chat(model='llama2', messages=[...])

# 이 프로젝트의 서버
python -m uvicorn server.main:app --port 8000
```

**모두 오프라인에서 100% 작동합니다!**

### ❌ 불가능한 것

```bash
# 새 모델 다운로드
ollama pull new-model  # ← 인터넷 필요

# 모델 업데이트
ollama pull llama2  # ← 이미 있어도 업데이트 시 인터넷 필요
```

---

## 📦 모델 파일은 어디에 저장될까?

Ollama는 모델을 로컬에 저장합니다:

### macOS
```
~/.ollama/models/
```

### Linux
```
/usr/share/ollama/.ollama/models/
또는
~/.ollama/models/
```

### Windows
```
C:\Users\<username>\.ollama\models\
```

### 확인 방법
```bash
# 다운로드된 모델 목록
ollama list

# 출력 예시:
# NAME              ID           SIZE    MODIFIED
# llama2:latest     78e26419b446 3.8 GB  2 hours ago
# codellama:latest  8fdf8f752f6e 3.8 GB  1 day ago
```

---

## 🧪 오프라인 테스트 방법

### 방법 1: 자동 테스트 스크립트

```bash
chmod +x test_offline.sh
./test_offline.sh
```

이 스크립트가:
1. Ollama 설치 확인
2. 모델 다운로드 확인
3. 네트워크 상태 확인
4. 오프라인에서 실제 질문/응답 테스트

### 방법 2: 수동 테스트

```bash
# 1. 모델 다운로드 (인터넷 연결 시)
ollama pull llama2

# 2. WiFi/네트워크 끄기
#    - macOS: WiFi 아이콘 → 끄기
#    - Windows: 비행기 모드 켜기
#    - Linux: nmcli radio wifi off

# 3. 오프라인 상태에서 테스트
ollama run llama2 "1+1은?"

# 4. 작동하면 성공! ✅
```

### 방법 3: Python 테스트

```python
import ollama
import socket

# 네트워크 상태 확인
def is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True
    except OSError:
        return False

print(f"인터넷 연결: {is_online()}")

# 오프라인 상태에서도 작동
response = ollama.chat(model='llama2', messages=[
    {'role': 'user', 'content': '안녕하세요!'}
])

print(f"응답: {response['message']['content']}")
print("\n✅ 오프라인에서 정상 작동!")
```

---

## 🚀 오프라인 환경 준비 체크리스트

인터넷 없는 환경에 가기 전:

### 필수 단계
- [ ] Ollama 설치
- [ ] 필요한 모델 다운로드
  - [ ] llama2 (일반 대화)
  - [ ] codellama (코딩)
  - [ ] 기타 필요한 모델
- [ ] 오프라인 테스트 완료

### 선택 단계 (이 프로젝트 사용 시)
- [ ] Python 의존성 설치
- [ ] 예제 코드 다운로드
- [ ] 서버 설정 완료
- [ ] Go 클라이언트 빌드 (Go 사용 시)

---

## 💾 오프라인 백업/이동

### 다른 PC로 모델 이동

```bash
# PC A (인터넷 있음)에서 모델 다운로드
ollama pull llama2

# 모델 파일 복사
# macOS/Linux
tar -czf ollama-models.tar.gz ~/.ollama/models/

# PC B (인터넷 없음)로 파일 전송
# USB, 외장하드 등 사용

# PC B에서 압축 해제
tar -xzf ollama-models.tar.gz -C ~/

# Ollama 설치 (오프라인 설치 프로그램 사용)
# 바로 사용 가능!
ollama run llama2
```

### Docker 이미지로 백업

```bash
# 인터넷 있는 곳에서
docker pull ollama/ollama
docker save ollama/ollama > ollama-image.tar

# 오프라인 환경으로 이동
docker load < ollama-image.tar

# 모델도 포함한 커스텀 이미지
docker commit llm-ollama my-ollama-with-models
docker save my-ollama-with-models > my-ollama.tar
```

---

## 🌍 실전 시나리오

### 시나리오 1: 비행기에서 코딩
```
✅ 가능!
- 비행기 모드 ON
- 노트북만 있으면 됨
- Ollama로 코드 작성/리뷰
```

### 시나리오 2: 산속 오두막
```
✅ 가능!
- 인터넷 없음
- 전기만 있으면 됨
- 모든 기능 사용 가능
```

### 시나리오 3: 회사 내부망
```
✅ 가능!
- 인터넷 차단된 보안 구역
- 모델을 미리 다운로드
- 내부에서 자유롭게 사용
```

### 시나리오 4: 개발도상국 출장
```
✅ 가능!
- 불안정한 인터넷
- 미리 모델 준비
- 오프라인으로 작업
```

---

## 📊 데이터 사용량 비교

### 온라인 AI 서비스 (ChatGPT, Claude 등)
- **모델 다운로드**: 불필요
- **사용 시 데이터**: 매번 인터넷 필요
- **월 사용량**: 수 GB ~ 수십 GB
- **비용**: 유료 구독

### Ollama (오프라인)
- **모델 다운로드**: 최초 1회 (3-7 GB/모델)
- **사용 시 데이터**: 0 bytes ✅
- **월 사용량**: 0 bytes ✅
- **비용**: $0 ✅

---

## ⚡ 성능 영향

**오프라인이라고 느려지지 않습니다!**

오히려 더 빠를 수 있습니다:
- 네트워크 지연 없음
- 서버 왕복 시간 없음
- 로컬 GPU/CPU 직접 사용

```bash
# 온라인 AI (예: ChatGPT API)
요청 → 인터넷 → 서버 → 처리 → 인터넷 → 응답
(지연: 500ms ~ 2초)

# Ollama 오프라인
요청 → 로컬 처리 → 응답
(지연: 즉시 시작)
```

---

## 🔒 프라이버시 보너스

완전 오프라인 = 완전 프라이빗

- ✅ 코드가 외부로 전송 안 됨
- ✅ 데이터가 서버에 저장 안 됨
- ✅ 로그가 남지 않음
- ✅ 감시 불가능
- ✅ 100% 프라이빗

---

## ✅ 최종 답변

### Q: Ollama도 계속 네트워크 연결 상태여야 해?

**A: 아니요! 완전히 오프라인입니다!**

```bash
# 한 번만 (인터넷 필요)
ollama pull llama2

# 이후 영원히 (인터넷 불필요)
ollama run llama2
ollama run llama2
ollama run llama2
...
```

### 검증 방법

```bash
# 1. WiFi 끄기
# 2. 실행
ollama run llama2 "안녕하세요!"

# 3. 정상 작동 확인! ✅
```

---

## 📞 문제 해결

### "connection refused" 에러

```bash
# Ollama 서비스 시작
ollama serve

# 또는 백그라운드로
nohup ollama serve &
```

### 모델이 없다고 나옴

```bash
# 모델 목록 확인
ollama list

# 비어있으면 다운로드 (인터넷 필요)
ollama pull llama2
```

---

## 🎉 결론

**Ollama = 완전한 오프라인 AI**

- 설치: 인터넷 필요 (1번)
- 모델 다운로드: 인터넷 필요 (모델당 1번)
- **사용: 인터넷 불필요 (영원히)**

**비행기 모드에서도, WiFi 없어도, 산 속에서도 사용 가능합니다!** 🚀
