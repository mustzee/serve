#!/usr/bin/env python3
"""
시스템 요구사항 확인 스크립트
실행하기 전에 시스템이 충분한 리소스를 가지고 있는지 확인합니다.
"""
import os
import sys
import platform
import subprocess
import shutil


def get_memory_info():
    """시스템 메모리 정보 조회"""
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                total = int([x for x in meminfo.split('\n') if 'MemTotal' in x][0].split()[1]) // 1024
                available = int([x for x in meminfo.split('\n') if 'MemAvailable' in x][0].split()[1]) // 1024
                return total, available
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
            total = int(result.stdout.split()[1]) // (1024 ** 2)
            # 간단히 80% 가용으로 가정
            available = int(total * 0.8)
            return total, available
    except:
        return None, None


def get_disk_space(path='.'):
    """디스크 여유 공간 조회 (MB)"""
    try:
        stat = shutil.disk_usage(path)
        return stat.free // (1024 ** 2)
    except:
        return None


def get_cpu_info():
    """CPU 정보 조회"""
    try:
        if platform.system() == "Linux":
            result = subprocess.run(['nproc'], capture_output=True, text=True)
            return int(result.stdout.strip())
        elif platform.system() == "Darwin":
            result = subprocess.run(['sysctl', '-n', 'hw.ncpu'], capture_output=True, text=True)
            return int(result.stdout.strip())
    except:
        return None


def check_gpu():
    """GPU 존재 여부 확인"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            # VRAM 정보 추출
            lines = result.stdout.split('\n')
            for line in lines:
                if 'MiB' in line and '/' in line:
                    # 간단한 파싱
                    return True, "NVIDIA GPU detected"
        return False, "No NVIDIA GPU"
    except:
        return False, "nvidia-smi not available"


def recommend_config(total_ram, available_ram, disk_free, cpu_cores, has_gpu):
    """시스템 사양에 따른 권장 설정"""
    print("\n" + "="*60)
    print("시스템 분석 결과")
    print("="*60)

    print(f"\n총 RAM: {total_ram} MB ({total_ram/1024:.1f} GB)")
    print(f"사용 가능한 RAM: {available_ram} MB ({available_ram/1024:.1f} GB)")
    print(f"디스크 여유 공간: {disk_free} MB ({disk_free/1024:.1f} GB)")
    print(f"CPU 코어: {cpu_cores}")
    print(f"GPU: {'Yes (NVIDIA)' if has_gpu else 'No'}")

    print("\n" + "="*60)
    print("권장 사항")
    print("="*60)

    # RAM 기준 판단
    ram_gb = total_ram / 1024
    available_gb = available_ram / 1024

    if ram_gb < 6:
        print("\n❌ 메모리 부족")
        print(f"   현재: {ram_gb:.1f} GB")
        print(f"   필요: 최소 8 GB")
        print(f"   권장: 16 GB 이상")
        return False

    elif ram_gb < 10:
        print("\n⚠️  최소 사양 (가벼운 사용)")
        print(f"   RAM: {ram_gb:.1f} GB")
        print("\n권장 설정:")
        print("  - 설정 파일: config-low-memory.yaml")
        print("  - 백엔드: llamacpp")
        print("  - 모델: Llama 2 7B Q4 (3.8 GB)")
        print("  - 컨텍스트: 2048")
        print("  - GPU: CPU 전용")
        print("\n시작 명령:")
        print("  docker-compose -f docker-compose-low-memory.yml up -d")
        print("  또는")
        print("  cp config-low-memory.yaml config.yaml")

    elif ram_gb < 20:
        print("\n✅ 일반 사양 (추천)")
        print(f"   RAM: {ram_gb:.1f} GB")
        print("\n권장 설정:")
        print("  - 설정 파일: config.yaml (기본)")
        print("  - 백엔드: ollama")
        print("  - 모델: Llama 2 7B + CodeLlama 7B")
        print("  - 컨텍스트: 4096")
        if has_gpu:
            print("  - GPU: 자동 활성화 (권장)")
            print("\n설정 파일: config-gpu.yaml 사용 권장")
        else:
            print("  - GPU: CPU 전용 (느릴 수 있음)")
        print("\n시작 명령:")
        print("  docker-compose up -d")

    else:
        print("\n🚀 고사양 (프로덕션 레벨)")
        print(f"   RAM: {ram_gb:.1f} GB")
        print("\n권장 설정:")
        print("  - 백엔드: vllm (최고 성능) 또는 ollama")
        print("  - 모델: 13B 모델 사용 가능")
        print("  - 여러 모델 동시 로드 가능")
        print("  - 컨텍스트: 8192")
        if has_gpu:
            print("  - GPU: 전체 레이어 오프로드")
        print("\n시작 명령:")
        print("  docker-compose up -d")

    # 디스크 확인
    disk_gb = disk_free / 1024
    print(f"\n디스크 여유 공간: {disk_gb:.1f} GB")

    if disk_gb < 5:
        print("❌ 디스크 공간 부족")
        print("   최소 10 GB 필요")
        return False
    elif disk_gb < 15:
        print("⚠️  디스크 공간 제한적")
        print("   1-2개 모델만 설치 가능")
        print("   권장: 30 GB 이상")
    else:
        print("✅ 디스크 공간 충분")

    # 권장 모델
    print("\n" + "="*60)
    print("권장 모델 다운로드")
    print("="*60)

    if ram_gb < 10:
        print("\n# 최소 사양용 (하나만 선택)")
        print("docker exec -it llm-ollama ollama pull llama2:7b-chat-q4_0")
        print("# 또는")
        print("docker exec -it llm-ollama ollama pull codellama:7b-q4_0")
        print("\n예상 디스크 사용: ~4 GB")

    elif ram_gb < 20:
        print("\n# 일반 사양용")
        print("docker exec -it llm-ollama ollama pull llama2:7b")
        print("docker exec -it llm-ollama ollama pull codellama:7b")
        print("\n예상 디스크 사용: ~8 GB")

    else:
        print("\n# 고사양용")
        print("docker exec -it llm-ollama ollama pull llama2:13b")
        print("docker exec -it llm-ollama ollama pull codellama:13b")
        print("docker exec -it llm-ollama ollama pull mistral:7b")
        print("\n예상 디스크 사용: ~20 GB")

    print("\n" + "="*60)
    print("다음 단계")
    print("="*60)
    print("\n1. 위의 설정 파일 사용")
    print("2. Docker Compose로 서비스 시작")
    print("3. 권장 모델 다운로드")
    print("4. 예제 실행 (examples/)")
    print("\n자세한 내용: MEMORY_OPTIMIZATION.md 참조")

    return True


def main():
    print("시스템 요구사항 확인 중...\n")

    total_ram, available_ram = get_memory_info()
    disk_free = get_disk_space()
    cpu_cores = get_cpu_info()
    has_gpu, gpu_info = check_gpu()

    if total_ram is None or disk_free is None:
        print("❌ 시스템 정보를 가져올 수 없습니다.")
        print("수동으로 확인해주세요:")
        print("  - RAM: 최소 8 GB (권장 16 GB)")
        print("  - 디스크: 최소 10 GB (권장 30 GB)")
        print("  - CPU: 4코어 이상")
        return

    success = recommend_config(total_ram, available_ram, disk_free, cpu_cores, has_gpu)

    if not success:
        print("\n시스템이 최소 요구사항을 충족하지 못합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
