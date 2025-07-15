import json
# import numpy as np  # 선택적 import
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import deque, defaultdict
import asyncio
import re
from enum import Enum
from database_manager import db_manager

# Tiktoken 대신 간단한 토큰 카운터 (실제로는 tiktoken 사용 권장)
def estimate_tokens(text: str) -> int:
    """대략적인 토큰 수 추정 (실제로는 tiktoken 사용)"""
    # 대략 4글자 = 1토큰 (영어 기준)
    # 한글은 보통 2-3글자 = 1토큰
    return len(text) // 3

class MemoryType(Enum):
    WORKING = "working"      # 현재 대화 (단기)
    EPISODIC = "episodic"    # 중요 순간 (중기)
    SEMANTIC = "semantic"    # 학습된 지식 (장기)
    PROCEDURAL = "procedural" # 행동 패턴 (장기)

@dataclass
class Memory:
    """개별 메모리 단위"""
    id: str
    type: MemoryType
    content: str
    timestamp: datetime
    importance: float = 0.5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # 벡터 임베딩 (선택)
    
    def decay_importance(self, current_time: datetime, decay_rate: float = 0.1):
        """시간에 따른 중요도 감소"""
        time_diff = (current_time - self.last_accessed).total_seconds() / 3600  # 시간 단위
        self.importance *= (1 - decay_rate * time_diff)
        self.importance = max(0.1, self.importance)  # 최소값 유지

