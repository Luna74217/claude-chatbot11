# 🚀 테스트 실행 가이드 (Path Mapping 적용)

## ✅ **설정 완료 사항**

### 1. TypeScript Path Mapping
```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@components/*": ["components/*"],
      "@utils/*": ["utils/*"],
      "@types/*": ["types/*"]
    }
  }
}
```

### 2. Jest Module Mapping
```javascript
// jest.config.js
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
  '^@components/(.*)$': '<rootDir>/src/components/$1',
  '^@utils/(.*)$': '<rootDir>/src/utils/$1',
  '^@types/(.*)$': '<rootDir>/src/types/$1'
}
```

### 3. Replit 환경 감지
```typescript
// src/test-utils/pathResolver.ts
const isReplit = process.env.REPL_ID !== undefined;
```

## 🎯 **테스트 실행 방법**

### **환경별 실행 명령어**

#### 1. **Replit 환경**
```bash
cd claude-chatbot/frontend
npm run test:replit
```

#### 2. **로컬 환경**
```bash
cd claude-chatbot/frontend
npm run test:local
```

#### 3. **React Scripts (기본)**
```bash
cd claude-chatbot/frontend
npm test
```

### **단계별 테스트 실행**

#### 1단계: Smoke Test
```bash
npm test -- --testPathPattern=smoke.test.tsx --watchAll=false
```

#### 2단계: 컴포넌트 테스트
```bash
# App 컴포넌트
npm test -- --testPathPattern=App.test.tsx --watchAll=false

# Dashboard 컴포넌트
npm test -- --testPathPattern=Dashboard.test.tsx --watchAll=false

# EntityXStateMonitor 컴포넌트
npm test -- --testPathPattern=EntityXStateMonitor.test.tsx --watchAll=false
```

#### 3단계: 유틸리티 테스트
```bash
# 파일 유틸리티
npm test -- --testPathPattern=fileUtils.test.ts --watchAll=false

# 검색 유틸리티
npm test -- --testPathPattern=searchUtils.test.ts --watchAll=false

# 스토리지 유틸리티
npm test -- --testPathPattern=storageUtils.test.ts --watchAll=false
```

## 📊 **예상 결과**

### **성공 시나리오**
```
✅ Smoke Test: 3개 통과
✅ App Test: 3개 통과  
✅ Dashboard Test: 5개 통과
✅ EntityXStateMonitor Test: 2개 통과
✅ fileUtils Test: 8개 통과
✅ searchUtils Test: 16개 통과
✅ storageUtils Test: 8개 통과

총 45개 테스트 케이스
실행 시간: 15-20초
```

### **실패 시나리오**
```
❌ 모듈을 찾을 수 없음
   → Path Mapping 설정 확인
   → Jest 설정 확인

❌ TypeScript 컴파일 오류
   → tsconfig.json 확인
   → 의존성 설치 확인

❌ localStorage Mock 오류
   → setupTests.ts 확인
```

## 🔧 **문제 해결**

### **Path Mapping이 작동하지 않을 때**
```bash
# 1. TypeScript 설정 확인
npx tsc --noEmit

# 2. Jest 설정 확인
npx jest --showConfig

# 3. 캐시 클리어
npm test -- --clearCache
```

### **Replit에서 특별한 문제**
```bash
# 1. 환경 변수 확인
echo $REPL_ID

# 2. NODE_PATH 설정
export NODE_PATH=./src

# 3. 강제 실행
npm run test:replit
```

## 🎉 **완료!**

이제 모든 import 경로가 통일되어 어디서든 동일하게 작동합니다!

```typescript
// 어디서든 동일한 import 사용 가능
import { Message } from '@/types';
import Dashboard from '@/Dashboard';
import { formatFileSize } from '@/utils/fileUtils';
``` 