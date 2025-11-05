#!/usr/bin/env python3
"""
Claude Opus 4.1 통합 테스트 스크립트
"""

import sys
import os
import asyncio
from datetime import datetime

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_test(name, status, message=""):
    """테스트 결과 출력"""
    icon = "✅" if status else "❌"
    color = GREEN if status else RED
    print(f"{icon} {color}{name}{RESET}", end="")
    if message:
        print(f" - {message}")
    else:
        print()

def print_header(text):
    """헤더 출력"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_section(text):
    """섹션 출력"""
    print(f"\n{BOLD}{YELLOW}▶ {text}{RESET}")

# 테스트 결과 저장
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def record_test(name, passed, message=""):
    """테스트 결과 기록"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    print_test(name, passed, message)

# ==================== 테스트 시작 ====================

print_header("Claude Opus 4.1 통합 테스트")
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Python 환경 테스트
print_section("1. Python 환경 확인")

try:
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    record_test(
        "Python 버전",
        is_valid,
        f"Python {version.major}.{version.minor}.{version.micro}"
    )
except Exception as e:
    record_test("Python 버전", False, str(e))

# 2. 필수 패키지 import 테스트
print_section("2. 필수 패키지 확인")

packages = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("anthropic", "Anthropic"),
    ("dotenv", "python-dotenv"),
    ("pydantic", "Pydantic")
]

for module_name, display_name in packages:
    try:
        __import__(module_name)
        record_test(f"{display_name} 패키지", True, f"{module_name} import 성공")
    except ImportError as e:
        record_test(f"{display_name} 패키지", False, f"import 실패: {str(e)}")

# 3. 백엔드 파일 존재 확인
print_section("3. 백엔드 파일 확인")

backend_files = [
    "backend/main.py",
    "backend/main_replit_improved.py",
    "backend/context_manager.py",
    "backend/connection_manager.py"
]

for file_path in backend_files:
    exists = os.path.exists(file_path)
    record_test(f"{file_path}", exists, "파일 존재" if exists else "파일 없음")

# 4. 모델명 확인
print_section("4. Claude Opus 4.1 모델명 확인")

try:
    with open("backend/main.py", "r", encoding="utf-8") as f:
        content = f.read()
        has_opus_4_1 = "claude-opus-4-1-20250805" in content
        record_test(
            "main.py 모델명",
            has_opus_4_1,
            "Opus 4.1 모델 사용" if has_opus_4_1 else "모델명 오류"
        )
except Exception as e:
    record_test("main.py 모델명", False, str(e))

try:
    with open("backend/main_replit_improved.py", "r", encoding="utf-8") as f:
        content = f.read()
        has_opus_4_1 = "claude-opus-4-1-20250805" in content
        count = content.count("claude-opus-4-1-20250805")
        record_test(
            "main_replit_improved.py 모델명",
            has_opus_4_1 and count >= 3,
            f"Opus 4.1 모델 {count}곳에서 사용" if has_opus_4_1 else "모델명 오류"
        )
except Exception as e:
    record_test("main_replit_improved.py 모델명", False, str(e))

# 5. max_tokens 확인
print_section("5. max_tokens 설정 확인")

try:
    with open("backend/main.py", "r", encoding="utf-8") as f:
        content = f.read()
        has_4096 = "max_tokens=4096" in content or "max_tokens = 4096" in content
        record_test(
            "main.py max_tokens",
            has_4096,
            "4096 토큰으로 설정" if has_4096 else "토큰 설정 확인 필요"
        )
except Exception as e:
    record_test("main.py max_tokens", False, str(e))

try:
    with open("backend/main_replit_improved.py", "r", encoding="utf-8") as f:
        content = f.read()
        has_4096 = "max_tokens=4096" in content or "max_tokens = 4096" in content
        record_test(
            "main_replit_improved.py max_tokens",
            has_4096,
            "4096 토큰으로 설정" if has_4096 else "토큰 설정 확인 필요"
        )
