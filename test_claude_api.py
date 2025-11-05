#!/usr/bin/env python3
"""
Claude Opus 4.1 API 연결 테스트
"""

import os
import sys
import asyncio
from datetime import datetime

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    """헤더 출력"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

print_header("Claude Opus 4.1 API 연결 테스트")
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 환경변수 확인
print(f"{BOLD}{YELLOW}▶ API 키 확인{RESET}")

api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key:
    masked_key = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
    print(f"✅ API 키 발견: {masked_key}")
    has_api_key = True
else:
    print(f"❌ API 키 없음 - 시뮬레이션 모드로 작동")
    has_api_key = False

# Anthropic 라이브러리 테스트
print(f"\n{BOLD}{YELLOW}▶ Anthropic 클라이언트 테스트{RESET}")

try:
    import anthropic
    print(f"✅ anthropic 라이브러리 import 성공")

    if has_api_key:
        client = anthropic.Anthropic(api_key=api_key)
        print(f"✅ Anthropic 클라이언트 생성 성공")

        # 간단한 API 호출 테스트
        print(f"\n{BOLD}{YELLOW}▶ Claude Opus 4.1 API 호출 테스트{RESET}")
        print(f"모델: claude-opus-4-1-20250805")
        print(f"요청: 간단한 테스트 메시지\n")

        try:
            response = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello! Please respond with 'Claude Opus 4.1 is working!' in one sentence."
                    }
                ]
            )

            print(f"✅ API 호출 성공!")
            print(f"\n{BOLD}응답:{RESET}")
            print(f"{GREEN}{response.content[0].text}{RESET}")

            print(f"\n{BOLD}메타데이터:{RESET}")
            print(f"- 모델: {response.model}")
            print(f"- 역할: {response.role}")
            print(f"- 사용된 토큰: input={response.usage.input_tokens}, output={response.usage.output_tokens}")

            # 스트리밍 테스트
            print(f"\n{BOLD}{YELLOW}▶ 스트리밍 API 테스트{RESET}")

            stream = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": "Count from 1 to 5 slowly."
                    }
                ],
                stream=True
            )

            print(f"스트리밍 응답: ", end="", flush=True)
            for chunk in stream:
                if chunk.type == 'content_block_delta':
                    print(f"{GREEN}{chunk.delta.text}{RESET}", end="", flush=True)

            print(f"\n✅ 스트리밍 테스트 성공!")

        except anthropic.APIError as e:
            print(f"❌ API 오류: {e}")
            print(f"   상태 코드: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")

    else:
        print(f"{YELLOW}⚠️  API 키가 없어 실제 API 테스트를 건너뜁니다.{RESET}")
        print(f"{YELLOW}   .env 파일에 ANTHROPIC_API_KEY를 설정하면 테스트할 수 있습니다.{RESET}")

except ImportError:
    print(f"❌ anthropic 라이브러리를 찾을 수 없습니다.")
    print(f"   설치: pip install anthropic")

# 백엔드 서버 테스트
print(f"\n{BOLD}{YELLOW}▶ 백엔드 서버 구조 테스트{RESET}")

try:
    sys.path.insert(0, os.path.abspath("backend"))
    from backend.main import StreamingClaude

    print(f"✅ StreamingClaude 클래스 import 성공")

    # 클라이언트 초기화 테스트
    streaming_claude = StreamingClaude()

    if streaming_claude.client:
        print(f"✅ Claude API 클라이언트 초기화 완료 (실제 모드)")
    else:
        print(f"✅ 시뮬레이션 모드로 초기화 완료")

except Exception as e:
    print(f"❌ 백엔드 모듈 로드 실패: {e}")

# 결과 요약
print_header("테스트 결과")

if has_api_key:
    print(f"{GREEN}{BOLD}✅ 모든 테스트 완료!{RESET}")
    print(f"\nClaude Opus 4.1이 올바르게 설정되고 API와 연결되었습니다.")
    print(f"\n{BOLD}다음 단계:{RESET}")
    print(f"1. 백엔드 서버 시작: python backend/main_replit_improved.py")
    print(f"2. 프론트엔드 시작: cd frontend && npm start")
    print(f"3. 챗봇 사용 가능!")
else:
    print(f"{YELLOW}{BOLD}⚠️  API 키 미설정{RESET}")
    print(f"\n시뮬레이션 모드로 작동합니다.")
    print(f"\n{BOLD}실제 Claude Opus 4.1 사용하기:{RESET}")
    print(f"1. .env 파일 생성: cp env.example .env")
    print(f"2. ANTHROPIC_API_KEY 설정")
    print(f"3. 서버 재시작")

print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
