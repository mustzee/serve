#!/bin/bash
# 로컬 설치 스크립트 (Docker 없이)

set -e

echo "=== Local LLM Serve - 로컬 설치 ==="
echo ""

# Ollama 설치 확인
if command -v ollama &> /dev/null; then
    echo "✓ Ollama 이미 설치됨"
    ollama --version
else
    echo "Ollama가 설치되지 않았습니다."
    echo ""

    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        read -p "Ollama를 설치하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Ollama 설치 중..."
            curl -fsSL https://ollama.ai/install.sh | sh
            echo "✓ Ollama 설치 완료"
        else
            echo "Ollama를 수동으로 설치해주세요: https://ollama.ai/download"
            exit 1
        fi
    else
        echo "Windows 사용자는 https://ollama.ai/download 에서 수동으로 설치해주세요."
        exit 1
    fi
fi

echo ""
echo "Ollama 서비스 시작 중..."

# Ollama 서비스 시작 (백그라운드)
if ! pgrep -x "ollama" > /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a Ollama 2>/dev/null || ollama serve &
    else
        # Linux
        ollama serve &
    fi
    sleep 3
    echo "✓ Ollama 서비스 시작됨"
else
    echo "✓ Ollama 서비스 이미 실행 중"
fi

# Python 확인
echo ""
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found: $(python3 --version)"
else
    echo "❌ Python3가 설치되지 않았습니다."
    echo "   Python 3.8 이상을 설치해주세요."
    exit 1
fi

# 가상환경 생성 (선택사항)
echo ""
read -p "Python 가상환경을 생성하시겠습니까? (권장) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "가상환경 생성 중..."
        python3 -m venv venv
        echo "✓ 가상환경 생성 완료"
    else
        echo "✓ 가상환경이 이미 존재합니다"
    fi

    echo "가상환경 활성화 중..."
    source venv/bin/activate
    echo "✓ 가상환경 활성화됨"
fi

# Python 의존성 설치
echo ""
echo "Python 의존성 설치 중..."
pip install -q --upgrade pip
pip install -q -r server/requirements.txt
pip install -q -r clients/python/requirements.txt
pip install -q ollama  # Ollama Python 클라이언트
echo "✓ 의존성 설치 완료"

# 모델 다운로드 안내
echo ""
echo "=== 모델 다운로드 ==="
echo ""
echo "다음 명령어로 모델을 다운로드하세요:"
echo ""
echo "# 일반 대화용"
echo "ollama pull llama2"
echo ""
echo "# 코딩용"
echo "ollama pull codellama"
echo ""

read -p "지금 llama2 모델을 다운로드하시겠습니까? (3.8 GB) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "llama2 다운로드 중... (시간이 걸릴 수 있습니다)"
    ollama pull llama2
    echo "✓ llama2 다운로드 완료"
fi

echo ""
read -p "codellama 모델도 다운로드하시겠습니까? (3.8 GB) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "codellama 다운로드 중..."
    ollama pull codellama
    echo "✓ codellama 다운로드 완료"
fi

# 설치 완료
echo ""
echo "=== 설치 완료! ==="
echo ""
echo "다음 방법으로 사용할 수 있습니다:"
echo ""
echo "1. Ollama 직접 사용 (가장 쉬움):"
echo "   ollama run llama2"
echo "   ollama run codellama"
echo ""
echo "2. Python으로 사용:"
echo "   python3 -c \"import ollama; print(ollama.chat(model='llama2', messages=[{'role':'user','content':'안녕'}]))\""
echo ""
echo "3. 이 프로젝트의 서버 실행 (OpenAI 호환 API):"
echo "   python -m uvicorn server.main:app --host 0.0.0.0 --port 8000"
echo "   또는"
echo "   python -m server.main"
echo ""
echo "4. 예제 실행:"
echo "   python examples/coding_assistant.py"
echo "   python examples/daily_agent.py"
echo ""
echo "자세한 사용법: INSTALL_WITHOUT_DOCKER.md 참조"
echo ""

# 빠른 테스트
echo "=== 빠른 테스트 ==="
echo ""
read -p "Ollama가 정상 작동하는지 테스트하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "테스트 중: '안녕하세요'라고 질문합니다..."
    echo ""
    ollama run llama2 "안녕하세요! 간단히 인사해주세요." --verbose=false 2>/dev/null || echo "모델을 먼저 다운로드해주세요: ollama pull llama2"
fi

echo ""
echo "설정이 완료되었습니다! 🎉"
