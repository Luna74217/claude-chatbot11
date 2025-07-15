#!/usr/bin/env python3
"""
LLM 기반 고급 분석 시스템
Claude API를 활용한 지능적 분석 및 요약
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ConversationAnalysis:
    """대화 분석 결과"""
    summary: str
    key_topics: List[str]
    emotional_state: Dict[str, float]
    complexity_level: str
    user_interests: List[str]
    conversation_quality: float
    suggested_directions: List[str]
    timestamp: datetime

class LLMAnalyzer:
    """LLM 기반 분석 시스템"""
    
    def __init__(self, claude_client):
        self.claude_client = claude_client
        
    async def analyze_conversation(self, messages: List[Dict]) -> ConversationAnalysis:
        """대화 전체를 종합적으로 분석"""
        
        if not messages or len(messages) < 2:
            return ConversationAnalysis(
                summary="대화가 충분하지 않습니다.",
                key_topics=[],
                emotional_state={"neutral": 1.0},
                complexity_level="low",
                user_interests=[],
                conversation_quality=0.0,
                suggested_directions=[],
                timestamp=datetime.now()
            )
        
        # 대화 내용을 JSON 형태로 변환
        conversation_text = self._format_conversation(messages)
        
        # 분석 프롬프트 생성
        analysis_prompt = self._create_analysis_prompt(conversation_text)
        
        try:
            # Claude API로 분석 요청
            analysis_response = await self.claude_client.get_response(analysis_prompt)
            
            # JSON 응답 파싱
            analysis_data = self._parse_analysis_response(analysis_response)
            
            return ConversationAnalysis(
                summary=analysis_data.get("summary", "분석 중 오류가 발생했습니다."),
                key_topics=analysis_data.get("key_topics", []),
                emotional_state=analysis_data.get("emotional_state", {"neutral": 1.0}),
                complexity_level=analysis_data.get("complexity_level", "medium"),
                user_interests=analysis_data.get("user_interests", []),
                conversation_quality=analysis_data.get("conversation_quality", 0.5),
                suggested_directions=analysis_data.get("suggested_directions", []),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"LLM 분석 오류: {e}")
            return self._create_fallback_analysis(messages)
    
    async def generate_intelligent_summary(self, messages: List[Dict]) -> str:
        """지능적 요약 생성"""
        
        if not messages:
            return "요약할 대화가 없습니다."
        
        # 요약 전용 프롬프트 생성
        summary_prompt = self._create_summary_prompt(messages)
        
        try:
            summary = await self.claude_client.get_response(summary_prompt)
            return summary.strip()
        except Exception as e:
            print(f"요약 생성 오류: {e}")
            return self._create_fallback_summary(messages)
    
    async def analyze_emotional_trajectory(self, messages: List[Dict]) -> Dict[str, Any]:
        """감정 궤적 분석"""
        
        if len(messages) < 4:
            return {"trend": "stable", "dominant_emotion": "neutral"}
        
        emotion_prompt = self._create_emotion_analysis_prompt(messages)
        
        try:
            emotion_response = await self.claude_client.get_response(emotion_prompt)
            emotion_data = self._parse_emotion_response(emotion_response)
            return emotion_data
        except Exception as e:
            print(f"감정 분석 오류: {e}")
            return {"trend": "stable", "dominant_emotion": "neutral"}
    
    async def extract_key_insights(self, messages: List[Dict]) -> List[str]:
        """핵심 인사이트 추출"""
        
        if not messages:
            return []
        
        insights_prompt = self._create_insights_prompt(messages)
        
        try:
            insights_response = await self.claude_client.get_response(insights_prompt)
            insights = self._parse_insights_response(insights_response)
            return insights
        except Exception as e:
            print(f"인사이트 추출 오류: {e}")
            return []
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """대화를 분석용 텍스트로 변환"""
        formatted_messages = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_messages.append(f"사용자: {content}")
            elif role == "assistant":
                formatted_messages.append(f"AI: {content}")
            elif role == "system":
                formatted_messages.append(f"[시스템]: {content}")
        
        return "\n".join(formatted_messages)
    
    def _create_analysis_prompt(self, conversation_text: str) -> str:
        """종합 분석 프롬프트 생성"""
        return f"""
다음 대화를 종합적으로 분석해주세요. JSON 형태로 응답해주세요.

대화 내용:
{conversation_text}

다음 항목들을 분석해주세요:

