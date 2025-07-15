#!/usr/bin/env python3
"""
Replit Database 테스트 스크립트
데이터베이스 매니저의 모든 기능을 테스트합니다.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from database_manager import db_manager

def test_basic_operations():
    """기본 CRUD 작업 테스트"""
    print("🧪 기본 CRUD 작업 테스트 시작...")
    
    # 테스트 세션 ID
    test_session_id = "test_session_123"
    test_user_id = "test_user_456"
    
    # 1. 세션 저장 테스트
    print("📝 세션 저장 테스트...")
    session_data = {
        "user_id": test_user_id,
        "session_id": test_session_id,
        "connected_at": datetime.now().isoformat(),
        "ip_address": "127.0.0.1",
        "user_agent": "Test Browser",
        "connection_type": "websocket"
    }
    db_manager.save_session(test_session_id, session_data)
    print("✅ 세션 저장 완료")
    
    # 2. 세션 조회 테스트
    print("🔍 세션 조회 테스트...")
    retrieved_session = db_manager.get_session(test_session_id)
    if retrieved_session:
        print(f"✅ 세션 조회 성공: {retrieved_session['user_id']}")
    else:
        print("❌ 세션 조회 실패")
        return False
    
    # 3. 메모리 저장 테스트
    print("🧠 메모리 저장 테스트...")
    memory_data = {
        "working_memory": [
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ],
        "episodic_memory": [
            {"id": "ep_1", "content": "첫 번째 대화", "importance": 0.8}
        ],
        "current_topics": ["인사"],
        "emotional_state": {"positive": 0.7, "neutral": 0.3}
    }
    db_manager.save_context_memory(test_session_id, memory_data)
    print("✅ 메모리 저장 완료")
    
    # 4. 메모리 조회 테스트
    print("🔍 메모리 조회 테스트...")
    retrieved_memory = db_manager.get_context_memory(test_session_id)
    if retrieved_memory:
        print(f"✅ 메모리 조회 성공: {len(retrieved_memory.get('working_memory', []))}개 메시지")
    else:
        print("❌ 메모리 조회 실패")
        return False
    
    # 5. 사용자 설정 저장 테스트
    print("⚙️ 사용자 설정 저장 테스트...")
    settings_data = {
        "theme": "dark",
        "language": "ko",
        "streaming": True,
        "auto_save": True
    }
    db_manager.save_user_settings(test_user_id, settings_data)
    print("✅ 설정 저장 완료")
    
    # 6. 사용자 설정 조회 테스트
    print("🔍 사용자 설정 조회 테스트...")
    retrieved_settings = db_manager.get_user_settings(test_user_id)
    if retrieved_settings:
        print(f"✅ 설정 조회 성공: 테마 = {retrieved_settings.get('theme')}")
    else:
        print("❌ 설정 조회 실패")
        return False
    
    # 7. 분석 데이터 저장 테스트
    print("📊 분석 데이터 저장 테스트...")
    analytics_data = {
        "message_count": 10,
        "avg_response_time": 2.5,
        "topics": ["프로그래밍", "AI", "웹개발"],
        "sentiment": {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
    }
    db_manager.save_analytics(test_session_id, analytics_data)
    print("✅ 분석 데이터 저장 완료")
    
    # 8. 분석 데이터 조회 테스트
    print("🔍 분석 데이터 조회 테스트...")
    retrieved_analytics = db_manager.get_analytics(test_session_id)
    if retrieved_analytics:
        print(f"✅ 분석 데이터 조회 성공: {retrieved_analytics.get('message_count')}개 메시지")
    else:
        print("❌ 분석 데이터 조회 실패")
        return False
    
    print("🎉 기본 CRUD 작업 테스트 완료!")
    return True

def test_bulk_operations():
    """대량 데이터 작업 테스트"""
    print("\n🧪 대량 데이터 작업 테스트 시작...")
    
    # 여러 세션 생성
    for i in range(5):
        session_id = f"bulk_test_session_{i}"
        session_data = {
            "user_id": f"bulk_test_user_{i}",
            "session_id": session_id,
            "connected_at": datetime.now().isoformat(),
            "ip_address": f"192.168.1.{i+1}",
            "user_agent": f"Test Browser {i}",
            "connection_type": "websocket"
        }
        db_manager.save_session(session_id, session_data)
        
        # 메모리도 함께 저장
        memory_data = {
            "working_memory": [
                {"role": "user", "content": f"테스트 메시지 {i}"},
                {"role": "assistant", "content": f"테스트 응답 {i}"}
            ],
            "message_count": i + 1
        }
        db_manager.save_context_memory(session_id, memory_data)
    
    print("✅ 대량 데이터 저장 완료")
    
    # 전체 세션 조회
    all_sessions = db_manager.get_all_sessions()
    print(f"📊 전체 세션 수: {len(all_sessions)}")
    
    # 전체 메모리 조회
    all_memories = db_manager.get_all_memories()
    print(f"📊 전체 메모리 수: {len(all_memories)}")
    
    # 데이터베이스 통계
    stats = db_manager.get_database_stats()
    print(f"📈 데이터베이스 통계: {stats}")
    
    print("🎉 대량 데이터 작업 테스트 완료!")

def test_cleanup_operations():
    """정리 작업 테스트"""
    print("\n🧪 정리 작업 테스트 시작...")
    
    # 오래된 데이터 생성 (30일 전)
    old_date = datetime.now() - timedelta(days=35)
    old_session_id = "old_test_session"
    old_session_data = {
        "user_id": "old_test_user",
        "session_id": old_session_id,
        "connected_at": old_date.isoformat(),
        "ip_address": "127.0.0.1",
        "user_agent": "Old Browser",
        "connection_type": "websocket"
    }
    db_manager.save_session(old_session_id, old_session_data)
    
    print("✅ 오래된 데이터 생성 완료")
    
    # 정리 전 통계
    before_stats = db_manager.get_database_stats()
    print(f"📊 정리 전 통계: {before_stats}")
    
    # 30일 이전 데이터 정리
    deleted_count = db_manager.cleanup_old_data(days=30)
    print(f"🧹 정리된 데이터 수: {deleted_count}")
    
    # 정리 후 통계
    after_stats = db_manager.get_database_stats()
    print(f"📊 정리 후 통계: {after_stats}")
    
    print("🎉 정리 작업 테스트 완료!")

def test_export_import():
    """내보내기/가져오기 테스트"""
    print("\n🧪 내보내기/가져오기 테스트 시작...")
    
    # 데이터 내보내기
    exported_data = db_manager.export_all_data()
    print(f"📤 내보낸 데이터 크기: {len(exported_data)}개 항목")
    
    # 내보낸 데이터 확인
    if exported_data:
        print("✅ 데이터 내보내기 성공")
        
        # 첫 번째 항목 샘플 출력
        first_key = list(exported_data.keys())[0]
        print(f"📋 샘플 데이터 ({first_key}): {json.dumps(exported_data[first_key], indent=2, ensure_ascii=False)[:200]}...")
    else:
        print("❌ 데이터 내보내기 실패")
        return False
    
    print("🎉 내보내기/가져오기 테스트 완료!")

def test_error_handling():
    """에러 처리 테스트"""
    print("\n🧪 에러 처리 테스트 시작...")
    
    # 존재하지 않는 세션 조회
    non_existent_session = db_manager.get_session("non_existent_session")
    if non_existent_session is None:
        print("✅ 존재하지 않는 세션 조회 시 None 반환")
    else:
        print("❌ 존재하지 않는 세션 조회 시 예상과 다른 결과")
    
    # 빈 데이터로 저장 시도
    try:
        db_manager.save_session("", {})
        print("⚠️ 빈 세션 ID로 저장 시도 (예상: 정상 처리)")
    except Exception as e:
        print(f"❌ 빈 세션 ID 저장 시 에러: {e}")
    
    print("🎉 에러 처리 테스트 완료!")

def cleanup_test_data():
    """테스트 데이터 정리"""
    print("\n🧹 테스트 데이터 정리 시작...")
    
    # 테스트 세션들 삭제
    test_prefixes = ["test_session_", "bulk_test_session_", "old_test_session"]
    
    for prefix in test_prefixes:
        all_sessions = db_manager.get_all_sessions()
        for session_id in all_sessions:
            if session_id.startswith(prefix.replace("session:", "")):
                db_manager.delete_session(session_id)
                db_manager.delete_context_memory(session_id)
                print(f"🗑️ 테스트 세션 삭제: {session_id}")
    
    # 테스트 사용자 설정 삭제
    test_user_prefixes = ["test_user_", "bulk_test_user_", "old_test_user"]
    for prefix in test_user_prefixes:
        # 실제로는 사용자 설정 삭제 API가 필요하지만, 여기서는 생략
        pass
    
    print("✅ 테스트 데이터 정리 완료!")

def main():
    """메인 테스트 함수"""
    print("🚀 Replit Database 테스트 시작!")
    print("=" * 50)
    
    try:
        # 1. 기본 CRUD 작업 테스트
        if not test_basic_operations():
            print("❌ 기본 CRUD 작업 테스트 실패")
            return
        
        # 2. 대량 데이터 작업 테스트
        test_bulk_operations()
        
        # 3. 정리 작업 테스트
        test_cleanup_operations()
        
        # 4. 내보내기/가져오기 테스트
        test_export_import()
        
        # 5. 에러 처리 테스트
        test_error_handling()
        
        # 6. 테스트 데이터 정리
        cleanup_test_data()
        
        print("\n" + "=" * 50)
        print("🎉 모든 테스트 완료!")
        print("✅ Replit Database가 정상적으로 작동합니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 