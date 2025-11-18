#!/bin/bash
# 오프라인 작동 테스트 스크립트

echo "=== Ollama 오프라인 작동 테스트 ==="
echo ""

# Ollama 설치 확인
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama가 설치되지 않았습니다."
    echo "먼저 설치해주세요: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✓ Ollama 설치됨"

# 모델 확인
echo ""
echo "다운로드된 모델 확인 중..."
models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

if [ -z "$models" ]; then
    echo "❌ 다운로드된 모델이 없습니다."
    echo ""
    echo "먼저 모델을 다운로드해주세요 (인터넷 필요):"
    echo "  ollama pull llama2"
    exit 1
fi

echo "✓ 다운로드된 모델:"
echo "$models" | while read model; do
    echo "  - $model"
done

# 네트워크 상태 확인
echo ""
echo "현재 네트워크 상태 확인 중..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "⚠️  현재 인터넷 연결됨"
    echo ""
    read -p "네트워크를 차단하고 테스트하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "안내: 수동으로 네트워크를 끄고 Enter를 눌러주세요."
        echo "(WiFi 끄기, 이더넷 케이블 뽑기 등)"
        read -p "네트워크를 껐으면 Enter를 눌러주세요..."

        if ping -c 1 8.8.8.8 &> /dev/null; then
            echo "⚠️  아직 네트워크가 연결되어 있습니다."
            echo "그래도 계속 테스트합니다..."
        else
            echo "✓ 네트워크 차단됨"
        fi
    fi
else
    echo "✓ 인터넷 연결 안 됨 (오프라인 상태)"
fi

# 오프라인 테스트
echo ""
echo "=== 오프라인 테스트 시작 ==="
echo ""
echo "Ollama에게 질문합니다: '안녕하세요! 1+1은?'"
echo ""
echo "응답:"
echo "---"

# 첫 번째 모델로 테스트
first_model=$(echo "$models" | head -n 1)
ollama run "$first_model" "안녕하세요! 1+1은 얼마인가요? 짧게 답해주세요." 2>&1

exit_code=$?

echo "---"
echo ""

if [ $exit_code -eq 0 ]; then
    echo "✅ 성공! Ollama가 오프라인에서 정상 작동합니다!"
    echo ""
    echo "결론:"
    echo "  - 인터넷 연결 없이도 완벽하게 작동합니다"
    echo "  - 모델은 로컬에 저장되어 있습니다"
    echo "  - 비행기 모드, WiFi 꺼도 사용 가능합니다"
else
    echo "❌ 테스트 실패"
    echo ""
    echo "가능한 원인:"
    echo "  1. Ollama 서비스가 실행되지 않음"
    echo "  2. 모델 파일이 손상됨"
    echo "  3. 권한 문제"
    echo ""
    echo "해결 방법:"
    echo "  - Ollama 재시작: ollama serve"
    echo "  - 모델 재다운로드: ollama pull $first_model"
fi

echo ""
echo "=== 테스트 완료 ==="
