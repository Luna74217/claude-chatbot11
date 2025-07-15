# 🚀 Claude UI 스트리밍 업그레이드 가이드

## ✨ 새로운 기능

### 🔄 실시간 스트리밍
- 메시지가 단어 단위로 실시간으로 표시됩니다
- 타이핑 인디케이터로 응답 생성 중임을 표시
- 자연스러운 타이핑 효과

### 🛑 스트리밍 취소
- 응답 생성 중 "중지" 버튼으로 취소 가능
- 서버에서 스트리밍 태스크 즉시 중단

### 🔧 두 가지 모드
1. **Claude API 모드**: 실제 Claude API 사용 (API 키 필요)
2. **시뮬레이션 모드**: API 키 없이도 테스트 가능

## 🚀 실행 방법

### 1. 백엔드 실행
```bash
cd backend
python main.py
```

### 2. 프론트엔드 실행
```bash
cd frontend
npm start
```

### 3. 브라우저에서 확인
- `http://localhost:3000` 접속
- WebSocket 연결 상태 확인
- 메시지 전송 테스트

## 🔑 Claude API 설정 (선택사항)

### 환경변수 설정
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# macOS/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

### .env 파일 생성
```bash
# backend/.env
ANTHROPIC_API_KEY=your_api_key_here
```

## 🧪 테스트 방법

### 1. 기본 테스트
- "안녕" 입력 → 시뮬레이션 응답
- "파이썬" 입력 → 파이썬 관련 응답
- "스트리밍" 입력 → 스트리밍 설명

### 2. 스트리밍 취소 테스트
- 긴 메시지 입력 후 "중지" 버튼 클릭
- 스트리밍이 즉시 중단되는지 확인

### 3. API 모드 테스트 (API 키 필요)
- 환경변수 설정 후 서버 재시작
- 실제 Claude API 응답 확인

## 📡 WebSocket 메시지 형식

### 클라이언트 → 서버
```json
{
  "type": "chat",
  "message": "사용자 메시지",
  "streaming": true
}
```

### 서버 → 클라이언트
```json
// 스트림 시작
{
  "type": "stream_start",
  "message_id": "msg_1234567890"
}

// 스트림 청크
{
  "type": "stream_chunk",
  "chunk": "텍스트 조각",
  "message_id": "msg_1234567890"
}

// 스트림 종료
{
  "type": "stream_end",
  "message_id": "msg_1234567890"
}
```

## 🔧 기술적 개선사항

### 백엔드
- **ConnectionManager**: 연결 관리 및 스트리밍 태스크 추적
- **StreamingClaude**: Claude API 통합 및 시뮬레이션
- **비동기 처리**: asyncio를 사용한 효율적인 스트리밍
- **에러 처리**: 연결 끊김, API 에러 등 처리

### 프론트엔드
- **실시간 업데이트**: 스트리밍 메시지 실시간 표시
- **상태 관리**: 스트리밍 상태 추적
- **UI 개선**: 타이핑 인디케이터, 취소 버튼
- **사용자 경험**: 스트리밍 중 입력 비활성화

## 🐛 문제 해결

### 연결 문제
1. 백엔드 서버가 실행 중인지 확인
2. WebSocket URL 확인 (`ws://localhost:8000/ws`)
3. 브라우저 콘솔에서 에러 메시지 확인

### API 키 문제
1. 환경변수 설정 확인
2. API 키 유효성 확인
3. 시뮬레이션 모드로 테스트

### 스트리밍 문제
1. 네트워크 연결 상태 확인
2. 브라우저 WebSocket 지원 확인
3. 서버 로그에서 에러 확인

## 📈 성능 최적화

- **메모리 효율성**: 스트리밍으로 메모리 사용량 최적화
- **응답 속도**: 실시간 표시로 사용자 경험 향상
- **연결 안정성**: 자동 재연결 및 에러 처리
- **확장성**: 다중 연결 지원 및 태스크 관리

---

🎉 이제 실시간 스트리밍을 지원하는 Claude UI를 즐겨보세요! 