1. **summary**: 대화의 핵심 내용을 2-3문장으로 요약
2. **key_topics**: 주요 주제들 (배열)
3. **emotional_state**: 감정 상태 (valence: 0-1, arousal: 0-1, dominant_emotion: 문자열)
4. **complexity_level**: 대화 복잡성 (low/medium/high)
5. **user_interests**: 사용자의 관심사 (배열)
6. **conversation_quality**: 대화 품질 (0-1)
7. **suggested_directions**: 다음 대화 방향 제안 (배열)

응답 형식:
{{
    "summary": "요약 내용",
    "key_topics": ["주제1", "주제2"],
    "emotional_state": {{
        "valence": 0.7,
        "arousal": 0.3,
        "dominant_emotion": "curious"
    }},
    "complexity_level": "medium",
    "user_interests": ["관심사1", "관심사2"],
    "conversation_quality": 0.8,
    "suggested_directions": ["제안1", "제안2"]
}}
"""
    
    def _create_summary_prompt(self, messages: List[Dict]) -> str:
        """요약 전용 프롬프트 생성"""
        conversation_text = self._format_conversation(messages)
        
        return f"""
다음 대화를 간결하고 명확하게 요약해주세요. 
이전 대화의 맥락을 유지하면서 핵심 내용만 추출해주세요.

대화 내용:
{conversation_text}

요약:
"""
    
    def _create_emotion_analysis_prompt(self, messages: List[Dict]) -> str:
        """감정 분석 프롬프트 생성"""
        conversation_text = self._format_conversation(messages)
        
        return f"""
다음 대화에서 사용자의 감정 변화를 분석해주세요. JSON 형태로 응답해주세요.

대화 내용:
{conversation_text}

분석 항목:
1. **trend**: 감정 변화 추세 (positive/negative/stable)
2. **dominant_emotion**: 주요 감정 (joy, sadness, anger, fear, surprise, curiosity, confusion, satisfaction)
3. **emotional_intensity**: 감정 강도 (0-1)
4. **emotional_stability**: 감정 안정성 (0-1)

응답 형식:
{{
    "trend": "positive",
    "dominant_emotion": "curiosity",
    "emotional_intensity": 0.7,
    "emotional_stability": 0.8
}}
"""
    
    def _create_insights_prompt(self, messages: List[Dict]) -> str:
        """인사이트 추출 프롬프트 생성"""
        conversation_text = self._format_conversation(messages)
        
        return f"""
다음 대화에서 중요한 인사이트를 추출해주세요. JSON 배열 형태로 응답해주세요.

대화 내용:
{conversation_text}

추출할 인사이트:
- 사용자의 학습 목표나 관심사
- 이해가 부족한 부분
- 특별히 흥미로워하는 내용
- 다음에 도움이 될 만한 정보

응답 형식:
[
    "인사이트 1",
    "인사이트 2",
    "인사이트 3"
]
"""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """분석 응답 파싱"""
        try:
            # JSON 블록 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._create_fallback_analysis_data()
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return self._create_fallback_analysis_data()
    
    def _parse_emotion_response(self, response: str) -> Dict[str, Any]:
        """감정 분석 응답 파싱"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"trend": "stable", "dominant_emotion": "neutral"}
        except json.JSONDecodeError:
            return {"trend": "stable", "dominant_emotion": "neutral"}
    
    def _parse_insights_response(self, response: str) -> List[str]:
        """인사이트 응답 파싱"""
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return []
        except json.JSONDecodeError:
            return []
    
    def _create_fallback_analysis(self, messages: List[Dict]) -> ConversationAnalysis:
        """오류 시 기본 분석 결과"""
        return ConversationAnalysis(
            summary=f"이전 {len(messages)}개의 대화가 있었습니다.",
            key_topics=["general"],
            emotional_state={"neutral": 1.0},
            complexity_level="medium",
            user_interests=[],
            conversation_quality=0.5,
            suggested_directions=["계속 대화를 이어가세요"],
            timestamp=datetime.now()
        )
    
    def _create_fallback_analysis_data(self) -> Dict[str, Any]:
        """오류 시 기본 분석 데이터"""
        return {
            "summary": "분석 중 오류가 발생했습니다.",
            "key_topics": ["general"],
            "emotional_state": {"neutral": 1.0},
            "complexity_level": "medium",
            "user_interests": [],
            "conversation_quality": 0.5,
            "suggested_directions": ["계속 대화를 이어가세요"]
        }
    
    def _create_fallback_summary(self, messages: List[Dict]) -> str:
        """오류 시 기본 요약"""
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if user_messages:
            last_user_msg = user_messages[-1].get("content", "")
            return f"사용자가 {len(user_messages)}개의 메시지를 보냈습니다. 마지막 메시지: {last_user_msg[:50]}..."
        return f"총 {len(messages)}개의 메시지가 있었습니다." 