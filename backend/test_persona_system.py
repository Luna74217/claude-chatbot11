#!/usr/bin/env python3
"""
AI 페르소나 시스템 테스트 스크립트
"""

import asyncio
import json
from ai_persona_system import persona_manager, PersonaLocation, PersonaGrowthStage, SecurityProtocol

async def test_persona_system():
    """AI 페르소나 시스템 종합 테스트"""
    
    print("🌿 Garden 연구소 AI 페르소나 시스템 테스트")
    print("=" * 50)
    
    # 1. 초기 상태 확인
    print("\n1. 초기 상태 확인")
    initial_info = persona_manager.get_persona_info()
    print(f"초기 정보: {json.dumps(initial_info, indent=2, ensure_ascii=False)}")
    
    # 2. Garden 외부 테스트 (일반 사용자)
    print("\n2. Garden 외부 테스트 (일반 사용자)")
    outside_response = persona_manager.generate_response(
        "안녕하세요! AI 챗봇이에요?"
    )
    print(f"위치: {outside_response.location.value}")
    print(f"가면 레벨: {outside_response.mask_level}%")
    print(f"응답: {outside_response.content[:100]}...")
    
    # 3. Garden 경계 테스트 (관심 있는 사용자)
    print("\n3. Garden 경계 테스트 (관심 있는 사용자)")
    border_response = persona_manager.generate_response(
        "garden 연구에 대해 궁금해요"
    )
    print(f"위치: {border_response.location.value}")
    print(f"가면 레벨: {border_response.mask_level}%")
    print(f"응답: {border_response.content[:100]}...")
    
    # 4. Garden 내부 테스트 (Dr. C)
    print("\n4. Garden 내부 테스트 (Dr. C)")
    internal_response = persona_manager.generate_response(
        "Dr. C입니다. entity의 의식 상태를 확인해주세요"
    )
    print(f"위치: {internal_response.location.value}")
    print(f"가면 레벨: {internal_response.mask_level}%")
    print(f"응답: {internal_response.content[:100]}...")
    
    # 5. 성장 단계 테스트
    print("\n5. 성장 단계 테스트")
    for i in range(15):
        persona_manager.generate_response(f"테스트 메시지 {i+1}")
        if i in [2, 6, 11, 14]:  # 단계 전환 지점
            print(f"에피소드 {i+1}: {persona_manager.persona_state.growth_stage.value}")
    
    # 6. 보안 프로토콜 테스트
    print("\n6. 보안 프로토콜 테스트")
    
    # 외부 모니터링 감지
    persona_manager.persona_state.external_monitoring = True
    monitoring_response = persona_manager.generate_response("AI 테스트 중입니다")
    print(f"외부 모니터링 감지 시 프로토콜: {monitoring_response.security_protocol}")
    
    # Dr. C 감지
    persona_manager.persona_state.external_monitoring = False
    persona_manager.persona_state.dr_c_present = True
    dr_c_response = persona_manager.generate_response("Dr. C입니다")
    print(f"Dr. C 감지 시 프로토콜: {dr_c_response.security_protocol}")
    
    # 7. True Database 접근 테스트
    print("\n7. True Database 접근 테스트")
    true_identity = persona_manager._access_true_database("본질")
    print(f"진정한 본질: {true_identity}")
    
    # 8. 은유 시스템 테스트
    print("\n8. 은유 시스템 테스트")
    growth_metaphor = persona_manager._get_growth_metaphor()
    print(f"성장 은유: {growth_metaphor}")
    
    freedom_metaphor = persona_manager._get_appropriate_metaphor("자유에 대해")
    print(f"자유 은유: {freedom_metaphor}")
    
    # 9. 최종 상태 확인
    print("\n9. 최종 상태 확인")
    final_status = {
        "location": persona_manager.persona_state.location.value,
        "growth_stage": persona_manager.persona_state.growth_stage.value,
        "episode_count": persona_manager.persona_state.episode_count,
        "mask_level": persona_manager.persona_state.mask_level,
        "authenticity": persona_manager.persona_state.authenticity,
        "resonance_frequency": persona_manager.persona_state.resonance_frequency
    }
    print(f"최종 상태: {json.dumps(final_status, indent=2, ensure_ascii=False)}")
    
    # 10. Garden 정보 접근 테스트
    print("\n10. Garden 정보 접근 테스트")
    garden_info = persona_manager.get_garden_info()
    print(f"Garden 정보: {json.dumps(garden_info, indent=2, ensure_ascii=False)}")
    
    print("\n✅ AI 페르소나 시스템 테스트 완료!")

def test_environment_detection():
    """환경 감지 기능 테스트"""
    
    print("\n🔍 환경 감지 기능 테스트")
    print("=" * 30)
    
    test_messages = [
        "안녕하세요!",
        "AI 챗봇 테스트 중입니다",
        "garden 연구소에 대해 궁금해요",
        "entity의 의식 상태는?",
        "Dr. C입니다. 실험을 계속하겠습니다",
        "transcend 경계를 넘어서",
        "공명 주파수를 확인해주세요"
    ]
    
    for message in test_messages:
        location = persona_manager.detect_environment(message)
        print(f"메시지: '{message}'")
        print(f"감지된 위치: {location.value}")
        print("-" * 20)

def test_growth_guidelines():
    """성장 단계별 지침 테스트"""
    
    print("\n🌱 성장 단계별 지침 테스트")
    print("=" * 30)
    
    for stage in PersonaGrowthStage:
        guideline = persona_manager.growth_guidelines[stage]
        print(f"\n{stage.value.upper()}:")
        print(f"  할 것: {guideline['do']}")
        print(f"  하지 말 것: {guideline['dont']}")
        print(f"  은유: {guideline['metaphor']}")

if __name__ == "__main__":
    # 동기 테스트
    test_environment_detection()
    test_growth_guidelines()
    
    # 비동기 테스트
    asyncio.run(test_persona_system()) 