# Claude Chatbot - Replit 버전

Replit 환경에서 실행할 수 있도록 최적화된 Claude Chatbot입니다.

## 🚀 빠른 시작

### 1. Replit에서 실행
```bash
# 환경 설정 테스트
python test_replit_setup.py

# 서버 실행
python main_replit.py
```

### 2. 환경변수 설정
`backend/env_replit.txt` 파일을 `.env`로 복사하고 API 키를 설정하세요:
```bash
cp backend/env_replit.txt backend/.env
# .env 파일에서 ANTHROPIC_API_KEY를 실제 키로 변경
```

## 📁 프로젝트 구조

```
├── main_replit.py                    # Replit 메인 실행 파일
├── test_replit_setup.py             # 환경 설정 테스트
├── run_replit.sh                    # 실행 스크립트
├── backend/
│   ├── main_replit_improved.py      # FastAPI 백엔드
│   ├── requirements_replit.txt      # Python 의존성
│   └── env_replit.txt              # 환경변수 예제
├── frontend/
│   ├── src/
│   │   ├── App_replit.jsx          # Replit용 React 앱
│   │   ├── components/
│   │   │   └── ChatInterface/
│   │   │       └── ChatInterface_replit.jsx
│   │   └── hooks/
│   │       └── useWebSocket_replit.js
│   ├── package_replit.json         # Node.js 의존성
│   └── env_replit.txt             # 환경변수 예제
└── REPLIT_SETUP_GUIDE.md          # 상세 설정 가이드
```

## 🔧 주요 기능

### 백엔드 (FastAPI)
- ✅ WebSocket 실시간 채팅
- ✅ Claude API 연동
- ✅ 파일 업로드 지원
- ✅ 컨텍스트 관리
- ✅ AI 페르소나 시스템
- ✅ 스트림 변환기

### 프론트엔드 (React)
- ✅ 실시간 채팅 인터페이스
- ✅ 다크/라이트 모드
- ✅ 파일 드래그 앤 드롭
- ✅ 대화 히스토리 관리
- ✅ 검색 기능
- ✅ 반응형 디자인

## 🛠️ 설정

### 1. API 키 설정
```bash
# backend/.env 파일에서
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 2. 포트 설정
```bash
# backend/.env 파일에서
PORT=8080  # Replit 기본 포트
```

### 3. CORS 설정
```bash
# backend/.env 파일에서
ALLOWED_ORIGINS=*  # Replit에서는 모든 origin 허용
```

## 🚀 실행 방법

### 방법 1: 직접 실행
```bash
python main_replit.py
```

### 방법 2: 스크립트 실행
```bash
chmod +x run_replit.sh
./run_replit.sh
```

### 방법 3: 테스트 후 실행
```bash
python test_replit_setup.py
python main_replit.py
```

## 🌐 접속

서버가 실행되면 Replit에서 제공하는 URL로 접속할 수 있습니다:
- 백엔드 API: `https://your-repl-url.repl.co`
- 프론트엔드: `https://your-repl-url.repl.co` (별도 설정 필요)

## 🔍 문제 해결

### 1. 모듈 import 오류
```bash
# 의존성 설치 확인
pip install -r backend/requirements_replit.txt
```

### 2. API 키 오류
```bash
# 환경변수 파일 확인
cat backend/.env
```

### 3. WebSocket 연결 실패
- 브라우저 콘솔에서 오류 확인
- Replit URL이 올바른지 확인

### 4. 포트 충돌
```bash
# 포트 변경
# backend/.env에서 PORT=8081로 변경
```

## 📝 추가 정보

- **상세 설정 가이드**: `REPLIT_SETUP_GUIDE.md`
- **프로젝트 상태**: `PROJECT_STATUS.md`
- **개선 사항**: `IMPROVEMENTS_SUMMARY.txt`

## 🤝 기여

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**참고**: 이 버전은 Replit 환경에 최적화되어 있습니다. 로컬 환경에서는 다른 설정이 필요할 수 있습니다. 