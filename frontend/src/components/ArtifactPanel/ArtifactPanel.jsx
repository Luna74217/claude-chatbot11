import React from 'react';
import { X, FileText, Search } from 'lucide-react';

const ArtifactPanel = ({
  artifactOpen,
  setArtifactOpen,
  darkMode,
  searchQuery,
  filteredConversations
}) => {
  return (
    <div className={`${artifactOpen ? 'w-96' : 'w-0'} transition-all duration-300 flex-shrink-0 ${darkMode ? 'bg-gray-800' : 'bg-white'} border-l ${darkMode ? 'border-gray-700' : 'border-gray-200'} overflow-hidden`}>
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>아티팩트</h2>
          <button
            onClick={() => setArtifactOpen(false)}
            className={`p-1.5 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <X size={18} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
          </button>
        </div>

        <div className={`rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} p-4`}>
          <div className="flex items-center gap-2 mb-3">
            <FileText size={16} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
            <span className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Claude UI 구현.tsx
            </span>
          </div>

          <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'} font-mono`}>
            <div>// Claude 스타일 UI 클론</div>
            <div>// - 3단 레이아웃</div>
            <div>// - 다크모드 지원</div>
            <div>// - 반응형 디자인</div>
            <div>// - 타이핑 애니메이션</div>
            <div>// - 마크다운 렌더링</div>
            <div>// - 코드 하이라이팅</div>
            <div>// - 파일 업로드 & 드래그 앤 드롭</div>
            <div>// - 파일 미리보기</div>
            <div>// - 대화 내용 검색</div>
            <div>// - 검색어 하이라이팅</div>
            <div>// - 설정 메뉴</div>
          </div>
        </div>

        <div className={`mt-4 p-4 rounded-lg ${darkMode ? 'bg-gray-900' : 'bg-blue-50'}`}>
          <h3 className={`text-sm font-medium mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            구현된 기능
          </h3>
          <ul className={`text-xs space-y-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            <li>✓ 대화 목록 관리</li>
            <li>✓ 메시지 전송/표시</li>
            <li>✓ 다크모드 토글</li>
            <li>✓ 자동 스크롤</li>
            <li>✓ 반응형 텍스트 입력</li>
            <li>✓ 메시지 복사</li>
            <li>✓ 타이핑 인디케이터</li>
            <li>✓ 마크다운 렌더링</li>
            <li>✓ 코드 블록 하이라이팅</li>
            <li>✓ 파일 업로드 (드래그 앤 드롭)</li>
            <li>✓ 파일 미리보기</li>
            <li>✓ 대화 내용 검색</li>
            <li>✓ 검색어 하이라이팅</li>
            <li>✓ 검색 모드 (전체/제목/내용)</li>
            <li>✓ 설정 메뉴 (폰트, 삭제, 초기화)</li>
          </ul>
        </div>

        {searchQuery && (
          <div className={`mt-4 p-4 rounded-lg ${darkMode ? 'bg-purple-900/20' : 'bg-purple-50'} border ${darkMode ? 'border-purple-700' : 'border-purple-200'}`}>
            <h3 className={`text-sm font-medium mb-2 ${darkMode ? 'text-purple-300' : 'text-purple-900'} flex items-center gap-2`}>
              <Search size={16} />
              검색 중: "{searchQuery}"
            </h3>
            <p className={`text-xs ${darkMode ? 'text-purple-400' : 'text-purple-700'}`}>
              {filteredConversations.length}개의 대화에서 일치하는 내용을 찾았습니다.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArtifactPanel; 