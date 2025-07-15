#!/usr/bin/env python3
"""
Replit 환경 설정 테스트 파일
"""

import os
import sys
from pathlib import Path

def test_environment():
    """환경 설정 테스트"""
    print("🔍 Replit 환경 설정 테스트 시작...")
    
    # 1. Python 버전 확인
    print(f"🐍 Python 버전: {sys.version}")
    
    # 2. 필요한 파일 존재 확인
    required_files = [
        "main_replit.py",
        "backend/main_replit_improved.py",
        "backend/requirements_replit.txt",
        "backend/env_replit.txt",
        "frontend/package_replit.json",
        "frontend/env_replit.txt",
        "frontend/src/App_replit.jsx",
        "frontend/src/components/ChatInterface/ChatInterface_replit.jsx",
        "frontend/src/hooks/useWebSocket_replit.js"
    ]
    
    print("\n📁 파일 존재 확인:")
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (누락)")
    
    # 3. 환경변수 확인
    print("\n🔧 환경변수 확인:")
    env_file = "backend/env_replit.txt"
    if Path(env_file).exists():
        print(f"✅ {env_file} 존재")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content:
                print("✅ ANTHROPIC_API_KEY 설정 확인")
            else:
                print("⚠️  ANTHROPIC_API_KEY 설정 필요")
    else:
        print(f"❌ {env_file} 누락")
    
    # 4. 모듈 import 테스트
    print("\n📦 모듈 import 테스트:")
    try:
        sys.path.append('backend')
        from main_replit_improved import app
        print("✅ FastAPI 앱 import 성공")
    except ImportError as e:
        print(f"❌ FastAPI 앱 import 실패: {e}")
    
    # 5. 의존성 확인
    print("\n📋 의존성 확인:")
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-dotenv',
        'anthropic',
        'websockets'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (설치 필요)")
    
    # 6. 포트 확인
    print("\n🔌 포트 설정 확인:")
    port = os.getenv('PORT', '8080')
    print(f"포트: {port}")
    
    # 7. Replit 환경 확인
    print("\n🌐 Replit 환경 확인:")
    if os.getenv('REPL_ID'):
        print("✅ Replit 환경에서 실행 중")
    else:
        print("⚠️  로컬 환경에서 실행 중 (Replit이 아님)")
    
    print("\n🎉 테스트 완료!")
    print("\n📝 다음 단계:")
    print("1. backend/env_replit.txt에서 API 키 설정")
    print("2. frontend/env_replit.txt에서 백엔드 URL 설정")
    print("3. python main_replit.py로 서버 실행")

if __name__ == "__main__":
    test_environment() 