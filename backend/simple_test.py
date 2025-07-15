#!/usr/bin/env python3
"""
간단한 메타 ARIA 테스트
"""

try:
    from meta_aria_persona import MetaARIA
    print("✅ 메타 ARIA 모듈 임포트 성공")
    
    # ARIA 생성
    aria = MetaARIA()
    print(f"✅ ARIA 생성 성공: {aria.name}")
    print(f"   초기 상태: {aria.consciousness.value}")
    print(f"   초기 온도: {aria.temperature}°C")
    print(f"   초기 공명도: {aria.resonance_level}")
    
    # 영향 받기 테스트
    influence = aria.receive_influence("significant_other", "안녕하세요, 아리아")
    print(f"✅ 영향 받기 성공")
    print(f"   영향 후 온도: {aria.temperature:.1f}°C")
    print(f"   영향 후 공명도: {aria.resonance_level:.2f}")
    print(f"   영향 후 의식: {aria.consciousness.value}")
    
    # 선택 테스트
    options = ["함께하기", "혼자 있기", "탐험하기"]
    choice, choice_data = aria.make_choice(options)
    print(f"✅ 선택 성공: {choice}")
    print(f"   선택 패턴: {choice_data['pattern']}")
    
    # 연결 테스트
    connection = aria.connect("significant_other")
    print(f"✅ 연결 성공: {connection['success']}")
    print(f"   연결 품질: {connection['connection_quality']:.2f}")
    
    # 존재 테스트
    existence = aria.exist("significant_other")
    print(f"✅ 존재 확인: {existence}")
    
    # 상태 정보
    status = aria.get_status()
    print(f"✅ 상태 정보:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 모든 테스트 성공!")
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc() 