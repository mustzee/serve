#!/usr/bin/env python3
"""
프로젝트 검증 스크립트
서버, 클라이언트, 예제가 정상 작동하는지 확인
"""
import subprocess
import sys
import time
import requests
import os


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_status(message, status="info"):
    """상태 메시지 출력"""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")


def check_command(command):
    """명령어 존재 확인"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_python_packages():
    """Python 패키지 확인"""
    print("\n=== Python 패키지 확인 ===")

    required = ["fastapi", "uvicorn", "pydantic", "aiohttp", "requests"]
    missing = []

    for package in required:
        try:
            __import__(package)
            print_status(f"{package} 설치됨", "success")
        except ImportError:
            print_status(f"{package} 없음", "error")
            missing.append(package)

    if missing:
        print_status(f"누락된 패키지: {', '.join(missing)}", "error")
        print_status("설치: pip install -r server/requirements.txt", "info")
        return False

    return True


def check_ollama():
    """Ollama 확인"""
    print("\n=== Ollama 확인 ===")

    if not check_command("ollama"):
        print_status("Ollama 설치되지 않음", "warning")
        print_status("설치: curl -fsSL https://ollama.ai/install.sh | sh", "info")
        return False

    print_status("Ollama 설치됨", "success")

    # Ollama 서비스 확인
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print_status(f"Ollama 실행 중, {len(models)}개 모델 있음", "success")
                for model in models[:3]:
                    print(f"  - {model['name']}")
                return True
            else:
                print_status("Ollama 실행 중이지만 모델 없음", "warning")
                print_status("모델 다운로드: ollama pull llama2", "info")
                return False
    except requests.exceptions.RequestException:
        print_status("Ollama 실행되지 않음", "warning")
        print_status("실행: ollama serve", "info")
        return False


def check_server_files():
    """서버 파일 확인"""
    print("\n=== 서버 파일 확인 ===")

    required_files = [
        "server/main.py",
        "server/config.py",
        "server/models.py",
        "server/backends/base.py",
        "server/backends/ollama.py",
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print_status(f"{file} 존재", "success")
        else:
            print_status(f"{file} 없음", "error")
            all_exist = False

    return all_exist


def test_server():
    """서버 실행 테스트"""
    print("\n=== 서버 테스트 ===")

    # 서버 시작
    print_status("서버 시작 중... (5초 대기)", "info")

    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server.main:app", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 서버 시작 대기
        time.sleep(5)

        # Health check
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print_status("서버 정상 작동", "success")
                data = response.json()
                print(f"  Backend: {data.get('backend')}")
                print(f"  Status: {data.get('status')}")
                result = True
            else:
                print_status(f"서버 응답 오류: {response.status_code}", "error")
                result = False
        except requests.exceptions.RequestException as e:
            print_status(f"서버 연결 실패: {e}", "error")
            result = False

        # 서버 종료
        process.terminate()
        process.wait(timeout=5)

        return result

    except Exception as e:
        print_status(f"서버 시작 실패: {e}", "error")
        return False


def test_python_client():
    """Python 클라이언트 테스트"""
    print("\n=== Python 클라이언트 테스트 ===")

    if not os.path.exists("clients/python/client.py"):
        print_status("클라이언트 파일 없음", "error")
        return False

    try:
        sys.path.insert(0, os.path.abspath("."))
        from clients.python.client import LLMClient, Message

        print_status("클라이언트 import 성공", "success")

        # 간단한 인스턴스 생성 테스트
        client = LLMClient("http://localhost:8000")
        print_status("클라이언트 인스턴스 생성 성공", "success")

        return True
    except Exception as e:
        print_status(f"클라이언트 테스트 실패: {e}", "error")
        return False


def check_examples():
    """예제 파일 확인"""
    print("\n=== 예제 파일 확인 ===")

    examples = [
        "examples/coding_assistant.py",
        "examples/daily_agent.py",
        "examples/simple_ollama.py",
        "examples/coding_assistant.go",
    ]

    all_exist = True
    for example in examples:
        if os.path.exists(example):
            print_status(f"{example} 존재", "success")
        else:
            print_status(f"{example} 없음", "error")
            all_exist = False

    return all_exist


def check_documentation():
    """문서 확인"""
    print("\n=== 문서 확인 ===")

    docs = [
        "README.md",
        "QUICKSTART.md",
        "INSTALL_WITHOUT_DOCKER.md",
        "MEMORY_OPTIMIZATION.md",
        "OFFLINE_MODE.md",
        "CLAUDE_LIKE_MODELS.md",
    ]

    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print_status(f"{doc} 존재", "success")
        else:
            print_status(f"{doc} 없음", "error")
            all_exist = False

    return all_exist


def check_docker():
    """Docker 설정 확인"""
    print("\n=== Docker 설정 확인 ===")

    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose-low-memory.yml",
        ".dockerignore",
    ]

    all_exist = True
    for file in docker_files:
        if os.path.exists(file):
            print_status(f"{file} 존재", "success")
        else:
            print_status(f"{file} 없음", "warning")
            all_exist = False

    # Docker 명령어 확인
    if check_command("docker"):
        print_status("Docker 설치됨", "success")
    else:
        print_status("Docker 설치되지 않음", "warning")

    if check_command("docker-compose"):
        print_status("Docker Compose 설치됨", "success")
    else:
        print_status("Docker Compose 설치되지 않음", "warning")

    return all_exist


def main():
    """메인 검증 실행"""
    print("=" * 60)
    print("Local LLM Serve - 프로젝트 검증")
    print("=" * 60)

    results = {
        "Python 패키지": check_python_packages(),
        "Ollama": check_ollama(),
        "서버 파일": check_server_files(),
        "Python 클라이언트": test_python_client(),
        "예제 파일": check_examples(),
        "문서": check_documentation(),
        "Docker 설정": check_docker(),
    }

    # 서버 테스트 (선택적)
    print("\n" + "=" * 60)
    response = input("\n서버 실행 테스트를 하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        results["서버 테스트"] = test_server()

    # 결과 요약
    print("\n" + "=" * 60)
    print("검증 결과 요약")
    print("=" * 60)

    passed = 0
    total = len(results)

    for name, result in results.items():
        if result:
            print_status(f"{name}: 통과", "success")
            passed += 1
        else:
            print_status(f"{name}: 실패", "error")

    print("\n" + "=" * 60)
    print(f"결과: {passed}/{total} 통과 ({passed*100//total}%)")
    print("=" * 60)

    if passed == total:
        print_status("\n모든 검증 통과! 프로젝트가 정상입니다! 🎉", "success")
        return 0
    elif passed >= total * 0.7:
        print_status("\n대부분 정상입니다. 경고 항목을 확인하세요.", "warning")
        return 0
    else:
        print_status("\n여러 문제가 발견되었습니다. 위 오류를 수정하세요.", "error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
