import asyncio
from typing import AsyncGenerator, Optional, Dict, List, Callable, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re
import json
from enum import Enum

# ===== 1. 기본 스트림 변환기 =====

class StreamTransformer(ABC):
    """모든 스트림 변환기의 기본 클래스"""
    
    @abstractmethod
    async def transform(self, chunk: str) -> str:
        """청크를 변환하는 추상 메서드"""
        pass
    
    async def process_stream(self, input_stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        """스트림 전체를 처리"""
        async for chunk in input_stream:
            transformed = await self.transform(chunk)
            if transformed:  # 빈 문자열이 아닌 경우만 전달
                yield transformed


# ===== 2. 실시간 번역 변환기 =====

class TranslationTransformer(StreamTransformer):
    """실시간 번역 스트림 변환기"""
    
    def __init__(self, source_lang: str = "ko", target_lang: str = "en"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.buffer = ""
        self.sentence_endings = [".", "!", "?", "。", "！", "？"]
        
        # 간단한 번역 사전 (실제로는 API 사용)
        self.translations = {
            "안녕하세요": "Hello",
            "감사합니다": "Thank you",
            "좋은 아침입니다": "Good morning",
            "어떻게 지내세요": "How are you",
        }
    
    async def transform(self, chunk: str) -> str:
        """문장 단위로 번역"""
        self.buffer += chunk
        output = ""
        
        # 문장 끝을 찾아서 번역
        for ending in self.sentence_endings:
            if ending in self.buffer:
                sentences = self.buffer.split(ending)
                
                # 마지막 부분은 다음 버퍼로
                self.buffer = sentences[-1]
                
                # 완성된 문장들 번역
                for sentence in sentences[:-1]:
                    sentence = sentence.strip()
                    if sentence:
                        # 실제로는 번역 API 호출
                        translated = await self._translate(sentence)
                        output += translated + ending + " "
        
        return output
    
    async def _translate(self, text: str) -> str:
        """실제 번역 (시뮬레이션)"""
        # 실제 구현에서는 Google Translate API 등 사용
        await asyncio.sleep(0.1)  # API 호출 시뮬레이션
        
        # 간단한 사전 기반 번역
        for ko, en in self.translations.items():
            if ko in text:
                return text.replace(ko, en)
        
        # 기본값: [번역: 원문]
        return f"[Translation: {text}]"


# ===== 3. 감정 분석 필터 =====

class SentimentFilter(StreamTransformer):
    """감정 분석을 통한 필터링"""
    
    def __init__(self, filter_negative: bool = True, threshold: float = 0.3):
        self.filter_negative = filter_negative
        self.threshold = threshold
        self.buffer = ""
        
        # 감정 키워드 (실제로는 ML 모델 사용)
        self.positive_words = ["좋아", "사랑", "행복", "감사", "훌륭", "최고"]
        self.negative_words = ["싫어", "나빠", "최악", "실망", "화나", "짜증"]
    
    async def transform(self, chunk: str) -> str:
        """감정 분석 후 필터링"""
        self.buffer += chunk
        
        # 문장이 어느 정도 모이면 분석
        if len(self.buffer) > 50 or any(end in chunk for end in ".!?"):
            sentiment = await self._analyze_sentiment(self.buffer)
            
            if self.filter_negative and sentiment < -self.threshold:
                # 부정적인 내용 필터링
                output = f"[필터됨: 부정적 내용 감지 (점수: {sentiment:.2f})]"
            elif not self.filter_negative and sentiment > self.threshold:
                # 긍정적인 내용만 필터링
                output = f"[필터됨: 긍정적 내용 (점수: {sentiment:.2f})]"
            else:
                output = self.buffer
            
            self.buffer = ""
            return output
        
        return ""
    
    async def _analyze_sentiment(self, text: str) -> float:
        """감정 점수 계산 (-1.0 ~ 1.0)"""
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total


# ===== 4. 실시간 요약 생성기 =====

class SummaryTransformer(StreamTransformer):
    """긴 텍스트를 실시간으로 요약"""
    
    def __init__(self, summary_ratio: float = 0.3, min_length: int = 100):
        self.summary_ratio = summary_ratio
        self.min_length = min_length
        self.buffer = ""
        self.sentence_count = 0
        self.key_sentences = []
    
    async def transform(self, chunk: str) -> str:
        """중요한 문장만 추출하여 요약"""
        self.buffer += chunk
        
        # 문장 분리
        sentences = re.split(r'[.!?]+', self.buffer)
        
        # 마지막 불완전한 문장은 버퍼에 유지
        if not chunk.endswith(('.', '!', '?')):
            self.buffer = sentences[-1]
            sentences = sentences[:-1]
        else:
            self.buffer = ""
        
        output = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # 너무 짧은 문장 제외
                continue
            
            self.sentence_count += 1
            importance = await self._calculate_importance(sentence)
            
            # 중요도가 높은 문장만 선택
            if importance > 0.6:
                self.key_sentences.append({
                    "text": sentence,
                    "importance": importance,
                    "position": self.sentence_count
                })
                
                # 일정 개수마다 요약 출력
                if len(self.key_sentences) >= 3:
                    summary = self._generate_summary()
                    output += f"\n📝 요약: {summary}\n"
                    self.key_sentences = []
        
        return output
    
    async def _calculate_importance(self, sentence: str) -> float:
        """문장의 중요도 계산"""
        # 실제로는 TF-IDF, TextRank 등 사용
        
        importance = 0.5  # 기본값
        
        # 키워드 기반 중요도
        important_keywords = ["중요", "핵심", "결론", "따라서", "요약"]
        for keyword in important_keywords:
            if keyword in sentence:
                importance += 0.2
        
        # 길이 기반 (너무 짧거나 긴 문장은 감점)
        if 20 < len(sentence) < 100:
            importance += 0.1
        
        # 위치 기반 (첫 문장과 마지막 문장은 가산점)
        if self.sentence_count <= 3:
            importance += 0.1
        
        return min(1.0, importance)
    
    def _generate_summary(self) -> str:
        """선택된 문장들로 요약 생성"""
        # 중요도 순으로 정렬
        sorted_sentences = sorted(
            self.key_sentences, 
            key=lambda x: x["importance"], 
            reverse=True
        )
        
        # 상위 문장들 선택
        top_sentences = sorted_sentences[:max(1, int(len(sorted_sentences) * self.summary_ratio))]
        
        # 원래 순서대로 재정렬
        top_sentences.sort(key=lambda x: x["position"])
        
        return " ".join(s["text"] for s in top_sentences)


# ===== 5. 코드 포맷팅 변환기 =====

class CodeFormatterTransformer(StreamTransformer):
    """코드를 실시간으로 포맷팅"""
    
    def __init__(self, language: str = "python"):
        self.language = language
        self.buffer = ""
        self.in_code_block = False
        self.code_buffer = ""
    
    async def transform(self, chunk: str) -> str:
        """코드 블록을 감지하고 포맷팅"""
        self.buffer += chunk
        output = ""
        
        # 코드 블록 시작/끝 감지
        if "```" in self.buffer:
            parts = self.buffer.split("```")
            
            for i, part in enumerate(parts):
                if i % 2 == 0:  # 일반 텍스트
                    if not self.in_code_block:
                        output += part
                else:  # 코드 블록
                    if not self.in_code_block:
                        # 코드 블록 시작
                        self.in_code_block = True
                        self.code_buffer = part
                        
                        # 언어 감지
                        lines = part.split('\n')
                        if lines[0].strip():
                            self.language = lines[0].strip()
                            self.code_buffer = '\n'.join(lines[1:])
                    else:
                        # 코드 블록 끝
                        self.code_buffer += part
                        formatted = await self._format_code(self.code_buffer)
                        output += f"```{self.language}\n{formatted}\n```"
                        
                        self.in_code_block = False
                        self.code_buffer = ""
            
            # 마지막 부분 처리
            if self.in_code_block:
                self.buffer = "```" + parts[-1]
            else:
                self.buffer = parts[-1]
        
        return output
    
    async def _format_code(self, code: str) -> str:
        """코드 포맷팅 (언어별)"""
        if self.language == "python":
            return self._format_python(code)
        elif self.language in ["javascript", "js"]:
            return self._format_javascript(code)
        else:
            return code
    
    def _format_python(self, code: str) -> str:
        """Python 코드 포맷팅"""
        # 실제로는 black, autopep8 등 사용
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # 들여쓰기 레벨 감소
            if stripped.startswith(('return', 'break', 'continue', 'pass')):
                formatted_lines.append('    ' * indent_level + stripped)
            elif stripped.endswith(':'):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped in ['else:', 'elif', 'except:', 'finally:']:
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            else:
                formatted_lines.append('    ' * indent_level + stripped)
            
            # 빈 줄 처리
            if not stripped and indent_level > 0:
                indent_level = max(0, indent_level - 1)
        
        return '\n'.join(formatted_lines)
    
    def _format_javascript(self, code: str) -> str:
        """JavaScript 코드 포맷팅"""
        # 간단한 포맷팅 규칙
        code = re.sub(r';\s*', ';\n', code)  # 세미콜론 후 줄바꿈
        code = re.sub(r'{\s*', ' {\n', code)  # 중괄호 스타일
        code = re.sub(r'}\s*', '\n}\n', code)
        return code


# ===== 6. 스트림 파이프라인 =====

class StreamPipeline:
    """여러 변환기를 연결하는 파이프라인"""
    
    def __init__(self):
        self.transformers: List[StreamTransformer] = []
    
    def add(self, transformer: StreamTransformer) -> 'StreamPipeline':
        """변환기 추가"""
        self.transformers.append(transformer)
        return self
    
    async def process(self, input_stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        """파이프라인 실행"""
        stream = input_stream
        
        # 각 변환기를 순차적으로 적용
        for transformer in self.transformers:
            stream = transformer.process_stream(stream)
        
        async for chunk in stream:
            yield chunk


# ===== 7. 고급 사용 예제 =====

class MultiModalStreamTransformer(StreamTransformer):
    """텍스트와 이미지 설명을 함께 처리하는 변환기"""
    
    def __init__(self):
        self.buffer = ""
        self.image_pattern = re.compile(r'\[IMAGE:([^\]]+)\]')
    
    async def transform(self, chunk: str) -> str:
        """이미지 태그를 찾아서 설명 추가"""
        self.buffer += chunk
        output = ""
        
        # 이미지 태그 찾기
        matches = self.image_pattern.finditer(self.buffer)
        last_end = 0
        
        for match in matches:
            # 이미지 전 텍스트
            output += self.buffer[last_end:match.start()]
            
            # 이미지 처리
            image_path = match.group(1)
            description = await self._describe_image(image_path)
            output += f"[이미지: {description}]"
            
            last_end = match.end()
        
        # 남은 텍스트는 버퍼에 유지
        self.buffer = self.buffer[last_end:]
        
        # 문장이 완성되면 출력
        if any(end in chunk for end in ".!?"):
            output += self.buffer
            self.buffer = ""
        
        return output
    
    async def _describe_image(self, image_path: str) -> str:
        """이미지 설명 생성 (시뮬레이션)"""
        # 실제로는 비전 AI API 사용
        descriptions = {
            "sunset.jpg": "노을이 지는 아름다운 해변",
            "cat.png": "귀여운 고양이가 놀고 있는 모습",
            "code.png": "Python 코드 스크린샷"
        }
        
        return descriptions.get(image_path, "이미지")


# ===== 8. 스트림 변환기 팩토리 =====

class StreamTransformerFactory:
    """스트림 변환기 생성 팩토리"""
    
    @staticmethod
    def create_transformer(transformer_type: str, **kwargs) -> StreamTransformer:
        """변환기 타입에 따라 생성"""
        transformers = {
            "translation": TranslationTransformer,
            "sentiment": SentimentFilter,
            "summary": SummaryTransformer,
            "code_format": CodeFormatterTransformer,
            "multimodal": MultiModalStreamTransformer
        }
        
        if transformer_type not in transformers:
            raise ValueError(f"Unknown transformer type: {transformer_type}")
        
        return transformers[transformer_type](**kwargs)
    
    @staticmethod
    def create_pipeline(transformer_configs: List[Dict[str, Any]]) -> StreamPipeline:
        """설정에 따라 파이프라인 생성"""
        pipeline = StreamPipeline()
        
        for config in transformer_configs:
            transformer_type = config.pop("type")
            transformer = StreamTransformerFactory.create_transformer(transformer_type, **config)
            pipeline.add(transformer)
        
        return pipeline 