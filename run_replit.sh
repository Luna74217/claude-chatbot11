#!/bin/bash

# Replit 환경용 Claude Chatbot 실행 스크립트

echo "🚀 Claude Chatbot Replit 실행 스크립트"
echo "======================================"

# 1. 환경 설정 확인
echo "📋 환경 설정 확인 중..."
python test_replit_setup.py

# 2. 의존성 설치 확인
echo ""
echo "📦 의존성 설치 확인 중..."
if [ -f "backend/requirements_replit.txt" ]; then
    echo "Python 의존성 설치 중..."
    pip install -r backend/requirements_replit.txt
else
    echo "❌ backend/requirements_replit.txt 파일이 없습니다."
    exit 1
fi

# 3. 환경변수 파일 확인
echo ""
echo "🔧 환경변수 설정 확인 중..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/env_replit.txt" ]; then
        echo "환경변수 파일을 복사합니다..."
        cp backend/env_replit.txt backend/.env
        echo "⚠️  backend/.env 파일에서 API 키를 설정해주세요."
    else
        echo "❌ 환경변수 파일이 없습니다."
        exit 1
    fi
fi

# 4. 서버 실행
echo ""
echo "🌐 서버 시작 중..."
echo "서버가 시작되면 Replit에서 제공하는 URL로 접속할 수 있습니다."
echo ""

python main_replit.py 