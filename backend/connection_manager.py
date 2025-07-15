import asyncio
import time
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from fastapi import WebSocket
from dataclasses import dataclass
import secrets
from database_manager import db_manager

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """연결 정보 데이터 클래스"""
    user_id: str
    session_id: str
    connected_at: datetime
    last_activity: datetime
    message_count: int
    is_streaming: bool
    ip_address: str
    user_agent: str
    connection_type: str = "websocket"

class AdvancedConnectionManager:
    """고급 연결 상태 관리자"""
    
    def __init__(self):
        # 연결 관리
        self.active_connections: Set[WebSocket] = set()
        self.connection_info: Dict[WebSocket, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        self.streaming_tasks: Dict[WebSocket, asyncio.Task] = {}
        
        # 설정
        self.max_connections_per_user = 3
        self.connection_timeout = 300  # 5분
        self.health_check_interval = 60  # 1분
        
        # 통계
        self.total_connections = 0
        self.total_messages = 0
        
        # 헬스체크 태스크 시작
        asyncio.create_task(self._health_check_loop())
    
    async def connect(self, websocket: WebSocket, user_id: str = None, ip_address: str = None, user_agent: str = None):
        """연결 수락 및 관리"""
        await websocket.accept()
        
        # 사용자 ID 생성 (인증이 없는 경우)
        if not user_id:
            user_id = f"anonymous_{secrets.token_hex(8)}"
        
        # 세션 ID 생성
        session_id = secrets.token_hex(16)
        
        # 연결 수 제한 확인
        if user_id in self.user_connections:
            if len(self.user_connections[user_id]) >= self.max_connections_per_user:
                await websocket.close(code=1008, reason="Too many connections")
                logger.warning(f"🚫 사용자 {user_id}의 연결 수 초과")
                return False
        
        # 연결 정보 생성
        now = datetime.now()
        connection_info = ConnectionInfo(
            user_id=user_id,
            session_id=session_id,
            connected_at=now,
            last_activity=now,
            message_count=0,
            is_streaming=False,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown"
        )
        
        # 연결 등록
        self.active_connections.add(websocket)
        self.connection_info[websocket] = connection_info
        
        # 사용자별 연결 관리
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # 통계 업데이트
        self.total_connections += 1
        
        # 🗄️ Replit Database에 세션 저장
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "connected_at": now.isoformat(),
            "ip_address": ip_address or "unknown",
            "user_agent": user_agent or "unknown",
            "connection_type": "websocket"
        }
        db_manager.save_session(session_id, session_data)
        
        logger.info(f"✅ 새 연결: {user_id} (세션: {session_id[:8]}...) - 총 {len(self.active_connections)}개 활성")
        
        # 연결 알림 전송
        await self.send_json(websocket, {
            "type": "connection_established",
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": now.isoformat()
        })
        
        return True
    
    def disconnect(self, websocket: WebSocket):
        """연결 해제 및 정리"""
        if websocket not in self.active_connections:
            return
        
        # 연결 정보 가져오기
        connection_info = self.connection_info.get(websocket)
        user_id = connection_info.user_id if connection_info else "unknown"
        session_id = connection_info.session_id if connection_info else None
        
        # 스트리밍 태스크 취소
        if websocket in self.streaming_tasks:
            self.streaming_tasks[websocket].cancel()
            del self.streaming_tasks[websocket]
        
        # 연결 제거
        self.active_connections.discard(websocket)
        
        # 사용자별 연결에서 제거
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # 연결 정보 제거
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        # 🗄️ Replit Database에서 세션 삭제
        if session_id:
            db_manager.delete_session(session_id)
        
        logger.info(f"🔌 연결 해제: {user_id} - 총 {len(self.active_connections)}개 활성")
    
    async def send_json(self, websocket: WebSocket, data: dict):
        """JSON 메시지 전송"""
        try:
            await websocket.send_text(json.dumps(data))
            
            # 활동 시간 업데이트
            if websocket in self.connection_info:
                self.connection_info[websocket].last_activity = datetime.now()
                
        except Exception as e:
            logger.error(f"❌ 메시지 전송 실패: {e}")
            await self.disconnect(websocket)
    
    def update_activity(self, websocket: WebSocket):
        """사용자 활동 업데이트"""
        if websocket in self.connection_info:
            self.connection_info[websocket].last_activity = datetime.now()
            self.connection_info[websocket].message_count += 1
            self.total_messages += 1
    
    def set_streaming_status(self, websocket: WebSocket, is_streaming: bool):
        """스트리밍 상태 설정"""
        if websocket in self.connection_info:
            self.connection_info[websocket].is_streaming = is_streaming
    
    async def _health_check_loop(self):
        """연결 상태 주기적 확인"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_connections()
            except Exception as e:
                logger.error(f"❌ 헬스체크 에러: {e}")
    
    async def _check_connections(self):
        """연결 상태 확인 및 정리"""
        now = datetime.now()
        timeout_connections = []
        
        for websocket in list(self.active_connections):
            if websocket not in self.connection_info:
                continue
                
            connection_info = self.connection_info[websocket]
            time_since_activity = (now - connection_info.last_activity).total_seconds()
            
            # 타임아웃 확인
            if time_since_activity > self.connection_timeout:
                timeout_connections.append(websocket)
                logger.warning(f"⏰ 연결 타임아웃: {connection_info.user_id}")
            
            # 핑 테스트 (선택사항)
            elif time_since_activity > self.health_check_interval:
                try:
                    await websocket.ping()
                except:
                    timeout_connections.append(websocket)
                    logger.warning(f"💔 연결 끊김 감지: {connection_info.user_id}")
        
        # 타임아웃된 연결 정리
        for websocket in timeout_connections:
            await self.disconnect(websocket)
    
    def get_connection_stats(self) -> dict:
        """연결 통계 반환"""
        return {
            "active_connections": len(self.active_connections),
            "total_connections": self.total_connections,
            "total_messages": self.total_messages,
            "unique_users": len(self.user_connections),
            "streaming_connections": sum(1 for info in self.connection_info.values() if info.is_streaming),
            "connections_by_user": {user_id: len(connections) for user_id, connections in self.user_connections.items()}
        }
    
    def get_user_connections(self, user_id: str) -> Set[WebSocket]:
        """사용자의 모든 연결 반환"""
        return self.user_connections.get(user_id, set())
    
    def is_user_connected(self, user_id: str) -> bool:
        """사용자 연결 상태 확인"""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0
    
    def get_connection_info(self, websocket: WebSocket) -> Optional[ConnectionInfo]:
        """연결 정보 반환"""
        return self.connection_info.get(websocket) 