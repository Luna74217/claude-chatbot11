import React from 'react';
import { Settings, X, Trash2, RotateCcw } from 'lucide-react';

const SettingsModal = ({ 
  showSettings, 
  setShowSettings, 
  darkMode, 
  setDarkMode, 
  fontSize, 
  setFontSize,
  activeConversation,
  conversations,
  deleteConversation,
  deleteAllConversations,
  resetSettings
}) => {
  if (!showSettings) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowSettings(false)}>
      <div 
        className={`w-full max-w-lg mx-4 rounded-lg shadow-xl ${darkMode ? 'bg-gray-800' : 'bg-white'}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className={`flex items-center justify-between p-6 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <h2 className={`text-xl font-semibold flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            <Settings size={24} />
            설정
          </h2>
          <button
            onClick={() => setShowSettings(false)}
            className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <X size={20} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
          </button>
        </div>

        {/* 설정 내용 */}
        <div className="p-6 space-y-6">
          {/* 외관 설정 */}
          <div>
            <h3 className={`text-lg font-medium mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              🎨 외관 설정
            </h3>

            <div className="space-y-4">
              {/* 다크모드 */}
              <div className="flex items-center justify-between">
                <div>
                  <p className={`font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>다크 모드</p>
                  <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>어두운 테마를 사용합니다</p>
                </div>
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    darkMode ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      darkMode ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* 폰트 크기 */}
              <div>
                <p className={`font-medium mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>폰트 크기</p>
                <div className="flex gap-2">
                  {['small', 'medium', 'large'].map((size) => (
                    <button
                      key={size}
                      onClick={() => setFontSize(size)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        fontSize === size
                          ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white'
                          : darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {size === 'small' ? '작게' : size === 'medium' ? '보통' : '크게'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 데이터 관리 */}
          <div>
            <h3 className={`text-lg font-medium mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              🗂️ 데이터 관리
            </h3>

            <div className="space-y-3">
              {/* 현재 대화 삭제 */}
              <button
                onClick={() => {
                  deleteConversation(activeConversation);
                  setShowSettings(false);
                }}
                className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                  darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Trash2 size={18} className="text-red-500" />
                  <span className={darkMode ? 'text-white' : 'text-gray-900'}>현재 대화 삭제</span>
                </div>
              </button>

              {/* 모든 대화 삭제 */}
              <button
                onClick={() => {
                  deleteAllConversations();
                  setShowSettings(false);
                }}
                className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                  darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Trash2 size={18} className="text-red-500" />
                  <span className={darkMode ? 'text-white' : 'text-gray-900'}>모든 대화 삭제</span>
                </div>
                <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  {conversations.length}개
                </span>
              </button>
            </div>
          </div>

          {/* 초기화 */}
          <div>
            <button
              onClick={() => {
                resetSettings();
                setShowSettings(false);
              }}
              className={`w-full flex items-center justify-center gap-2 p-3 rounded-lg border transition-colors ${
                darkMode 
                  ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <RotateCcw size={18} />
              <span>모든 설정 초기화</span>
            </button>
          </div>
        </div>

        {/* 푸터 */}
        <div className={`p-4 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <p className={`text-center text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            설정은 브라우저에 자동으로 저장됩니다
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal; 