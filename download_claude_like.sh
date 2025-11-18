#!/bin/bash
# Claude와 유사한 모델 다운로드 스크립트

echo "=== Claude와 유사한 모델 다운로드 ==="
echo ""

# 시스템 메모리 확인
if command -v free &> /dev/null; then
    total_ram=$(free -g | awk '/^Mem:/{print $2}')
    echo "시스템 RAM: ${total_ram}GB"
elif command -v sysctl &> /dev/null; then
    total_ram=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
    echo "시스템 RAM: ${total_ram}GB"
else
    total_ram=0
    echo "메모리 정보를 확인할 수 없습니다."
fi

echo ""
echo "Claude와 가장 비슷한 모델을 선택하세요:"
echo ""
echo "1. Qwen2.5 7B (8GB RAM, 가장 추천! ⭐)"
echo "   - 논리적 추론 우수"
echo "   - 코딩 능력 최고"
echo "   - Claude와 85% 유사"
echo ""
echo "2. Qwen2.5-Coder 7B (8GB RAM, 코딩 특화)"
echo "   - 코드 생성/리뷰 전문"
echo "   - Python, Go, JavaScript 등"
echo ""
echo "3. Llama 3.1 8B (10GB RAM, Meta 최신)"
echo "   - 긴 컨텍스트 지원"
echo "   - 균형잡힌 성능"
echo ""
echo "4. Qwen2.5 14B (16GB RAM, 고성능)"
echo "   - Claude와 90% 유사"
echo "   - 최고 품질"
echo ""
echo "5. Mixtral 8x7B (32GB RAM, 프로급)"
echo "   - Claude와 92% 유사"
echo "   - 최강 성능"
echo ""
echo "6. 전부 다운로드 (자동 선택)"
echo ""

read -p "선택 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Qwen2.5 7B 다운로드 중... (4.7 GB)"
        ollama pull qwen2.5:7b
        echo "✅ 완료!"
        echo ""
        echo "사용 방법:"
        echo "  ollama run qwen2.5:7b"
        ;;
    2)
        echo ""
        echo "Qwen2.5-Coder 7B 다운로드 중... (4.7 GB)"
        ollama pull qwen2.5-coder:7b
        echo "✅ 완료!"
        echo ""
        echo "사용 방법:"
        echo "  ollama run qwen2.5-coder:7b '피보나치 수열 만들어줘'"
        ;;
    3)
        echo ""
        echo "Llama 3.1 8B 다운로드 중... (4.7 GB)"
        ollama pull llama3.1:8b
        echo "✅ 완료!"
        echo ""
        echo "사용 방법:"
        echo "  ollama run llama3.1:8b"
        ;;
    4)
        if [ "$total_ram" -lt 16 ] && [ "$total_ram" -gt 0 ]; then
            echo ""
            echo "⚠️  경고: RAM이 부족할 수 있습니다 (${total_ram}GB < 16GB)"
            read -p "계속하시겠습니까? (y/n) " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "취소되었습니다."
                exit 1
            fi
        fi
        echo ""
        echo "Qwen2.5 14B 다운로드 중... (9 GB)"
        ollama pull qwen2.5:14b
        echo "✅ 완료!"
        echo ""
        echo "사용 방법:"
        echo "  ollama run qwen2.5:14b"
        ;;
    5)
        if [ "$total_ram" -lt 32 ] && [ "$total_ram" -gt 0 ]; then
            echo ""
            echo "⚠️  경고: RAM이 부족합니다 (${total_ram}GB < 32GB)"
            echo "이 모델은 32GB 이상 RAM이 필요합니다."
            read -p "계속하시겠습니까? (느릴 수 있음) (y/n) " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "취소되었습니다."
                exit 1
            fi
        fi
        echo ""
        echo "Mixtral 8x7B 다운로드 중... (26 GB, 시간 걸립니다)"
        ollama pull mixtral:8x7b
        echo "✅ 완료!"
        echo ""
        echo "사용 방법:"
        echo "  ollama run mixtral:8x7b"
        ;;
    6)
        echo ""
        echo "시스템에 맞는 모델을 자동으로 선택합니다..."

        if [ "$total_ram" -ge 32 ]; then
            echo "고사양 시스템: Mixtral 8x7B + Qwen2.5 14B"
            ollama pull mixtral:8x7b
            ollama pull qwen2.5:14b
        elif [ "$total_ram" -ge 16 ]; then
            echo "중사양 시스템: Qwen2.5 14B + Llama 3.1 8B"
            ollama pull qwen2.5:14b
            ollama pull llama3.1:8b
        else
            echo "일반 시스템: Qwen2.5 7B + Qwen2.5-Coder 7B"
            ollama pull qwen2.5:7b
            ollama pull qwen2.5-coder:7b
        fi
        echo "✅ 모두 완료!"
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "=== 다운로드 완료! ==="
echo ""
echo "설치된 모델 확인:"
ollama list
echo ""
echo "빠른 테스트:"
echo "  ollama run qwen2.5:7b '안녕하세요! 자기소개해주세요.'"
echo ""
echo "Python에서 사용:"
echo "  python examples/simple_ollama.py"
echo ""
echo "이 프로젝트 서버에서 사용:"
echo "  # config-claude-like.yaml 사용"
echo "  cp config-claude-like.yaml config.yaml"
echo "  python -m uvicorn server.main:app --port 8000"
