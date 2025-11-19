# Contributing to Local LLM Serve

프로젝트에 기여해주셔서 감사합니다! 🎉

## 🚀 빠른 시작

### 1. 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/mustzee/serve.git
cd serve

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r server/requirements.txt
pip install -r tests/requirements.txt

# Ollama 설치 및 모델 다운로드
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
```

### 2. 프로젝트 검증

```bash
# 전체 검증
python verify_project.py

# 테스트 실행
pytest tests/
```

## 📝 기여 방법

### 버그 리포트

버그를 발견하셨나요? GitHub Issues에 다음 정보와 함께 올려주세요:

- 운영체제 및 버전
- Python 버전
- 재현 단계
- 예상 동작 vs 실제 동작
- 에러 메시지 (있다면)

### 기능 제안

새로운 기능을 제안하고 싶으신가요?

1. GitHub Issues에서 먼저 토론
2. 기능의 목적과 사용 사례 설명
3. 가능하면 API 디자인 제안

### Pull Request

1. **Fork** 저장소
2. **새 브랜치** 생성 (`git checkout -b feature/amazing-feature`)
3. **변경 사항 커밋** (`git commit -m 'Add amazing feature'`)
4. **브랜치 푸시** (`git push origin feature/amazing-feature`)
5. **Pull Request** 열기

## 🎨 코드 스타일

### Python

```python
# PEP 8 따르기
# 들여쓰기: 4칸 스페이스
# 최대 줄 길이: 100자

# 타입 힌트 사용
def process_message(message: str, temperature: float = 0.7) -> str:
    """함수 설명

    Args:
        message: 처리할 메시지
        temperature: 샘플링 온도

    Returns:
        처리된 결과
    """
    pass

# Docstring은 Google 스타일
```

### Go

```go
// Go 표준 포맷 사용
// gofmt로 자동 포맷팅

// 주석은 완전한 문장으로
// 함수 위에 설명 추가

// Chat sends a chat completion request to the server
func (c *Client) Chat(ctx context.Context, req *ChatCompletionRequest) (*ChatCompletionResponse, error) {
    // 구현
}
```

## 🧪 테스트

### 테스트 작성

```python
# tests/test_new_feature.py
def test_new_feature():
    """새 기능 테스트"""
    # Arrange
    client = LLMClient("http://localhost:8000")

    # Act
    result = client.new_feature()

    # Assert
    assert result is not None
```

### 테스트 실행

```bash
# 모든 테스트
pytest tests/

# 특정 파일
pytest tests/test_client.py

# 커버리지
pytest --cov=server tests/
```

## 📚 문서

### 문서 업데이트

코드 변경 시 관련 문서도 함께 업데이트해주세요:

- `README.md`: 주요 기능 변경
- `QUICKSTART.md`: 사용법 변경
- API 주석: 함수/클래스 변경
- 예제 코드: 새 기능 추가

### 문서 작성 가이드

- 명확하고 간결하게
- 예제 코드 포함
- 한국어와 영어 모두 환영
- 이모지 적절히 사용 ✅

## 🏗️ 프로젝트 구조

```
serve/
├── server/              # FastAPI 서버
│   ├── main.py         # 애플리케이션 진입점
│   ├── models.py       # Pydantic 모델
│   ├── config.py       # 설정 관리
│   └── backends/       # LLM 백엔드
├── clients/            # 클라이언트 라이브러리
│   ├── python/         # Python 클라이언트
│   └── go/             # Go 클라이언트
├── examples/           # 예제 코드
├── tests/              # 테스트
└── docs/               # 추가 문서
```

## 🎯 기여 아이디어

도움이 필요한 영역:

### 쉬운 기여
- [ ] 오타 수정
- [ ] 문서 개선
- [ ] 예제 추가
- [ ] 번역 (영어 ↔ 한국어)

### 중간 기여
- [ ] 버그 수정
- [ ] 테스트 추가
- [ ] 에러 처리 개선
- [ ] 성능 최적화

### 고급 기여
- [ ] 새 백엔드 추가
- [ ] 새 기능 구현
- [ ] 아키텍처 개선
- [ ] CI/CD 설정

## 🤝 커뮤니티

### 행동 강령

- 존중하고 친절하게
- 건설적인 피드백
- 다양성 존중
- 협력적인 태도

### 소통

- GitHub Issues: 버그, 기능 요청
- GitHub Discussions: 일반 토론
- Pull Requests: 코드 리뷰

## 📜 라이선스

기여한 코드는 프로젝트의 MIT 라이선스를 따릅니다.

## ❓ 질문이 있으신가요?

GitHub Issues에 질문을 올려주세요. 기꺼이 도와드리겠습니다!

---

**다시 한번 감사드립니다!** 🎉

모든 기여는 소중합니다. 작은 오타 수정부터 큰 기능 추가까지, 모든 것이 프로젝트를 더 좋게 만듭니다!
