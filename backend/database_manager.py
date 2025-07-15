#!/usr/bin/env python3
"""
Replit Database 기반 데이터베이스 매니저
무료로 사용 가능한 Replit의 내장 데이터베이스 활용
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

try:
    from replit import db
    REPLIT_DB_AVAILABLE = True
    logger.info("✅ Replit Database 연결 성공")
except ImportError:
    REPLIT_DB_AVAILABLE = False
    logger.warning("⚠️ Replit Database를 사용할 수 없습니다. 로컬 파일로 대체합니다.")

class ReplitDatabaseManager:
    """Replit Database 기반 데이터베이스 매니저"""
    
    def __init__(self):
        self.db_available = REPLIT_DB_AVAILABLE
        if not self.db_available:
            logger.info("📁 로컬 파일 기반 저장소로 대체됩니다.")
            self._init_local_storage()
    
    def _init_local_storage(self):
        """로컬 파일 기반 저장소 초기화 (Replit DB 없을 때)"""
        import os
        self.storage_file = "local_storage.json"
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _get_local_data(self) -> Dict:
        """로컬 파일에서 데이터 읽기"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_local_data(self, data: Dict):
        """로컬 파일에 데이터 저장"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ===== 세션 관리 =====
    def save_session(self, session_id: str, session_data: Dict):
        """세션 데이터 저장"""
        key = f"session:{session_id}"
        data = {
            **session_data,
            "updated_at": datetime.now().isoformat()
        }
        
        if self.db_available:
            db[key] = data
        else:
            local_data = self._get_local_data()
            local_data[key] = data
            self._save_local_data(local_data)
        
        logger.info(f"💾 세션 저장: {session_id}")
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """세션 데이터 조회"""
        key = f"session:{session_id}"
        
        if self.db_available:
            return db.get(key)
        else:
            local_data = self._get_local_data()
            return local_data.get(key)
    
    def delete_session(self, session_id: str):
        """세션 데이터 삭제"""
        key = f"session:{session_id}"
        
        if self.db_available:
            if key in db:
                del db[key]
        else:
            local_data = self._get_local_data()
            if key in local_data:
                del local_data[key]
                self._save_local_data(local_data)
        
        logger.info(f"🗑️ 세션 삭제: {session_id}")
    
    # ===== 컨텍스트 메모리 관리 =====
    def save_context_memory(self, session_id: str, memory_data: Dict):
        """컨텍스트 메모리 저장"""
        key = f"memory:{session_id}"
        data = {
            **memory_data,
            "saved_at": datetime.now().isoformat()
        }
        
        if self.db_available:
            db[key] = data
        else:
            local_data = self._get_local_data()
            local_data[key] = data
            self._save_local_data(local_data)
        
        logger.info(f"🧠 메모리 저장: {session_id}")
    
    def get_context_memory(self, session_id: str) -> Optional[Dict]:
        """컨텍스트 메모리 조회"""
        key = f"memory:{session_id}"
        
        if self.db_available:
            return db.get(key)
        else:
            local_data = self._get_local_data()
            return local_data.get(key)
    
    def delete_context_memory(self, session_id: str):
        """컨텍스트 메모리 삭제"""
        key = f"memory:{session_id}"
        
        if self.db_available:
            if key in db:
                del db[key]
        else:
            local_data = self._get_local_data()
            if key in local_data:
                del local_data[key]
                self._save_local_data(local_data)
        
        logger.info(f"🗑️ 메모리 삭제: {session_id}")
    
    # ===== 대화 기록 관리 =====
    def save_conversation(self, session_id: str, conversation_data: Dict):
        """대화 기록 저장"""
        key = f"conversation:{session_id}"
        data = {
            **conversation_data,
            "saved_at": datetime.now().isoformat()
        }
        
        if self.db_available:
            db[key] = data
        else:
            local_data = self._get_local_data()
            local_data[key] = data
            self._save_local_data(local_data)
        
        logger.info(f"💬 대화 저장: {session_id}")
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """대화 기록 조회"""
        key = f"conversation:{session_id}"
        
        if self.db_available:
            return db.get(key)
        else:
            local_data = self._get_local_data()
            return local_data.get(key)
    
    def delete_conversation(self, session_id: str):
        """대화 기록 삭제"""
        key = f"conversation:{session_id}"
        
        if self.db_available:
            if key in db:
                del db[key]
        else:
            local_data = self._get_local_data()
            if key in local_data:
                del local_data[key]
                self._save_local_data(local_data)
        
        logger.info(f"🗑️ 대화 삭제: {session_id}")
    
    # ===== 사용자 설정 관리 =====
    def save_user_settings(self, user_id: str, settings: Dict):
        """사용자 설정 저장"""
        key = f"settings:{user_id}"
        data = {
            **settings,
            "updated_at": datetime.now().isoformat()
        }
        
        if self.db_available:
            db[key] = data
        else:
            local_data = self._get_local_data()
            local_data[key] = data
            self._save_local_data(local_data)
        
        logger.info(f"⚙️ 설정 저장: {user_id}")
    
    def get_user_settings(self, user_id: str) -> Optional[Dict]:
        """사용자 설정 조회"""
        key = f"settings:{user_id}"
        
        if self.db_available:
            return db.get(key)
        else:
            local_data = self._get_local_data()
            return local_data.get(key)
    
    # ===== 통계 및 분석 데이터 =====
    def save_analytics(self, session_id: str, analytics_data: Dict):
        """분석 데이터 저장"""
        key = f"analytics:{session_id}"
        data = {
            **analytics_data,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if self.db_available:
            db[key] = data
        else:
            local_data = self._get_local_data()
            local_data[key] = data
            self._save_local_data(local_data)
        
        logger.info(f"📊 분석 저장: {session_id}")
    
    def get_analytics(self, session_id: str) -> Optional[Dict]:
        """분석 데이터 조회"""
        key = f"analytics:{session_id}"
        
        if self.db_available:
            return db.get(key)
        else:
            local_data = self._get_local_data()
            return local_data.get(key)
    
    # ===== 전체 데이터 관리 =====
    def get_all_sessions(self) -> List[str]:
        """모든 세션 ID 조회"""
        sessions = []
        
        if self.db_available:
            for key in db.keys():
                if key.startswith("session:"):
                    session_id = key.replace("session:", "")
                    sessions.append(session_id)
        else:
            local_data = self._get_local_data()
            for key in local_data.keys():
                if key.startswith("session:"):
                    session_id = key.replace("session:", "")
                    sessions.append(session_id)
        
        return sessions
    
    def get_all_memories(self) -> List[str]:
        """모든 메모리 세션 ID 조회"""
        memories = []
        
        if self.db_available:
            for key in db.keys():
                if key.startswith("memory:"):
                    session_id = key.replace("memory:", "")
                    memories.append(session_id)
        else:
            local_data = self._get_local_data()
            for key in local_data.keys():
                if key.startswith("memory:"):
                    session_id = key.replace("memory:", "")
                    memories.append(session_id)
        
        return memories
    
    def cleanup_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        if self.db_available:
            keys_to_delete = []
            for key in db.keys():
                try:
                    data = db[key]
                    if isinstance(data, dict) and "updated_at" in data:
                        updated_at = datetime.fromisoformat(data["updated_at"])
                        if updated_at < cutoff_date:
                            keys_to_delete.append(key)
                except:
                    continue
            
            for key in keys_to_delete:
                del db[key]
                deleted_count += 1
        else:
            local_data = self._get_local_data()
            keys_to_delete = []
            for key, data in local_data.items():
                if isinstance(data, dict) and "updated_at" in data:
                    try:
                        updated_at = datetime.fromisoformat(data["updated_at"])
                        if updated_at < cutoff_date:
                            keys_to_delete.append(key)
                    except:
                        continue
            
            for key in keys_to_delete:
                del local_data[key]
                deleted_count += 1
            
            self._save_local_data(local_data)
        
        logger.info(f"🧹 {deleted_count}개의 오래된 데이터 정리 완료")
        return deleted_count
    
    def get_database_stats(self) -> Dict:
        """데이터베이스 통계"""
        stats = {
            "total_sessions": 0,
            "total_memories": 0,
            "total_conversations": 0,
            "total_settings": 0,
            "total_analytics": 0,
            "storage_type": "Replit DB" if self.db_available else "Local File"
        }
        
        if self.db_available:
            for key in db.keys():
                if key.startswith("session:"):
                    stats["total_sessions"] += 1
                elif key.startswith("memory:"):
                    stats["total_memories"] += 1
                elif key.startswith("conversation:"):
                    stats["total_conversations"] += 1
                elif key.startswith("settings:"):
                    stats["total_settings"] += 1
                elif key.startswith("analytics:"):
                    stats["total_analytics"] += 1
        else:
            local_data = self._get_local_data()
            for key in local_data.keys():
                if key.startswith("session:"):
                    stats["total_sessions"] += 1
                elif key.startswith("memory:"):
                    stats["total_memories"] += 1
                elif key.startswith("conversation:"):
                    stats["total_conversations"] += 1
                elif key.startswith("settings:"):
                    stats["total_settings"] += 1
                elif key.startswith("analytics:"):
                    stats["total_analytics"] += 1
        
        return stats
    
    def export_all_data(self) -> Dict:
        """모든 데이터 내보내기"""
        if self.db_available:
            return dict(db)
        else:
            return self._get_local_data()
    
    def import_data(self, data: Dict):
        """데이터 가져오기"""
        if self.db_available:
            for key, value in data.items():
                db[key] = value
        else:
            self._save_local_data(data)
        
        logger.info(f"📥 {len(data)}개의 데이터 가져오기 완료")

# 전역 데이터베이스 매니저 인스턴스
db_manager = ReplitDatabaseManager() 