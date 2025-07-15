#!/usr/bin/env python3
"""
스트림 변환기 테스트 스크립트
"""

import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stream_transformers import (
    TranslationTransformer, SentimentFilter, SummaryTransformer,
    CodeFormatterTransformer, StreamPipeline, StreamTransformerFactory
)

async def test_translation():
    """번역 변환기 테스트"""
    print("=== 번역 변환기 테스트 ===")
    
    async def korean_stream():
        text = "안녕하세요. 오늘 날씨가 좋네요. 감사합니다."
        for char in text:
            yield char
            await asyncio.sleep(0.05)
    
    translator = TranslationTransformer()
    
    print("원본: ", end="", flush=True)
    async for chunk in korean_stream():
        print(chunk, end="", flush=True)
    
    print("\n번역: ", end="", flush=True)
    async for translated in translator.process_stream(korean_stream()):
        print(translated, end="", flush=True)
    print()

async def test_sentiment_filter():
    """감정 필터 테스트"""
    print("\n=== 감정 필터 테스트 ===")
    
    async def mixed_sentiment_stream():
        texts = [
            "오늘 정말 좋은 하루였어요! ",
            "날씨도 좋고 기분도 최고입니다. ",
            "하지만 일이 너무 많아서 짜증나네요. ",
            "그래도 긍정적으로 생각하려고 해요."
        ]
        for text in texts:
            yield text
            await asyncio.sleep(0.2)
    
    filter = SentimentFilter(filter_negative=True)
    
    async for filtered in filter.process_stream(mixed_sentiment_stream()):
        print(f"필터 결과: {filtered}")

async def test_code_formatting():
    """코드 포맷팅 테스트"""
    print("\n=== 코드 포맷팅 테스트 ===")
    
    async def code_stream():
        code = '''일반 텍스트입니다.
```python
def hello(name):
print(f"Hello, {name}!")
if name == "CHOI":
print("특별한 사용자입니다!")
return True
else:
return False
```
코드가 포맷팅되었습니다!'''
        
        chunk_size = 20
        for i in range(0, len(code), chunk_size):
            yield code[i:i+chunk_size]
            await asyncio.sleep(0.1)
    
    formatter = CodeFormatterTransformer()
    
    async for formatted in formatter.process_stream(code_stream()):
        print(formatted, end="")
    print()

async def test_pipeline():
    """파이프라인 테스트"""
    print("\n=== 스트림 파이프라인 테스트 ===")
    
    async def story_stream():
        story = """안녕하세요. 오늘은 정말 특별한 날이었습니다.
아침에 일어나니 날씨가 너무 좋았어요.
공원을 산책하면서 아름다운 꽃들을 보았습니다.
점심은 가족들과 함께 맛있게 먹었습니다.
오후에는 친구들을 만나서 즐거운 시간을 보냈어요.
저녁에는 좋아하는 영화를 보면서 하루를 마무리했습니다.
정말 행복한 하루였습니다. 감사합니다!"""
        
        for sentence in story.split('\n'):
            yield sentence + " "
            await asyncio.sleep(0.2)
    
    # 파이프라인 구성
    pipeline = StreamPipeline()
    pipeline.add(TranslationTransformer())
    pipeline.add(SentimentFilter(filter_negative=False))
    pipeline.add(SummaryTransformer())
    
    async for result in pipeline.process(story_stream()):
        if result.strip():
            print(f"파이프라인 출력: {result}")

async def test_factory():
    """팩토리 테스트"""
    print("\n=== 팩토리 테스트 ===")
    
    # 설정으로 변환기 생성
    configs = [
        {"type": "translation", "source_lang": "ko", "target_lang": "en"},
        {"type": "sentiment", "filter_negative": True, "threshold": 0.3},
        {"type": "code_format", "language": "python"}
    ]
    
    pipeline = StreamTransformerFactory.create_pipeline(configs)
    print(f"팩토리로 생성된 파이프라인: {len(pipeline.transformers)}개 변환기")
    
    for i, transformer in enumerate(pipeline.transformers):
        print(f"  {i+1}. {type(transformer).__name__}")

async def main():
    """모든 테스트 실행"""
    print("🚀 스트림 변환기 테스트 시작\n")
    
    try:
        await test_translation()
        await test_sentiment_filter()
        await test_code_formatting()
        await test_pipeline()
        await test_factory()
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 