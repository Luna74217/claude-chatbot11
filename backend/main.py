# 🔧 main_replit.py 스트리밍 업그레이드 버전
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import time
from typing import Dict, Set
import anthropic
import os
from dotenv import load_dotenv
import secrets
import logging
from database_manager import db_manager

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정 (보안 강화)
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
# 활성 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.streaming_tasks: Dict[WebSocket, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ 새 연결: {len(self.active_connections)}개 활성")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        # 진행 중인 스트리밍 취소
        if websocket in self.streaming_tasks:
            self.streaming_tasks[websocket].cancel()
            del self.streaming_tasks[websocket]
        print(f"🔌 연결 해제: {len(self.active_connections)}개 활성")
    
    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_text(json.dumps(data))

manager = ConnectionManager()

# Claude 스트리밍 래퍼
class StreamingClaude:
    def __init__(self):
        self.api_key = self._get_api_key()
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("✅ Claude API 클라이언트 초기화 완료")
        else:
            self.client = None
            logger.warning("⚠️ ANTHROPIC_API_KEY 없음 - 시뮬레이션 모드")
    
    def _get_api_key(self) -> str | None:
        """안전한 API 키 가져오기"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None
        
        # API 키 유효성 검사 (기본적인 형식 확인)
        if not api_key.startswith('sk-ant-'):
            logger.error("❌ 잘못된 API 키 형식")
            return None
        
        # API 키 마스킹 (로그에서 보안)
        masked_key = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
        logger.info(f"🔑 API 키 로드됨: {masked_key}")
        
        return api_key
    
    def _validate_input(self, message: str) -> bool:
        """사용자 입력 검증"""
        if not message or not isinstance(message, str):
            return False
        
        # 메시지 길이 제한 (10,000자)
        if len(message) > 10000:
            return False
        
        # 위험한 문자나 패턴 차단
        dangerous_patterns = [
            '<script', 'javascript:', 'data:', 'vbscript:',
            'onload=', 'onerror=', 'onclick=', 'eval(',
            'document.cookie', 'localStorage', 'sessionStorage'
        ]
        
        message_lower = message.lower()
        for pattern in dangerous_patterns:
            if pattern in message_lower:
                logger.warning(f"🚫 위험한 입력 감지: {pattern}")
                return False
        
        return True
    
    async def stream_response(self, message: str, websocket: WebSocket):
        """실제 Claude API 스트리밍 또는 시뮬레이션"""
        
        # 입력 검증
        if not self._validate_input(message):
            await manager.send_json(websocket, {
                "type": "error",
                "error": "잘못된 입력입니다.",
                "message_id": None
            })
            return
        
        message_id = f"msg_{int(time.time() * 1000)}"
        
        # 스트림 시작 알림
        await manager.send_json(websocket, {
            "type": "stream_start",
            "message_id": message_id
        })
        
        try:
            if self.client:
                # 실제 Claude API 스트리밍
                stream = self.client.messages.create(
                    model="claude-3-opus-4-20250514",
                    messages=[{"role": "user", "content": message}],
                    max_tokens=1024,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.type == 'content_block_delta':
                        text = chunk.delta.text
                        if text:
                            await manager.send_json(websocket, {
                                "type": "stream_chunk",
                                "chunk": text,
                                "message_id": message_id
                            })
                            # 자연스러운 타이핑 효과
                            await asyncio.sleep(0.02)
            else:
                # 시뮬레이션 모드 - 더 현실적으로 개선
                simulated_response = self._generate_simulated_response(message)
                
                # 단어 단위로 스트리밍
                words = simulated_response.split(' ')
                for i, word in enumerate(words):
                    # 마지막 단어가 아니면 공백 추가
                    chunk = word + (' ' if i < len(words) - 1 else '')
                    
                    await manager.send_json(websocket, {
                        "type": "stream_chunk",
                        "chunk": chunk,
                        "message_id": message_id
                    })
                    
                    # 가변적인 딜레이 (더 자연스럽게)
                    delay = 0.05 + (0.1 if ',' in word or '.' in word else 0)
                    await asyncio.sleep(delay)
        
        except asyncio.CancelledError:
            # 스트리밍 취소됨
            await manager.send_json(websocket, {
                "type": "stream_cancelled",
                "message_id": message_id
            })
            raise
        
        except Exception as e:
            # 에러 처리 (민감한 정보 노출 방지)
            error_message = "서버 오류가 발생했습니다."
            if os.getenv('DEBUG', 'False').lower() == 'true':
                error_message = str(e)
            
            logger.error(f"❌ 스트리밍 에러: {str(e)}")
            await manager.send_json(websocket, {
                "type": "error",
                "error": error_message,
                "message_id": message_id
            })
            raise
        
        finally:
            # 스트림 종료
            await manager.send_json(websocket, {
                "type": "stream_end",
                "message_id": message_id
            })
    
    def _generate_simulated_response(self, message: str) -> str:
        """시뮬레이션용 응답 생성 (더 다양하게)"""
        responses = {
            "안녕": "안녕하세요! 무엇을 도와드릴까요? 저는 Claude입니다. 프로그래밍, 분석, 창의적인 작업 등 다양한 분야에서 도움을 드릴 수 있어요.",
            "파이썬": "파이썬은 배우기 쉽고 강력한 프로그래밍 언어입니다. 웹 개발부터 데이터 과학, 인공지능까지 다양한 분야에서 사용됩니다. 특히 간결한 문법과 풍부한 라이브러리가 장점이죠.",
            "스트리밍": "스트리밍은 데이터를 한 번에 모두 받지 않고 조금씩 받아서 처리하는 방식입니다. 사용자 경험이 향상되고 메모리 효율도 좋아집니다.",
        }
        
        # 키워드 매칭
        for keyword, response in responses.items():
            if keyword in message.lower():
                return response
        
        # 기본 응답
        return f"'{message}'에 대한 제 생각은 이렇습니다: 흥미로운 질문이네요! 이 주제에 대해 더 자세히 알아보면 좋을 것 같습니다. 구체적으로 어떤 부분이 궁금하신가요?"

claude_streamer = StreamingClaude()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "")
                streaming = message_data.get("streaming", False)
                
                print(f"📨 메시지 수신: {user_message[:50]}... (스트리밍: {streaming})")
                
                if streaming:
                    # 스트리밍 태스크 생성
                    task = asyncio.create_task(
                        claude_streamer.stream_response(user_message, websocket)
                    )
                    manager.streaming_tasks[websocket] = task
                    
                    # 태스크 완료 대기 (취소 가능)
                    try:
                        await task
                    except asyncio.CancelledError:
                        print("🛑 스트리밍 취소됨")
                    finally:
                        if websocket in manager.streaming_tasks:
                            del manager.streaming_tasks[websocket]
                else:
                    # 기존 방식 (하위 호환성)
                    response = "기존 방식의 응답입니다. 스트리밍을 활성화하려면 streaming: true를 설정하세요."
                    await manager.send_json(websocket, {
                        "type": "message",
                        "content": response,
                        "role": "assistant"
                    })
            
            elif message_data.get("type") == "cancel_stream":
                # 스트리밍 취소 요청
                if websocket in manager.streaming_tasks:
                    manager.streaming_tasks[websocket].cancel()
                    print("🛑 클라이언트가 스트리밍 취소 요청")
            
            elif message_data.get("type") == "ping":
                # 연결 상태 확인
                await manager.send_json(websocket, {"type": "pong"})
    
    except WebSocketDisconnect:
        print("🔌 WebSocket 연결 끊김")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        manager.disconnect(websocket)

# 상태 확인 엔드포인트
@app.get("/")
async def root():
    return {
        "status": "running",
        "mode": "streaming" if claude_streamer.client else "simulation",
        "active_connections": len(manager.active_connections),
        "features": [
            "Real-time streaming",
            "Cancel support",
            "Auto-reconnect",
            "Claude API integration"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "connections": len(manager.active_connections)
    }

# ===== 🗄️ Replit Database API 엔드포인트 =====

@app.get("/api/database/stats")
async def get_database_stats():
    """데이터베이스 통계 조회"""
    try:
        stats = db_manager.get_database_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 데이터베이스 통계 조회 실패: {e}")
        return {
            "success": False,
            "error": "데이터베이스 통계 조회 실패",
            "timestamp": time.time()
        }

@app.get("/api/database/sessions")
async def get_all_sessions():
    """모든 세션 조회"""
    try:
        sessions = db_manager.get_all_sessions()
        return {
            "success": True,
            "data": {
                "sessions": sessions,
                "count": len(sessions)
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 세션 조회 실패: {e}")
        return {
            "success": False,
            "error": "세션 조회 실패",
            "timestamp": time.time()
        }

@app.get("/api/database/sessions/{session_id}")
async def get_session_data(session_id: str):
    """특정 세션 데이터 조회"""
    try:
        session_data = db_manager.get_session(session_id)
        if session_data:
            return {
                "success": True,
                "data": session_data,
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "error": "세션을 찾을 수 없습니다",
                "timestamp": time.time()
            }
    except Exception as e:
        logger.error(f"❌ 세션 데이터 조회 실패: {e}")
        return {
            "success": False,
            "error": "세션 데이터 조회 실패",
            "timestamp": time.time()
        }

@app.get("/api/database/memories")
async def get_all_memories():
    """모든 메모리 조회"""
    try:
        memories = db_manager.get_all_memories()
        return {
            "success": True,
            "data": {
                "memories": memories,
                "count": len(memories)
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 메모리 조회 실패: {e}")
        return {
            "success": False,
            "error": "메모리 조회 실패",
            "timestamp": time.time()
        }

@app.get("/api/database/memories/{session_id}")
async def get_memory_data(session_id: str):
    """특정 세션의 메모리 데이터 조회"""
    try:
        memory_data = db_manager.get_context_memory(session_id)
        if memory_data:
            return {
                "success": True,
                "data": memory_data,
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "error": "메모리를 찾을 수 없습니다",
                "timestamp": time.time()
            }
    except Exception as e:
        logger.error(f"❌ 메모리 데이터 조회 실패: {e}")
        return {
            "success": False,
            "error": "메모리 데이터 조회 실패",
            "timestamp": time.time()
        }

@app.delete("/api/database/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        db_manager.delete_session(session_id)
        return {
            "success": True,
            "message": "세션이 삭제되었습니다",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 세션 삭제 실패: {e}")
        return {
            "success": False,
            "error": "세션 삭제 실패",
            "timestamp": time.time()
        }

@app.delete("/api/database/memories/{session_id}")
async def delete_memory(session_id: str):
    """메모리 삭제"""
    try:
        db_manager.delete_context_memory(session_id)
        return {
            "success": True,
            "message": "메모리가 삭제되었습니다",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 메모리 삭제 실패: {e}")
        return {
            "success": False,
            "error": "메모리 삭제 실패",
            "timestamp": time.time()
        }

@app.post("/api/database/cleanup")
async def cleanup_old_data(days: int = 30):
    """오래된 데이터 정리"""
    try:
        deleted_count = db_manager.cleanup_old_data(days)
        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count,
                "days": days
            },
            "message": f"{deleted_count}개의 오래된 데이터가 정리되었습니다",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 데이터 정리 실패: {e}")
        return {
            "success": False,
            "error": "데이터 정리 실패",
            "timestamp": time.time()
        }

@app.get("/api/database/export")
async def export_all_data():
    """모든 데이터 내보내기"""
    try:
        data = db_manager.export_all_data()
        return {
            "success": True,
            "data": data,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ 데이터 내보내기 실패: {e}")
        return {
            "success": False,
            "error": "데이터 내보내기 실패",
            "timestamp": time.time()
        }

if __name__ == "__main__":
    import uvicorn
    
    # 서버 설정
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 스트리밍 지원 서버 시작...")
    logger.info(f"📡 WebSocket: ws://{host}:{port}/ws")
    logger.info(f"🔧 모드: {'Claude API' if claude_streamer.client else '시뮬레이션'}")
    logger.info(f"🌐 CORS 허용 도메인: {allowed_origins}")
    
    if debug:
        logger.warning("⚠️ 디버그 모드 활성화 - 프로덕션에서는 비활성화하세요")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )