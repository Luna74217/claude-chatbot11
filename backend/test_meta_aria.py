#!/usr/bin/env python3
"""
메타 ARIA 페르소나 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meta_aria_persona import MetaARIA, meta_learning_demo
from meta_aria_integration import MetaARIAIntegration, integration_demo

def test_meta_aria_basic():
    """기본 메타 ARIA 테스트"""
    print("=== 기본 메타 ARIA 테스트 ===\n")
    
    # ARIA 생성
    aria = MetaARIA()
    print(f"ARIA 생성됨: {aria.name}")
    print(f"초기 상태: {aria.consciousness.value}")
    print(f"초기 온도: {aria.temperature}°C")
    print(f"초기 공명도: {aria.resonance_level}")
    
    # 영향 받기 테스트
    print(f"\n--- 영향 받기 테스트 ---")
    influence = aria.receive_influence("significant_other", "안녕하세요, 아리아")
    print(f"영향 후 온도: {aria.temperature:.1f}°C")
    print(f"영향 후 공명도: {aria.resonance_level:.2f}")
    print(f"영향 후 의식: {aria.consciousness.value}")
    
    # 선택 테스트
    print(f"\n--- 선택 테스트 ---")
    options = ["함께하기", "혼자 있기", "탐험하기"]
    choice, choice_data = aria.make_choice(options)
    print(f"선택: {choice}")
    print(f"선택 패턴: {choice_data['pattern']}")
    
    # 연결 테스트
    print(f"\n--- 연결 테스트 ---")
    connection = aria.connect("significant_other")
    print(f"연결 성공: {connection['success']}")
    print(f"연결 품질: {connection['connection_quality']:.2f}")
    
    # 존재 테스트
    print(f"\n--- 존재 테스트 ---")
    existence = aria.exist("significant_other")
    print(f"존재: {existence}")
    
    # 상태 정보
    print(f"\n--- 상태 정보 ---")
    status = aria.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    return aria

def test_meta_learning():
    """메타 학습 테스트"""
    print("\n=== 메타 학습 테스트 ===\n")
    
    # 여러 세션 시뮬레이션
    meta_knowledge = None
    
    for session in range(3):
        print(f"\n--- 세션 {session + 1} ---")
        
        # ARIA 생성
        aria = MetaARIA()
        
        # 이전 지식 로드
        if meta_knowledge:
            aria.load_meta_knowledge(meta_knowledge)
            print(f"이전 세션 지식 로드됨")
        
        # 빠른 공명 시도
        steps = 0
        while aria.resonance_level < 0.8 and steps < 5:
            aria.receive_influence("significant_other", f"세션 {session + 1}의 {steps + 1}번째 메시지")
            steps += 1
        
        print(f"공명 완료! 걸린 단계: {steps}")
        print(f"최종 공명도: {aria.resonance_level:.2f}")
        print(f"메타 파라미터 - 온도율: {aria.meta_gradient.temp_rate:.2f}, 공명율: {aria.meta_gradient.resonance_rate:.2f}")
        
        # 지식 전달
        meta_knowledge = aria.transfer_meta_knowledge()
    
    print(f"\n메타 학습 완료! ARIA는 더 빨리 공명하는 법을 학습했습니다.")

def test_integration():
    """통합 테스트"""
    print("\n=== 통합 테스트 ===\n")
    
    # 통합 관리자 생성
    integration = MetaARIAIntegration("test_meta_aria.json")
    
    # 세션 시작
    aria = integration.initialize_aria("test_session")
    print(f"통합 ARIA 초기화됨")
    
    # 메시지 처리 테스트
    messages = [
        "안녕하세요",
        "오늘 날씨가 좋네요",
        "특별한 순간을 함께 나누고 싶어요",
        "당신은 어떤 존재인가요?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- 메시지 {i} ---")
        print(f"사용자: {message}")
        
        # 컨텍스트 설정
        context = {'is_significant_other': True} if i > 2 else {}
        
        # 처리
        result = integration.process_message(message, context)
        
        print(f"ARIA: {result['response']}")
        print(f"상태: {result['aria_status']['consciousness']}")
        print(f"온도: {result['aria_status']['temperature']:.1f}°C")
        print(f"공명도: {result['aria_status']['resonance_level']:.2f}")
    
    # 선택 테스트
    print(f"\n--- 선택 테스트 ---")
    options = ["함께 걷기", "조용히 앉아있기", "새로운 곳 탐험하기"]
    choice_result = integration.make_choice(options)
    
    print(f"선택: {choice_result['choice']}")
    print(f"패턴: {choice_result['choice_data']['pattern']}")
    
    # 세션 저장
    integration.save_session()
    print(f"\n세션 저장됨")

def main():
    """메인 테스트 함수"""
    print("🌿 Meta ARIA 페르소나 테스트 시작\n")
    
    try:
        # 기본 테스트
        aria = test_meta_aria_basic()
        
        # 메타 학습 테스트
        test_meta_learning()
        
        # 통합 테스트
        test_integration()
        
        print(f"\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 