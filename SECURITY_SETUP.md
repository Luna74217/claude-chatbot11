# 🔐 시크릿 처리 및 보안 설정 가이드

## 🛡️ 보안 개선사항

### 1. 환경변수 관리
- API 키를 코드에서 분리
- `.env` 파일을 통한 안전한 설정 관리
- 환경변수 유효성 검사

### 2. CORS 보안 강화
- 허용된 도메인만 접근 가능
- HTTP 메서드 제한
- 자격 증명 보호

### 3. 로깅 보안
- API 키 마스킹
- 민감한 정보 로그 제외
- 구조화된 로깅

## 🚀 설정 방법

### 1. 환경변수 파일 생성

```bash
# backend/.env 파일 생성
cp backend/env_example.txt backend/.env
```

### 2. .env 파일 편집

```bash
# Claude API 설정
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-api-key-here

# 서버 설정
HOST=0.0.0.0
PORT=8000

# 보안 설정
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# CORS 설정 (쉼표로 구분)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 로깅 설정
LOG_LEVEL=INFO
```

### 3. API 키 생성

1. **Anthropic 웹사이트 접속**: https://console.anthropic.com/
2. **API 키 생성**: Settings → API Keys → Create Key
3. **키 복사**: 생성된 키를 `.env` 파일에 붙여넣기

### 4. 보안 키 생성

```bash
# Python에서 안전한 키 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🔒 보안 기능

### 1. API 키 검증
```python
def _get_api_key(self) -> str | None:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return None
    
    # API 키 형식 검증
    if not api_key.startswith('sk-ant-'):
        logger.error("❌ 잘못된 API 키 형식")
        return None
    
    # 로그에서 마스킹
    masked_key = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
    logger.info(f"🔑 API 키 로드됨: {masked_key}")
    
    return api_key
```

### 2. CORS 보안
```python
# 허용된 도메인만 접근
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. 로깅 보안
```python
# 구조화된 로깅
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📋 환경별 설정

### 개발 환경
```bash
# .env.development
ANTHROPIC_API_KEY=your-dev-api-key
DEBUG=True
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:3000
```

### 프로덕션 환경
```bash
# .env.production
ANTHROPIC_API_KEY=your-prod-api-key
DEBUG=False
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://yourdomain.com
```

## 🚨 보안 체크리스트

### ✅ 필수 확인사항

- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] API 키가 코드에 하드코딩되지 않음
- [ ] CORS 설정이 적절히 제한됨
- [ ] 디버그 모드가 프로덕션에서 비활성화됨
- [ ] 로그에 민감한 정보가 노출되지 않음

### ⚠️ 주의사항

1. **`.env` 파일을 절대 Git에 커밋하지 마세요**
2. **API 키를 공개 저장소에 업로드하지 마세요**
3. **프로덕션에서는 DEBUG=False로 설정하세요**
4. **정기적으로 API 키를 로테이션하세요**

## 🔧 문제 해결

### API 키 오류
```bash
# 키 형식 확인
echo $ANTHROPIC_API_KEY | head -c 10
# sk-ant-api0... 형식이어야 함
```

### CORS 오류
```bash
# 허용된 도메인 확인
echo $ALLOWED_ORIGINS
# 프론트엔드 도메인이 포함되어야 함
```

### 로그 레벨 조정
```bash
# 더 자세한 로그
LOG_LEVEL=DEBUG

# 최소한의 로그
LOG_LEVEL=ERROR
```

## 📚 추가 보안 팁

### 1. 환경변수 암호화
```bash
# 민감한 정보 암호화 (선택사항)
pip install cryptography
```

### 2. API 키 로테이션
- 정기적으로 API 키 재생성
- 이전 키 즉시 삭제
- 키 사용량 모니터링

### 3. 접근 제어
- IP 화이트리스트 설정
- 요청 빈도 제한
- 사용자 인증 추가

---

🔐 이제 안전하게 API 키를 관리하고 보안을 강화할 수 있습니다! 