except Exception as e:
    record_test("main_replit_improved.py max_tokens", False, str(e))

# 6. 환경변수 확인
print_section("6. 환경 설정 확인")

env_file_exists = os.path.exists(".env")
record_test(".env 파일", env_file_exists, "파일 존재" if env_file_exists else "파일 없음 (시뮬레이션 모드)")

env_example_exists = os.path.exists("env.example")
record_test("env.example 파일", env_example_exists, "템플릿 존재" if env_example_exists else "템플릿 없음")

# 7. API 클라이언트 초기화 테스트
print_section("7. API 클라이언트 초기화 테스트")

try:
    import anthropic

    # API 키 없이 클라이언트 생성 테스트 (실패 예상)
    try:
        client = anthropic.Anthropic(api_key="test-key")
        record_test("Anthropic 클라이언트 생성", True, "클라이언트 객체 생성 성공")
    except Exception as e:
        record_test("Anthropic 클라이언트 생성", False, str(e))

except ImportError as e:
    record_test("Anthropic 라이브러리", False, f"import 실패: {str(e)}")

# 8. FastAPI 앱 import 테스트
print_section("8. FastAPI 앱 로드 테스트")

try:
    sys.path.insert(0, os.path.abspath("backend"))

    # main.py import 테스트
    try:
        from backend import main as main_module
        has_app = hasattr(main_module, 'app')
        record_test("main.py FastAPI 앱", has_app, "앱 객체 존재" if has_app else "앱 객체 없음")
    except Exception as e:
        record_test("main.py FastAPI 앱", False, f"import 오류: {str(e)}")

except Exception as e:
    record_test("FastAPI 앱 로드", False, str(e))

# 9. 문서 파일 확인
print_section("9. 문서 파일 확인")

doc_files = [
    "README.md",
    "CODE_REVIEW_SUMMARY.md",
    "CLAUDE_OPUS_4_1_UPGRADE.md"
]

for doc_file in doc_files:
    exists = os.path.exists(doc_file)
    record_test(f"{doc_file}", exists, "문서 존재" if exists else "문서 없음")

# ==================== 테스트 결과 요약 ====================

print_header("테스트 결과 요약")

print(f"총 테스트: {test_results['total']}")
print(f"{GREEN}✅ 성공: {test_results['passed']}{RESET}")
print(f"{RED}❌ 실패: {test_results['failed']}{RESET}")

success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
print(f"\n성공률: {success_rate:.1f}%")

if success_rate >= 80:
    print(f"\n{GREEN}{BOLD}🎉 테스트 통과! Claude Opus 4.1이 올바르게 설정되었습니다.{RESET}")
elif success_rate >= 60:
    print(f"\n{YELLOW}{BOLD}⚠️  일부 테스트 실패. 확인이 필요합니다.{RESET}")
else:
    print(f"\n{RED}{BOLD}❌ 많은 테스트 실패. 설정을 다시 확인해주세요.{RESET}")

print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 실패한 테스트가 있으면 상세 정보 출력
if test_results['failed'] > 0:
    print_header("실패한 테스트 상세")
    for test in test_results['tests']:
        if not test['passed']:
            print(f"{RED}❌ {test['name']}{RESET}")
            if test['message']:
                print(f"   └─ {test['message']}")

# 다음 단계 안내
print_header("다음 단계")

if not env_file_exists:
    print(f"{YELLOW}1. .env 파일 생성:{RESET}")
    print("   cp env.example .env")
    print("   # .env 파일을 열어 ANTHROPIC_API_KEY 설정")

print(f"\n{YELLOW}2. 서버 실행:{RESET}")
print("   python backend/main_replit_improved.py")

print(f"\n{YELLOW}3. 프론트엔드 실행:{RESET}")
print("   cd frontend")
print("   npm install")
print("   npm start")

print(f"\n{GREEN}4. 테스트 완료 후 사용 가능!{RESET}")

# 종료 코드 반환
sys.exit(0 if test_results['failed'] == 0 else 1)
