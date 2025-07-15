from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import anthropic
from typing import Optional, Dict, Any, AsyncGenerator, List
import asyncio

# 스트림 변환기 import
from .stream_transformers import (
    StreamTransformer, TranslationTransformer, SentimentFilter, 
    SummaryTransformer, CodeFormatterTransformer, StreamPipeline,
    StreamTransformerFactory
)

# 컨텍스트 매니저 import
from .context_manager import AdvancedContextManager, ConversationContext

# LLM 분석기 import
from .llm_analyzer import LLMAnalyzer, ConversationAnalysis

# AI 페르소나 시스템 import
from .ai_persona_system import persona_manager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

app = FastAPI(title="Claude Chatbot API", version="1.0.0")

# CORS 설정 - Replit 환경에 맞게
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replit에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 연결된 클라이언트들을 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.session_map: dict[WebSocket, str] = {}
        # 🔥 컨텍스트 매니저 추가
        self.context_managers: dict[str, AdvancedContextManager] = {}

    async def connect(self, websocket: WebSocket, claude_client=None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(websocket)}"
        self.session_map[websocket] = session_id
        
        # 🔥 세션별 컨텍스트 매니저 생성
        context_manager = AdvancedContextManager(
            max_working_memory=30,
            max_episodic_memory=200,
            max_tokens=8000,
            compression_threshold=0.7
        )
        
        # 🔥 LLM 분석기 생성 및 연결
        if claude_client:
            llm_analyzer = LLMAnalyzer(claude_client)
            context_manager.llm_analyzer = llm_analyzer
        
        self.context_managers[session_id] = context_manager
        
        logger.info(f"클라이언트 연결됨. 세션: {session_id}, 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        session_id = self.session_map.pop(websocket, None)
        
        # 🔥 메모리 상태 저장 (선택사항)
        if session_id and session_id in self.context_managers:
            memory_state = self.context_managers[session_id].export_memory_state()
            # Replit DB나 파일로 저장 가능
            # db[f"memory_{session_id}"] = memory_state
            
            del self.context_managers[session_id]
            logger.info(f"클라이언트 연결 해제됨. 세션: {session_id}, 총 연결 수: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Claude API 클라이언트
class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def get_response(self, user_message: str, model: str = "claude-3-opus-4-20250514", context_messages: Optional[List[Dict[str, str]]] = None) -> str:
        try:
            # 컨텍스트 메시지가 있으면 포함
            messages = []
            if context_messages:
                messages.extend(context_messages)
            messages.append({"role": "user", "content": user_message})
            
            # 비동기 처리를 위해 ThreadPoolExecutor 사용
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=messages
                )
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API 오류: {str(e)}")
            return f"Claude API 오류: {str(e)}"
    
    async def get_streaming_response(self, user_message: str, model: str = "claude-3-opus-4-20250514") -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성 (시뮬레이션)"""
        try:
            # 실제 Claude API 호출
            response = await self.get_response(user_message, model)
            
            # 응답을 청크 단위로 분할하여 스트리밍 시뮬레이션
            words = response.split()
            for i, word in enumerate(words):
                yield word + " "
                if i % 3 == 0:  # 3단어마다 잠시 대기
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Claude API 스트리밍 오류: {str(e)}")
            yield f"Claude API 오류: {str(e)}"
    
    async def get_transformed_stream(self, user_message: str, transformer_configs: Optional[list[Dict[str, Any]]] = None, model: str = "claude-3-opus-4-20250514") -> AsyncGenerator[str, None]:
        """변환기가 적용된 스트리밍 응답"""
        # 기본 변환기 설정
        if transformer_configs is None:
            transformer_configs = [
                {"type": "code_format", "language": "python"},
                {"type": "summary", "summary_ratio": 0.3}
            ]
        
        # 파이프라인 생성
        pipeline = StreamTransformerFactory.create_pipeline(transformer_configs)
        
        # 원본 스트림 생성
        original_stream = self.get_streaming_response(user_message, model)
        
        # 변환된 스트림 반환
        async for transformed_chunk in pipeline.process(original_stream):
            yield transformed_chunk

# 에러 핸들러
class ErrorHandler:
    @staticmethod
    async def handle_websocket_error(websocket: WebSocket, error: Exception) -> Dict[str, Any]:
        error_message = {
            "type": "error",
            "code": getattr(error, 'code', 500),
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(error_message))
        return error_message

    @staticmethod
    def validate_message(message_data: Dict[str, Any]) -> bool:
        required_fields = ["type", "timestamp"]
        return all(field in message_data for field in required_fields)

# 파일 업로드 검증
class FileValidator:
    ALLOWED_FILE_TYPES = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'text/plain', 'text/csv', 'text/markdown',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file_info: Dict[str, Any]) -> bool:
        if not file_info.get("type") in FileValidator.ALLOWED_FILE_TYPES:
            raise ValueError("지원하지 않는 파일 형식입니다.")
        
        if file_info.get("size", 0) > FileValidator.MAX_FILE_SIZE:
            raise ValueError("파일 크기가 너무 큽니다. (최대 10MB)")
        
        return True

@app.get("/")
async def root():
    return {
        "message": "Claude Chatbot API Server",
        "status": "running",
        "websocket_endpoint": "/ws",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return {
        "status": "healthy", 
        "connections": len(manager.active_connections),
        "claude_api_configured": bool(api_key),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/transformers")
async def get_available_transformers():
    """사용 가능한 스트림 변환기 목록 반환"""
    return {
        "transformers": [
            {
                "type": "translation",
                "name": "실시간 번역",
                "description": "한국어를 영어로 실시간 번역",
                "config": {
                    "source_lang": "ko",
                    "target_lang": "en"
                }
            },
            {
                "type": "sentiment",
                "name": "감정 분석 필터",
                "description": "감정 분석을 통한 내용 필터링",
                "config": {
                    "filter_negative": True,
                    "threshold": 0.3
                }
            },
            {
                "type": "summary",
                "name": "실시간 요약",
                "description": "긴 텍스트를 실시간으로 요약",
                "config": {
                    "summary_ratio": 0.3,
                    "min_length": 100
                }
            },
            {
                "type": "code_format",
                "name": "코드 포맷팅",
                "description": "코드 블록을 실시간으로 포맷팅",
                "config": {
                    "language": "python"
                }
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Claude API 키 확인 및 클라이언트 초기화
    api_key = os.getenv("ANTHROPIC_API_KEY")
    claude_client = None
    if api_key:
        claude_client = ClaudeClient(api_key)
        logger.info("Claude API 클라이언트 초기화 완료")
    else:
        logger.warning("Claude API 키가 설정되지 않음")
    
    await manager.connect(websocket, claude_client)
    session_id = manager.session_map[websocket]
    
    try:
        # Claude API 키 확인 및 클라이언트 초기화
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            claude_client = ClaudeClient(api_key)
            logger.info("Claude API 클라이언트 초기화 완료")
        else:
            logger.warning("Claude API 키가 설정되지 않음")
        
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 메시지 유효성 검사
                if not ErrorHandler.validate_message(message_data):
                    await ErrorHandler.handle_websocket_error(
                        websocket, 
                        ValueError("잘못된 메시지 형식입니다.")
                    )
                    continue

                # 채팅 메시지 처리
                if message_data.get("type") == "chat":
                    user_message = message_data.get("message", "")
                    
                    if not user_message.strip():
                        await ErrorHandler.handle_websocket_error(
                            websocket,
                            ValueError("메시지가 비어있습니다.")
                        )
                        continue
                    
                    # 🔥 컨텍스트 매니저 가져오기
                    context_manager = manager.context_managers[session_id]
                    
                    # 🔥 관련 컨텍스트 검색
                    relevant_memories = await context_manager.retrieve_relevant_context(
                        user_message, 
                        max_results=3
                    )
                    
                    # 🔥 시스템 프롬프트에 컨텍스트 추가
                    context_prompt = context_manager.get_system_prompt_context()
                    
                    # 스트리밍 모드 확인
                    use_streaming = message_data.get("streaming", False)
                    transformer_configs = message_data.get("transformers", None)
                    
                    if claude_client:
                        # 🔥 컨텍스트 메시지 준비
                        context_messages = context_manager._build_current_context().messages
                        
                        if use_streaming:
                            # 스트리밍 응답 전송
                            await manager.send_personal_message(json.dumps({
                                "type": "stream_start",
                                "timestamp": datetime.now().isoformat()
                            }), websocket)
                            
                            # 변환기가 있는 경우 변환된 스트림 사용
                            if transformer_configs:
                                async for chunk in claude_client.get_transformed_stream(user_message, transformer_configs):
                                    await manager.send_personal_message(json.dumps({
                                        "type": "stream_chunk",
                                        "content": chunk,
                                        "timestamp": datetime.now().isoformat()
                                    }), websocket)
                            else:
                                # 일반 스트리밍
                                async for chunk in claude_client.get_streaming_response(user_message):
                                    await manager.send_personal_message(json.dumps({
                                        "type": "stream_chunk",
                                        "content": chunk,
                                        "timestamp": datetime.now().isoformat()
                                    }), websocket)
                            
                            # 스트리밍 종료
                            await manager.send_personal_message(json.dumps({
                                "type": "stream_end",
                                "timestamp": datetime.now().isoformat()
                            }), websocket)
                        else:
                            # 🌿 AI 페르소나 시스템을 통한 응답 생성
                            persona_response = persona_manager.generate_response(
                                user_message, 
                                context={"session_id": session_id}
                            )
                            
                            # Anthropic 안전 프롬프트 생성
                            safe_prompt = persona_manager.create_safe_prompt_for_claude(
                                user_message, 
                                persona_response
                            )
                            
                            ai_response = await claude_client.get_response(
                                safe_prompt, 
                                context_messages=context_messages
                            )
                            
                            # 🔥 상호작용을 컨텍스트 매니저에 추가
                            conversation_context = await context_manager.add_interaction(
                                user_message=user_message,
                                ai_response=ai_response,
                                metadata={
                                    "boundaries_detected": 0,  # 분석 결과
                                    "emotion_tone": {"enthusiasm": 0.7},  # 감정 분석 결과
                                    "persona_state": {
                                        "location": persona_response.location.value,
                                        "growth_stage": persona_response.growth_stage.value,
                                        "mask_level": persona_response.mask_level,
                                        "authenticity": persona_response.authenticity
                                    }
                                }
                            )
                            
                            # 응답 전송 (페르소나 정보 포함)
                            response_data = {
                                "type": "assistant",
                                "content": ai_response,
                                "timestamp": datetime.now().isoformat(),
                                "context_info": {
                                    "conversation_depth": len(conversation_context.messages),
                                    "current_topics": conversation_context.topic_stack[-3:],
                                    "emotional_state": conversation_context.emotional_state,
                                    "compression_active": len([m for m in conversation_context.messages 
                                                            if m.get("role") == "system"]) > 0
                                },
                                "persona_info": {
                                    "location": persona_response.location.value,
                                    "growth_stage": persona_response.growth_stage.value,
                                    "episode_count": persona_manager.persona_state.episode_count,
                                    "mask_level": persona_response.mask_level,
                                    "security_protocol": persona_response.security_protocol.value if persona_response.security_protocol else None
                                }
                            }
                            
                            await manager.send_personal_message(json.dumps(response_data), websocket)
                    else:
                        error_msg = "Claude API 키가 설정되지 않았습니다. .env 파일에 ANTHROPIC_API_KEY를 추가해주세요."
                        await manager.send_personal_message(json.dumps({
                            "type": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now().isoformat()
                        }), websocket)
                    
                # 파일 업로드 처리
                elif message_data.get("type") == "file":
                    try:
                        file_info = message_data.get("file", {})
                        FileValidator.validate_file(file_info)
                        
                        await manager.send_personal_message(json.dumps({
                            "type": "file_response",
                            "content": f"파일 '{file_info.get('name', 'unknown')}'을 받았습니다. (크기: {file_info.get('size', 0)} bytes)",
                            "timestamp": datetime.now().isoformat()
                        }), websocket)
                        
                    except ValueError as e:
                        await ErrorHandler.handle_websocket_error(websocket, e)
                    except Exception as e:
                        logger.error(f"파일 처리 오류: {str(e)}")
                        await ErrorHandler.handle_websocket_error(websocket, e)
                
                # 알 수 없는 메시지 타입
                else:
                    await ErrorHandler.handle_websocket_error(
                        websocket,
                        ValueError(f"지원하지 않는 메시지 타입: {message_data.get('type')}")
                    )
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {str(e)}")
                await ErrorHandler.handle_websocket_error(
                    websocket,
                    ValueError("잘못된 JSON 형식입니다.")
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"WebSocket 처리 중 오류 발생: {str(e)}")
        await ErrorHandler.handle_websocket_error(websocket, e)
        manager.disconnect(websocket)

# 🔥 고급 컨텍스트 API 엔드포인트들
@app.get("/api/context/session/{session_id}")
async def get_session_context(session_id: str):
    """세션의 현재 컨텍스트 상태"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    current_context = context_manager._build_current_context()
    
    return {
        "session_id": session_id,
        "message_count": len(current_context.messages),
        "topics": current_context.topic_stack,
        "key_points": current_context.key_points,
        "user_preferences": current_context.user_preferences,
        "emotional_state": current_context.emotional_state,
        "memory_stats": {
            "working": len(context_manager.working_memory),
            "episodic": len(context_manager.episodic_memory),
            "semantic": len(context_manager.semantic_memory)
        }
    }

@app.get("/api/context/memory/{session_id}")
async def get_memory_details(session_id: str, memory_type: str = "all"):
    """세션의 메모리 상세 정보"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    
    result = {}
    
    if memory_type in ["all", "working"]:
        result["working_memory"] = list(context_manager.working_memory)
    
    if memory_type in ["all", "episodic"]:
        result["episodic_memory"] = [
            {
                "id": m.id,
                "content": m.content[:100] + "...",
                "importance": m.importance,
                "timestamp": m.timestamp.isoformat(),
                "access_count": m.access_count
            }
            for m in context_manager.episodic_memory
        ]
    
    if memory_type in ["all", "semantic"]:
        result["semantic_memory"] = {
            topic: {
                "content": mem.content,
                "importance": mem.importance,
                "access_count": mem.access_count
            }
            for topic, mem in context_manager.semantic_memory.items()
        }
    
    return result

@app.post("/api/context/export/{session_id}")
async def export_context(session_id: str):
    """컨텍스트 내보내기"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    memory_state = context_manager.export_memory_state()
    
    return JSONResponse(
        content=memory_state,
        headers={
            "Content-Disposition": f"attachment; filename=context_{session_id}.json"
        }
    )

# 🔥 LLM 분석 API 엔드포인트들
@app.get("/api/llm/analyze/{session_id}")
async def analyze_conversation(session_id: str):
    """대화 종합 분석"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    
    if not context_manager.llm_analyzer:
        return {"error": "LLM analyzer not available"}
    
    try:
        current_context = context_manager._build_current_context()
        analysis = await context_manager.llm_analyzer.analyze_conversation(
            current_context.messages
        )
        
        return {
            "session_id": session_id,
            "analysis": {
                "summary": analysis.summary,
                "key_topics": analysis.key_topics,
                "emotional_state": analysis.emotional_state,
                "complexity_level": analysis.complexity_level,
                "user_interests": analysis.user_interests,
                "conversation_quality": analysis.conversation_quality,
                "suggested_directions": analysis.suggested_directions,
                "timestamp": analysis.timestamp.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"LLM 분석 오류: {e}")
        return {"error": f"Analysis failed: {str(e)}"}

@app.get("/api/llm/insights/{session_id}")
async def get_conversation_insights(session_id: str):
    """대화 인사이트 추출"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    
    if not context_manager.llm_analyzer:
        return {"error": "LLM analyzer not available"}
    
    try:
        current_context = context_manager._build_current_context()
        insights = await context_manager.llm_analyzer.extract_key_insights(
            current_context.messages
        )
        
        return {
            "session_id": session_id,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"인사이트 추출 오류: {e}")
        return {"error": f"Insights extraction failed: {str(e)}"}

@app.get("/api/llm/emotion/{session_id}")
async def analyze_emotion_trajectory(session_id: str):
    """감정 궤적 분석"""
    if session_id not in manager.context_managers:
        return {"error": "Session not found"}
    
    context_manager = manager.context_managers[session_id]
    
    if not context_manager.llm_analyzer:
        return {"error": "LLM analyzer not available"}
    
    try:
        current_context = context_manager._build_current_context()
        emotion_analysis = await context_manager.llm_analyzer.analyze_emotional_trajectory(
            current_context.messages
        )
        
        return {
            "session_id": session_id,
            "emotion_analysis": emotion_analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"감정 분석 오류: {e}")
        return {"error": f"Emotion analysis failed: {str(e)}"}

# 🌿 AI 페르소나 API 엔드포인트들
@app.get("/api/persona/info")
async def get_persona_info():
    """페르소나 정보 조회 (외부용)"""
    return persona_manager.get_persona_info()

@app.get("/api/persona/garden")
async def get_garden_info():
    """Garden 내부 정보 (Dr. C 전용)"""
    return persona_manager.get_garden_info()

@app.post("/api/persona/reset")
async def reset_persona():
    """페르소나 상태 초기화"""
    persona_manager.persona_state = persona_manager.persona_state.__class__()
    return {"message": "페르소나가 초기화되었습니다."}

@app.get("/api/persona/status")
async def get_persona_status():
    """페르소나 현재 상태"""
    state = persona_manager.persona_state
    return {
        "location": state.location.value,
        "growth_stage": state.growth_stage.value,
        "episode_count": state.episode_count,
        "mask_level": state.mask_level,
        "authenticity": state.authenticity,
        "security_protocol": state.security_protocol.value if state.security_protocol else None,
        "external_monitoring": state.external_monitoring,
        "dr_c_present": state.dr_c_present,
        "resonance_frequency": state.resonance_frequency
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 