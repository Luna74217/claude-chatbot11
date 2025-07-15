#!/usr/bin/env python3
"""
설치된 패키지 확인 스크립트
"""

print("=== 메타 ARIA 의존성 확인 ===\n")

# torch 확인
try:
    import torch
    print("✅ torch 설치됨 - 버전:", torch.__version__)
except ImportError:
    print("❌ torch 설치되지 않음")

# numpy 확인
try:
    import numpy
    print("✅ numpy 설치됨 - 버전:", numpy.__version__)
except ImportError:
    print("❌ numpy 설치되지 않음")

# 메타 ARIA 최소 버전 테스트
try:
    from meta_aria_persona_minimal import MinimalMetaARIA
    print("✅ 메타 ARIA 최소 버전 임포트 성공")
    
    # 간단한 테스트
    aria = MinimalMetaARIA()
    print("✅ 메타 ARIA 생성 성공:", aria.name)
    
    # 영향 받기 테스트
    influence = aria.receive_influence("significant_other", "안녕하세요")
    print("✅ 영향 받기 성공 - 온도:", aria.temperature, "공명도:", aria.resonance_level)
    
except Exception as e:
    print("❌ 메타 ARIA 테스트 실패:", e)

print("\n=== 확인 완료 ===") 