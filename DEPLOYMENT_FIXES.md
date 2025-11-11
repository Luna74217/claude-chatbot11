# 서버 배포 수정 사항

## 문제점

1. **`.replit` 파일 경로 오류**: `main:app`로 되어 있었지만 실제 앱은 `backend/main.py`에 위치
2. **포트 불일치**: `.replit`은 8000 포트, `backend/env_replit.txt`는 8080 포트 사용
3. **프론트엔드 API URL 미설정**: 환경 변수가 없어 백엔드 연결 불가
4. **Import 경로 문제**: `main_replit.py`가 잘못된 모듈을 import

## 수정 내용

### 1. `.replit` 파일 수정
- 변경 전: `run = ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]`
- 변경 후: `run = ["python", "main_replit.py"]`
- 배포 설정도 동일하게 수정

### 2. 포트 통일 (8000으로 통일)
- `main_replit.py`: 기본 포트를 8000으로 변경
- `backend/env_replit.txt`: PORT=8000으로 변경
- `.replit`: localPort=8000 유지

### 3. 환경 변수 파일 생성

#### `/home/user/claude-chatbot11/.env`
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=true
SECRET_KEY=your_secret_key_here
```

#### `/home/user/claude-chatbot11/frontend/.env`
```env
# 로컬 개발
REACT_APP_API_URL=http://localhost:8000

# Replit 배포 시 실제 백엔드 URL로 변경 필요
# REACT_APP_API_URL=https://your-backend-repl-url.repl.co
```

### 4. Import 경로 수정
- `main_replit.py`에서 `from backend.main_replit_improved import app`를 `from main import app`로 변경
- `sys.path.append('backend')`를 통해 backend 폴더를 Python 경로에 추가

## 배포 방법

### Replit에 배포하는 경우

1. **백엔드 URL 확인**
   - Replit에서 배포 후 백엔드 URL을 확인합니다 (예: `https://your-project.your-username.repl.co`)

2. **프론트엔드 환경 변수 설정**
   - `frontend/.env` 파일에서 `REACT_APP_API_URL`을 실제 백엔드 URL로 변경

3. **API 키 설정**
   - `backend/env_replit.txt` 또는 루트의 `.env` 파일에서 `ANTHROPIC_API_KEY`를 실제 API 키로 변경
   - Replit Secrets를 사용하는 것을 권장

4. **배포 실행**
   - Replit에서 "Run" 버튼 클릭
   - 또는 `python main_replit.py` 실행

### 로컬 개발

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **백엔드 실행**
   ```bash
   python main_replit.py
   ```

3. **프론트엔드 실행** (별도 터미널)
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 주의사항

- **API 키 보안**: `.env` 파일은 절대 git에 커밋하지 마세요 (이미 .gitignore에 추가됨)
- **CORS 설정**: `backend/main.py`에서 CORS가 모든 origin을 허용하도록 설정되어 있습니다. 프로덕션에서는 특정 도메인만 허용하도록 변경하세요.
- **포트 충돌**: 8000 포트가 이미 사용 중이면 `.env` 파일에서 다른 포트로 변경하세요.

## 테스트

배포 후 다음을 확인하세요:

1. 백엔드 health check: `http://your-backend-url/health`
2. WebSocket 연결: `ws://your-backend-url/ws`
3. 프론트엔드에서 메시지 전송 테스트

## 문제 해결

### Import 오류가 발생하는 경우
- `backend/main.py`의 상대 import를 확인
- `database_manager.py`, `stream_transformers.py` 등 필요한 모듈이 모두 있는지 확인

### WebSocket 연결 실패
- 프론트엔드 `.env`의 `REACT_APP_API_URL`이 올바른지 확인
- CORS 설정이 올바른지 확인
- 백엔드가 실행 중인지 확인

### API 응답 없음
- `ANTHROPIC_API_KEY`가 올바르게 설정되었는지 확인
- API 키가 유효한지 확인
