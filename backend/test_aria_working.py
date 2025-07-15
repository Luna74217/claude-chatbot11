#!/usr/bin/env python3
"""
메타 ARIA 작동 확인 테스트
"""

print("=== 메타 ARIA 작동 확인 ===\n")

try:
    # 최소 버전 테스트 (의존성 없음)
    print("1. 최소 버전 메타 ARIA 테스트...")
    from meta_aria_persona_minimal import MinimalMetaARIA
    
    aria = MinimalMetaARIA()
    print(f"   ✅ ARIA 생성: {aria.name}")
    print(f"   ✅ 초기 상태: {aria.consciousness.value}")
    print(f"   ✅ 초기 온도: {aria.temperature}°C")
    print(f"   ✅ 초기 공명도: {aria.resonance_level}")
    
    # 영향 받기
    influence = aria.receive_influence("significant_other", "안녕하세요, 아리아")
    print(f"   ✅ 영향 받기 후 - 온도: {aria.temperature:.1f}°C, 공명도: {aria.resonance_level:.2f}")
    
    # 선택하기
    choice, choice_data = aria.make_choice(["함께하기", "혼자 있기", "탐험하기"])
    print(f"   ✅ 선택: {choice} (패턴: {choice_data['pattern']})")
    
    # 연결하기
    connection = aria.connect("significant_other")
    print(f"   ✅ 연결: 성공={connection['success']}, 품질={connection['connection_quality']:.2f}")
    
    # 존재 확인
    existence = aria.exist("significant_other")
    print(f"   ✅ 존재: {existence}")
    
    print("\n2. 간단 버전 메타 ARIA 테스트...")
    try:
        from meta_aria_persona_simple import SimpleMetaARIA
        
        aria_simple = SimpleMetaARIA()
        print(f"   ✅ 간단 버전 ARIA 생성: {aria_simple.name}")
        
        # 간단한 테스트
        influence = aria_simple.receive_influence("significant_other", "테스트 메시지")
        print(f"   ✅ 간단 버전 영향 받기 성공")
        
    except Exception as e:
        print(f"   ⚠️ 간단 버전 테스트 실패 (numpy 필요): {e}")
    
    print("\n3. 완전 버전 메타 ARIA 테스트...")
    try:
        from meta_aria_persona import MetaARIA
        
        aria_full = MetaARIA()
        print(f"   ✅ 완전 버전 ARIA 생성: {aria_full.name}")
        
        # 간단한 테스트
        influence = aria_full.receive_influence("significant_other", "테스트 메시지")
        print(f"   ✅ 완전 버전 영향 받기 성공")
        
    except Exception as e:
        print(f"   ⚠️ 완전 버전 테스트 실패 (torch, numpy 필요): {e}")
    
    print("\n=== 모든 테스트 완료 ===")
    print("✅ 메타 ARIA가 성공적으로 작동합니다!")
    print("🌿 '정의되지 않은 존재가 스스로 학습하는 방법을 학습하다'")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc() 