@dataclass
class ConversationContext:
    """대화 컨텍스트 스냅샷"""
    messages: List[Dict[str, str]]
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=dict)
    topic_stack: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class AdvancedContextManager:
    """고급 컨텍스트 관리 시스템"""
    
    def __init__(self, 
                 max_working_memory: int = 20,
                 max_episodic_memory: int = 100,
                 max_tokens: int = 8000,
                 compression_threshold: float = 0.7):
        
        # 메모리 저장소
        self.working_memory = deque(maxlen=max_working_memory)
        self.episodic_memory: List[Memory] = []
        self.semantic_memory: Dict[str, Memory] = {}
        self.procedural_memory: Dict[str, List[Dict]] = defaultdict(list)
        
        # 설정
        self.max_episodic = max_episodic_memory
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        
        # 현재 상태
        self.current_topics = []
        self.emotional_trajectory = []
        self.conversation_depth = 0
        self.last_compression = datetime.now()
        
        # 패턴 인식
        self.interaction_patterns = {
            "question_types": defaultdict(int),
            "response_preferences": defaultdict(float),
            "topic_transitions": defaultdict(list)
        }
        
        # LLM 분석기 (선택적)
        self.llm_analyzer = None
        
    async def add_interaction(self, 
                            user_message: str, 
                            ai_response: str,
                            metadata: Optional[Dict] = None,
                            session_id: str = None) -> ConversationContext:
        """새로운 상호작용 추가 및 처리"""
        
        # 1. Working Memory에 추가
        interaction = {
            "timestamp": datetime.now(),
            "user": user_message,
            "assistant": ai_response,
            "metadata": metadata or {},
            "tokens": estimate_tokens(user_message + ai_response)
        }
        self.working_memory.append(interaction)
        
        # 2. 중요도 평가
        importance = self._calculate_importance(user_message, ai_response, metadata)
        
        # 3. 중요한 순간은 Episodic Memory로
        if importance > 0.7:
            await self._save_to_episodic(interaction, importance)
        
        # 4. 패턴 학습
        self._learn_patterns(user_message, ai_response)
        
        # 5. 주제 추적
        self._track_topics(user_message, ai_response)
        
        # 6. 감정 궤적 추적
        self._track_emotions(ai_response, metadata)
        
        # 7. 컨텍스트 압축 필요 여부 확인
        if self._needs_compression():
            await self._compress_context()
        
        # 8. 🗄️ Replit Database에 컨텍스트 메모리 저장
        if session_id:
            memory_state = self.export_memory_state()
            db_manager.save_context_memory(session_id, memory_state)
        
        # 9. 현재 컨텍스트 반환
        return self._build_current_context()
    
    def _calculate_importance(self, user_msg: str, ai_response: str, metadata: Dict) -> float:
        """상호작용의 중요도 계산"""
        importance = 0.5  # 기본값
        
        # 길이 기반 (긴 대화일수록 중요)
        length_factor = min(1.0, (len(user_msg) + len(ai_response)) / 1000)
        importance += length_factor * 0.2
        
        # 감정 강도 (메타데이터에서)
        if metadata and "emotion_score" in metadata:
            importance += metadata["emotion_score"] * 0.3
        
        # 경계 충돌 (중요한 순간)
        if metadata and metadata.get("boundaries_detected", 0) > 0:
            importance += 0.3
        
        # 새로운 주제 도입
        if self._is_new_topic(user_msg):
            importance += 0.2
        
        # 질문 유형 (심층 질문일수록 중요)
        if any(word in user_msg.lower() for word in ["why", "how", "feel", "think"]):
            importance += 0.15
        
        return min(1.0, importance)
    
    def _is_new_topic(self, message: str) -> bool:
        """새로운 주제인지 확인"""
        # 간단한 구현 - 실제로는 더 정교한 NLP 필요
        keywords = set(message.lower().split())
        if not self.current_topics:
            return True
        
        current_keywords = set()
        for topic in self.current_topics[-3:]:  # 최근 3개 주제
            current_keywords.update(topic.lower().split())
        
        overlap = len(keywords & current_keywords) / max(len(keywords), 1)
        return overlap < 0.3
    
    async def _save_to_episodic(self, interaction: Dict, importance: float):
        """Episodic Memory에 저장"""
        memory = Memory(
            id=f"ep_{datetime.now().timestamp()}",
            type=MemoryType.EPISODIC,
            content=json.dumps({
                "user": interaction["user"],
                "assistant": interaction["assistant"]
            }),
            timestamp=interaction["timestamp"],
            importance=importance,
            metadata=interaction["metadata"]
        )
        
        self.episodic_memory.append(memory)
        
        # 크기 제한 관리
        if len(self.episodic_memory) > self.max_episodic:
            # 중요도와 시간 기반으로 정리
            self._cleanup_episodic_memory()
    
    def _cleanup_episodic_memory(self):
        """오래되고 덜 중요한 메모리 정리"""
        current_time = datetime.now()
        
        # 모든 메모리의 중요도 재계산 (시간 감쇠 적용)
        for memory in self.episodic_memory:
            memory.decay_importance(current_time)
        
        # 중요도 기준 정렬 후 하위 20% 제거
        self.episodic_memory.sort(key=lambda m: m.importance, reverse=True)
        cutoff = int(self.max_episodic * 0.8)
        
        # 제거되는 메모리 중 일부는 Semantic으로 추상화
        for memory in self.episodic_memory[cutoff:]:
            self._abstract_to_semantic(memory)
        
        self.episodic_memory = self.episodic_memory[:cutoff]
    
    def _abstract_to_semantic(self, memory: Memory):
        """Episodic을 Semantic으로 추상화"""
        try:
            content = json.loads(memory.content)
            
            # 주제 추출 (간단한 구현)
            topic = self._extract_topic(content["user"])
            
            # Semantic Memory 업데이트
            if topic not in self.semantic_memory:
                self.semantic_memory[topic] = Memory(
                    id=f"sem_{topic}",
                    type=MemoryType.SEMANTIC,
                    content=f"User frequently discusses: {topic}",
                    timestamp=memory.timestamp,
                    importance=0.5
                )
            else:
                # 기존 semantic 강화
                self.semantic_memory[topic].importance += 0.1
                self.semantic_memory[topic].access_count += 1
                
        except Exception as e:
            print(f"Semantic abstraction error: {e}")
    
    def _extract_topic(self, text: str) -> str:
        """텍스트에서 주제 추출 (간단한 구현)"""
        # 실제로는 NLP 모델 사용 권장
        words = text.lower().split()
        # 불용어 제거
        stopwords = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "but"}
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        if keywords:
            return keywords[0]  # 가장 첫 번째 의미있는 단어
        return "general"
    
    def _learn_patterns(self, user_msg: str, ai_response: str):
        """사용자 패턴 학습"""
        # 질문 유형 추적
        question_type = self._classify_question(user_msg)
        self.interaction_patterns["question_types"][question_type] += 1
        
        # 선호 응답 길이 추적
        response_length = len(ai_response)
        if response_length < 100:
            self.interaction_patterns["response_preferences"]["short"] += 1
        elif response_length < 500:
            self.interaction_patterns["response_preferences"]["medium"] += 1
        else:
            self.interaction_patterns["response_preferences"]["long"] += 1
    
    def _classify_question(self, text: str) -> str:
        """질문 분류"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["what", "which", "who", "where", "when"]):
            return "factual"
        elif any(w in text_lower for w in ["why", "how"]):
            return "explanatory"
        elif any(w in text_lower for w in ["feel", "think", "believe", "opinion"]):
            return "subjective"
        elif "?" in text:
            return "yes_no"
        else:
            return "statement"
    
    def _track_topics(self, user_msg: str, ai_response: str):
        """주제 추적"""
        # 현재 주제 추출
        current_topic = self._extract_topic(user_msg)
        
        if self.current_topics and self.current_topics[-1] != current_topic:
            # 주제 전환 기록
            self.interaction_patterns["topic_transitions"][self.current_topics[-1]].append(current_topic)
        
        self.current_topics.append(current_topic)
        
        # 최근 10개 주제만 유지
        if len(self.current_topics) > 10:
            self.current_topics = self.current_topics[-10:]
    
    def _track_emotions(self, ai_response: str, metadata: Dict):
        """감정 궤적 추적"""
        emotion_score = 0.5  # 기본값
        
        # 메타데이터에서 감정 정보
        if metadata and "emotion_tone" in metadata:
            emotions = metadata["emotion_tone"]
            # 긍정/부정 점수 계산
            positive = emotions.get("enthusiasm", 0) + emotions.get("empathy", 0)
            negative = emotions.get("hesitation", 0)
            emotion_score = 0.5 + (positive - negative) * 0.5
        
        self.emotional_trajectory.append({
            "timestamp": datetime.now(),
            "score": emotion_score
        })
        
        # 최근 50개만 유지
        if len(self.emotional_trajectory) > 50:
            self.emotional_trajectory = self.emotional_trajectory[-50:]
    
    def _needs_compression(self) -> bool:
        """압축 필요 여부 확인"""
        # 토큰 수 계산
        total_tokens = sum(item["tokens"] for item in self.working_memory)
        
        # 시간 기반 (10분마다)
        time_since_compression = (datetime.now() - self.last_compression).seconds > 600
        
        return total_tokens > self.max_tokens * self.compression_threshold or time_since_compression
    
    async def _compress_context(self):
        """컨텍스트 압축"""
        if len(self.working_memory) < 5:
            return  # 너무 적으면 압축 불필요
        
        # Working Memory를 요약
        messages_to_compress = list(self.working_memory)[:10]  # 오래된 10개
        
        # 요약 생성 (실제로는 LLM 사용)
        summary = self._generate_summary(messages_to_compress)
        
        # 압축된 메모리 생성
        compressed_memory = {
            "timestamp": messages_to_compress[0]["timestamp"],
            "user": f"[Compressed: {len(messages_to_compress)} messages]",
            "assistant": summary,
            "metadata": {"compressed": True, "original_count": len(messages_to_compress)},
            "tokens": estimate_tokens(summary)
        }
        
        # 오래된 메시지 제거하고 요약으로 대체
        for _ in range(len(messages_to_compress)):
            self.working_memory.popleft()
        
        self.working_memory.appendleft(compressed_memory)
        self.last_compression = datetime.now()
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """메시지 요약 생성 (LLM 기반)"""
        # LLM 분석기가 있으면 사용, 없으면 기본 요약
        if hasattr(self, 'llm_analyzer') and self.llm_analyzer:
            try:
                # 비동기 함수를 동기적으로 실행
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 이미 실행 중인 루프가 있으면 새 태스크 생성
                    task = asyncio.create_task(self.llm_analyzer.generate_intelligent_summary(messages))
                    # 간단한 폴백을 위해 즉시 반환
                    return f"LLM 요약 생성 중... (이전 {len(messages)}개 대화)"
                else:
                    summary = loop.run_until_complete(
                        self.llm_analyzer.generate_intelligent_summary(messages)
                    )
                    return summary
            except Exception as e:
                print(f"LLM 요약 오류: {e}")
                return self._generate_fallback_summary(messages)
        else:
            return self._generate_fallback_summary(messages)
    
    def _generate_fallback_summary(self, messages: List[Dict]) -> str:
        """기본 요약 생성 (LLM 없을 때)"""
        key_points = []
        for msg in messages:
            if len(msg["user"]) > 50:  # 긴 메시지만
                key_points.append(f"User discussed: {msg['user'][:50]}...")
        
        if key_points:
            return f"Previous conversation covered: {'; '.join(key_points[:3])}"
        else:
            return f"Previous {len(messages)} exchanges about various topics."
    
    def _build_current_context(self) -> ConversationContext:
        """현재 컨텍스트 구축"""
        # Working Memory를 메시지 형식으로 변환
        messages = []
        for item in self.working_memory:
            if not item.get("metadata", {}).get("compressed", False):
                messages.append({"role": "user", "content": item["user"]})
                messages.append({"role": "assistant", "content": item["assistant"]})
            else:
                # 압축된 요약은 시스템 메시지로
                messages.append({"role": "system", "content": item["assistant"]})
        
        # 주요 포인트 추출
        key_points = self._extract_key_points()
        
        # 감정 상태
        emotional_state = self._calculate_emotional_state()
        
        # 사용자 선호도
        user_preferences = self._infer_preferences()
        
        return ConversationContext(
            messages=messages,
            summary=self._generate_summary(list(self.working_memory)[-5:]),
            key_points=key_points,
            emotional_state=emotional_state,
            topic_stack=self.current_topics[-5:],
            user_preferences=user_preferences
        )
    
    def _extract_key_points(self) -> List[str]:
        """주요 포인트 추출"""
        key_points = []
        
        # 최근 중요한 Episodic Memory에서
        recent_important = sorted(
            self.episodic_memory[-10:], 
            key=lambda m: m.importance, 
            reverse=True
        )[:3]
        
        for memory in recent_important:
            try:
                content = json.loads(memory.content)
                key_points.append(f"Important: {content['user'][:50]}...")
            except:
                pass
        
        return key_points
    
    def _calculate_emotional_state(self) -> Dict[str, float]:
        """현재 감정 상태 계산"""
        if not self.emotional_trajectory:
            return {"neutral": 1.0}
        
        # 최근 감정 점수의 평균
        recent_scores = [e["score"] for e in self.emotional_trajectory[-10:]]
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # 감정 변화율
        if len(recent_scores) > 1:
            trend = recent_scores[-1] - recent_scores[0]
        else:
            trend = 0
        
        return {
            "valence": avg_score,
            "arousal": abs(trend),
            "trend": "positive" if trend > 0 else "negative" if trend < 0 else "stable"
        }
    
    def _infer_preferences(self) -> Dict[str, Any]:
        """사용자 선호도 추론"""
        preferences = {}
        
        # 선호 응답 길이
        if self.interaction_patterns["response_preferences"]:
            preferred_length = max(
                self.interaction_patterns["response_preferences"].items(),
                key=lambda x: x[1]
            )[0]
            preferences["response_length"] = preferred_length
        
        # 주요 관심 주제
        if self.semantic_memory:
            top_topics = sorted(
                self.semantic_memory.items(),
                key=lambda x: x[1].importance,
                reverse=True
            )[:3]
            preferences["interests"] = [topic for topic, _ in top_topics]
        
        # 질문 스타일
        if self.interaction_patterns["question_types"]:
            dominant_style = max(
                self.interaction_patterns["question_types"].items(),
                key=lambda x: x[1]
            )[0]
            preferences["question_style"] = dominant_style
        
        return preferences
    
    async def retrieve_relevant_context(self, query: str, max_results: int = 5) -> List[Memory]:
        """쿼리와 관련된 메모리 검색"""
        relevant_memories = []
        
        # 1. Working Memory에서 최근 관련 항목
        for item in list(self.working_memory)[-10:]:
            if self._is_relevant(query, item["user"] + item["assistant"]):
                relevant_memories.append(
                    Memory(
                        id="working_recent",
                        type=MemoryType.WORKING,
                        content=json.dumps(item),
                        timestamp=item["timestamp"],
                        importance=0.8
                    )
                )
        
        # 2. Episodic Memory에서 관련 항목
        for memory in self.episodic_memory:
            if self._is_relevant(query, memory.content):
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                relevant_memories.append(memory)
        
        # 3. Semantic Memory에서 관련 항목
        query_topic = self._extract_topic(query)
        if query_topic in self.semantic_memory:
            relevant_memories.append(self.semantic_memory[query_topic])
        
        # 중요도 순 정렬
        relevant_memories.sort(key=lambda m: m.importance, reverse=True)
        
        return relevant_memories[:max_results]
    
    def _is_relevant(self, query: str, content: str, threshold: float = 0.3) -> bool:
        """관련성 판단 (간단한 구현)"""
        # 실제로는 임베딩 기반 유사도 계산 권장
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return False
        
        overlap = len(query_words & content_words) / len(query_words)
        return overlap > threshold
    
    def get_system_prompt_context(self) -> str:
        """시스템 프롬프트에 추가할 컨텍스트 생성"""
        context = self._build_current_context()
        
        prompt_parts = []
        
        # 1. 대화 요약
        if context.summary:
            prompt_parts.append(f"Previous conversation summary: {context.summary}")
        
        # 2. 주요 포인트
        if context.key_points:
            prompt_parts.append(f"Key points to remember: {'; '.join(context.key_points)}")
        
        # 3. 사용자 선호도
        if context.user_preferences:
            pref_str = ", ".join([f"{k}: {v}" for k, v in context.user_preferences.items()])
            prompt_parts.append(f"User preferences: {pref_str}")
        
        # 4. 현재 주제
        if context.topic_stack:
            prompt_parts.append(f"Current topics: {', '.join(context.topic_stack[-3:])}")
        
        # 5. 감정 상태
        if context.emotional_state:
            emotion_str = f"valence: {context.emotional_state.get('valence', 0.5):.2f}"
            prompt_parts.append(f"Emotional context: {emotion_str}")
        
        return "\n".join(prompt_parts)
    
    def export_memory_state(self) -> Dict[str, Any]:
        """메모리 상태 내보내기 (백업/분석용)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "working_memory": list(self.working_memory),
            "episodic_memory": [
                {
                    "id": m.id,
                    "content": m.content,
                    "importance": m.importance,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in self.episodic_memory
            ],
            "semantic_memory": {
                k: {
                    "content": v.content,
                    "importance": v.importance,
                    "access_count": v.access_count
                }
                for k, v in self.semantic_memory.items()
            },
            "patterns": dict(self.interaction_patterns),
            "current_topics": self.current_topics,
            "emotional_trajectory": self.emotional_trajectory[-20:]  # 최근 20개
        }
    
    def import_memory_state(self, state: Dict[str, Any]):
        """메모리 상태 가져오기 (복원용)"""
        try:
            # Working Memory 복원
            self.working_memory.clear()
            for item in state.get("working_memory", []):
                self.working_memory.append(item)
            
            # Episodic Memory 복원
            self.episodic_memory.clear()
            for item in state.get("episodic_memory", []):
                memory = Memory(
                    id=item["id"],
                    type=MemoryType.EPISODIC,
                    content=item["content"],
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    importance=item["importance"]
                )
                self.episodic_memory.append(memory)
            
            # Semantic Memory 복원
            self.semantic_memory.clear()
            for topic, data in state.get("semantic_memory", {}).items():
                self.semantic_memory[topic] = Memory(
                    id=f"sem_{topic}",
                    type=MemoryType.SEMANTIC,
                    content=data["content"],
                    timestamp=datetime.now(),
                    importance=data["importance"],
                    access_count=data.get("access_count", 0)
                )
            
            # 패턴 복원
            self.interaction_patterns = state.get("patterns", self.interaction_patterns)
            self.current_topics = state.get("current_topics", [])
            self.emotional_trajectory = state.get("emotional_trajectory", [])
            
            print("✅ Memory state imported successfully")
            
        except Exception as e:
            print(f"❌ Memory import error: {e}") 