#!/usr/bin/env python3
"""
가장 간단한 사용 예제 - Ollama Python 라이브러리 직접 사용
Docker나 서버 없이 바로 실행 가능

설치: pip install ollama
"""

try:
    import ollama
except ImportError:
    print("❌ ollama 라이브러리가 설치되지 않았습니다.")
    print("설치: pip install ollama")
    exit(1)


def simple_chat():
    """가장 간단한 대화"""
    print("=== 간단한 대화 ===\n")

    response = ollama.chat(model='llama2', messages=[
        {
            'role': 'user',
            'content': '안녕하세요! 간단히 자기소개해주세요.',
        },
    ])

    print(response['message']['content'])


def streaming_chat():
    """스트리밍 대화"""
    print("\n\n=== 스트리밍 대화 ===\n")
    print("질문: Python으로 Hello World 출력하는 법?\n")
    print("답변: ", end="", flush=True)

    stream = ollama.chat(
        model='llama2',
        messages=[{
            'role': 'user',
            'content': 'Python으로 Hello World를 출력하는 가장 간단한 방법을 알려주세요.',
        }],
        stream=True,
    )

    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)

    print()  # 줄바꿈


def code_generation():
    """코드 생성 (CodeLlama)"""
    print("\n\n=== 코드 생성 (CodeLlama) ===\n")
    print("질문: Python으로 피보나치 수열 함수 만들기\n")

    try:
        response = ollama.chat(model='codellama', messages=[
            {
                'role': 'user',
                'content': 'Python으로 피보나치 수열을 계산하는 함수를 작성해주세요. 메모이제이션을 사용하세요.',
            },
        ])

        print("생성된 코드:")
        print(response['message']['content'])
    except ollama.ResponseError as e:
        print(f"❌ 에러: {e}")
        print("codellama 모델을 다운로드해주세요: ollama pull codellama")


def interactive_mode():
    """대화형 모드"""
    print("\n\n=== 대화형 모드 ===")
    print("종료하려면 'exit' 또는 'quit'를 입력하세요\n")

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("안녕히 가세요!")
            break

        conversation_history.append({
            'role': 'user',
            'content': user_input
        })

        print("Assistant: ", end="", flush=True)

        full_response = ""
        stream = ollama.chat(
            model='llama2',
            messages=conversation_history,
            stream=True,
        )

        for chunk in stream:
            content = chunk['message']['content']
            print(content, end='', flush=True)
            full_response += content

        print("\n")

        conversation_history.append({
            'role': 'assistant',
            'content': full_response
        })


def list_models():
    """설치된 모델 목록"""
    print("=== 설치된 모델 ===\n")

    models = ollama.list()

    if not models['models']:
        print("설치된 모델이 없습니다.")
        print("\n모델 다운로드:")
        print("  ollama pull llama2")
        print("  ollama pull codellama")
        return

    for model in models['models']:
        name = model['name']
        size = model['size'] / (1024**3)  # GB로 변환
        print(f"- {name} ({size:.2f} GB)")


def main():
    """메인 함수"""
    print("=" * 60)
    print("Ollama Python 라이브러리 사용 예제")
    print("Docker나 별도 서버 없이 바로 사용 가능!")
    print("=" * 60)

    # 모델 목록 확인
    list_models()

    try:
        # 간단한 예제들
        simple_chat()
        streaming_chat()
        code_generation()

        # 대화형 모드
        print("\n")
        input("Enter를 눌러 대화형 모드를 시작하세요...")
        interactive_mode()

    except ollama.ResponseError as e:
        print(f"\n❌ 에러 발생: {e}")
        print("\nOllama가 실행 중인지 확인하세요:")
        print("  - macOS: Ollama 앱 실행")
        print("  - Linux: ollama serve")
        print("\n모델이 다운로드되었는지 확인하세요:")
        print("  ollama pull llama2")
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 에러: {e}")


if __name__ == "__main__":
    main()
