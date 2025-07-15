# 🧪 테스트 환경 설정 가이드

## 📋 사전 준비사항

### 1. 의존성 설치
```bash
cd claude-chatbot/frontend
npm install --save-dev @types/jest jest jest-environment-jsdom ts-jest identity-obj-proxy @types/node
```

### 2. 설정 파일 확인
- ✅ `jest.config.js` - Jest 설정
- ✅ `src/setupTests.ts` - 테스트 환경 설정
- ✅ `src/test-utils.tsx` - 테스트 유틸리티

## 🚀 테스트 실행 단계

### 1단계: Smoke Test 실행
```bash
npm test -- --testPathPattern=smoke.test.tsx --watchAll=false
```

### 2단계: 개별 컴포넌트 테스트
```bash
# App 컴포넌트 테스트
npm test -- --testPathPattern=App.test.tsx --watchAll=false

# Dashboard 컴포넌트 테스트
npm test -- --testPathPattern=Dashboard.test.tsx --watchAll=false

# EntityXStateMonitor 컴포넌트 테스트
npm test -- --testPathPattern=EntityXStateMonitor.test.tsx --watchAll=false
```

### 3단계: 유틸리티 테스트
```bash
# 파일 유틸리티 테스트
npm test -- --testPathPattern=fileUtils.test.ts --watchAll=false

# 검색 유틸리티 테스트
npm test -- --testPathPattern=searchUtils.test.ts --watchAll=false

# 스토리지 유틸리티 테스트
npm test -- --testPathPattern=storageUtils.test.ts --watchAll=false
```

### 4단계: 전체 테스트 실행
```bash
npm test -- --watchAll=false --passWithNoTests
```

## 🔧 문제 해결

### TypeScript 오류 발생 시
```bash
# TypeScript 설정 확인
npx tsc --noEmit

# Jest 타입 확인
npx jest --showConfig
```

### 모듈을 찾을 수 없을 때
```bash
# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

### localStorage Mock 오류
- `setupTests.ts`에서 전역 mock 설정 확인
- 개별 테스트에서 중복 mock 설정 제거

## 📊 예상 결과

- ✅ Smoke Test: 3개 테스트 통과
- ✅ App Test: 3개 테스트 통과
- ✅ Dashboard Test: 5개 테스트 통과
- ✅ EntityXStateMonitor Test: 2개 테스트 통과
- ✅ fileUtils Test: 8개 테스트 통과
- ✅ searchUtils Test: 12개 테스트 통과
- ✅ storageUtils Test: 8개 테스트 통과

**총 41개 테스트 케이스**

## 🎯 성공 기준

1. 모든 테스트가 30초 이내에 완료
2. 테스트 실패율 0%
3. TypeScript 컴파일 오류 없음
4. Jest 설정 오류 없음 