# Replit 환경 설정 가이드

이 가이드는 Claude Chatbot 프로젝트를 Replit 환경에서 실행하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. Replit에서 새 프로젝트 생성
- Replit에서 새 Python 프로젝트를 생성합니다.
- 이 저장소의 파일들을 업로드하거나 복사합니다.

### 2. 환경변수 설정

#### 백엔드 환경변수 설정
`backend/env_replit.txt` 파일을 `.env`로 복사하고 설정을 수정합니다:

```bash
# Claude API 설정
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here

# Replit 서버 설정
HOST=0.0.0.0
PORT=8080

# 보안 설정
SECRET_KEY=your_secret_key_here
DEBUG=True

# CORS 설정 - Replit에서는 모든 origin 허용
ALLOWED_ORIGINS=*

# 로깅 설정
LOG_LEVEL=INFO
```

#### 프론트엔드 환경변수 설정
`frontend/env_replit.txt` 파일을 `frontend/.env`로 복사하고 설정을 수정합니다:

```bash
# 백엔드 API URL (실제 Replit URL로 변경)
REACT_APP_API_URL=https://your-actual-backend-repl-url.repl.co

# 개발 모드
REACT_APP_DEV_MODE=true
```

### 3. 의존성 설치

#### 백엔드 의존성 설치
```bash
pip install -r backend/requirements_replit.txt
```

#### 프론트엔드 의존성 설치
```bash
cd frontend
npm install
```

### 4. 서버 실행

#### 백엔드 서버 실행
```bash
python main_replit.py
```

#### 프론트엔드 개발 서버 실행 (별도 터미널)
```bash
cd frontend
npm start
```

## 📁 프로젝트 구조

```
claude-chatbot/
├── main_replit.py              # Replit 메인 실행 파일
├── backend/
│   ├── main_replit_improved.py # FastAPI 백엔드
│   ├── requirements_replit.txt # Python 의존성
│   └── env_replit.txt         # 환경변수 예제
├── frontend/
│   ├── src/
│   │   ├── App_replit.jsx     # Replit용 React 앱
│   │   ├── components/
│   │   │   └── ChatInterface/
│   │   │       └── ChatInterface_replit.jsx
│   │   └── hooks/
│   │       └── useWebSocket_replit.js
│   ├── package_replit.json    # Node.js 의존성
│   └── env_replit.txt        # 환경변수 예제
└── REPLIT_SETUP_GUIDE.md     # 이 파일
```

## 🔧 주요 설정 사항

### 1. 포트 설정
- Replit에서는 기본적으로 8080 포트를 사용합니다.
- `backend/env_replit.txt`에서 `PORT=8080`으로 설정되어 있습니다.

### 2. CORS 설정
- Replit 환경에서는 모든 origin을 허용하도록 설정되어 있습니다.
- `ALLOWED_ORIGINS=*`로 설정되어 있습니다.

### 3. WebSocket 연결
- Replit URL을 자동으로 감지하여 WebSocket 연결을 설정합니다.
- `frontend/src/hooks/useWebSocket_replit.js`에서 처리됩니다.

### 4. API 키 설정
- Anthropic API 키를 `backend/env_replit.txt`에 설정해야 합니다.
- API 키가 없으면 경고 메시지가 표시됩니다.

## 🐛 문제 해결

### 1. 모듈 import 오류
```bash
# 백엔드 모듈 경로가 올바른지 확인
python -c "import sys; print(sys.path)"
```

### 2. WebSocket 연결 실패
- 브라우저 콘솔에서 WebSocket URL을 확인합니다.
- Replit URL이 올바른지 확인합니다.

### 3. API 키 오류
- Anthropic API 키가 올바르게 설정되었는지 확인합니다.
- API 키에 충분한 크레딧이 있는지 확인합니다.

### 4. 포트 충돌
- Replit에서 다른 프로세스가 8080 포트를 사용하고 있는지 확인합니다.
- 필요시 다른 포트로 변경합니다.

## 📝 추가 설정

### 1. Replit 데이터베이스 사용 (선택사항)
```bash
# Replit 데이터베이스 URL 설정
REPLIT_DB_URL=your_replit_db_url_here
```

### 2. 로깅 레벨 조정
```bash
# 더 자세한 로그를 원하는 경우
LOG_LEVEL=DEBUG
```

### 3. 개발 모드 설정
```bash
# 개발 모드 활성화
DEBUG=True
```

## 🚀 배포

### 1. Replit에서 실행
- `main_replit.py` 파일을 실행하면 백엔드 서버가 시작됩니다.
- 프론트엔드는 별도로 `npm start`로 실행할 수 있습니다.

### 2. 외부 접근
- Replit에서 제공하는 URL을 통해 외부에서 접근할 수 있습니다.
- WebSocket 연결도 자동으로 설정됩니다.

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. 환경변수가 올바르게 설정되었는지
2. 의존성이 모두 설치되었는지
3. API 키가 유효한지
4. Replit 콘솔에서 오류 메시지를 확인

---

**참고**: 이 가이드는 Replit 환경에 최적화되어 있습니다. 로컬 환경에서는 다른 설정이 필요할 수 있습니다. 