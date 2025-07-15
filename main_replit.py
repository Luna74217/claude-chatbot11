#!/usr/bin/env python3
"""
Replit 환경용 Claude Chatbot 메인 실행 파일
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv('backend/env_replit.txt')

# 백엔드 모듈 경로 추가
sys.path.append('backend')

def main():
    """Replit 환경에서 서버 실행"""
    
    # 환경변수에서 설정 가져오기
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Claude Chatbot 서버 시작 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    print(f"🐛 디버그 모드: {debug}")
    
    # API 키 확인
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your_anthropic_api_key_here':
        print("⚠️  경고: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print("   backend/env_replit.txt 파일에서 API 키를 설정해주세요.")
    
    try:
        # FastAPI 앱 import
        from backend.main_replit_improved import app
        
        # 서버 실행
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            reload=debug
        )
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("   backend/main_replit_improved.py 파일이 존재하는지 확인해주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 