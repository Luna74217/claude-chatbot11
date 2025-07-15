import React from 'react';
import { Plus, Search, X } from 'lucide-react';
import { filterConversations, isSearchActive } from '../../utils/searchUtils';

const Sidebar = ({
  sidebarOpen,
  darkMode,
  fontSize,
  searchQuery,
  setSearchQuery,
  searchMode,
  setSearchMode,
  conversations,
  activeConversation,
  filteredConversations,
  isSearching,
  startNewChat,
  switchConversation,
  highlightText,
  getFontSizeClass
}) => {
  return (
    <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 flex-shrink-0 ${darkMode ? 'bg-gray-800' : 'bg-white'} border-r ${darkMode ? 'border-gray-700' : 'border-gray-200'} overflow-hidden`}>
      <div className="p-4">
        <button
          onClick={startNewChat}
          className={`w-full flex items-center gap-2 px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'} transition-colors`}
        >
          <Plus size={20} />
          <span>새 대화</span>
        </button>
      </div>

      <div className="px-4 mb-4">
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
          <Search size={16} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="대화 검색..."
            className={`flex-1 bg-transparent outline-none ${getFontSizeClass()} ${darkMode ? 'text-white placeholder-gray-400' : 'text-gray-700 placeholder-gray-500'}`}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className={`p-1 rounded hover:bg-gray-600 transition-colors`}
            >
              <X size={14} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
            </button>
          )}
        </div>

        {/* 검색 모드 선택 */}
        {searchQuery && (
          <div className="flex gap-1 mt-2">
            {[
              { value: 'all', label: '전체' },
              { value: 'title', label: '제목' },
              { value: 'content', label: '내용' }
            ].map(mode => (
              <button
                key={mode.value}
                onClick={() => setSearchMode(mode.value)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  searchMode === mode.value
                    ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white'
                    : darkMode ? 'bg-gray-600 text-gray-300' : 'bg-gray-200 text-gray-600'
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="overflow-y-auto px-2">
        {searchQuery && filteredConversations.length === 0 && (
          <div className={`text-center py-8 px-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <Search size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">"{searchQuery}"에 대한</p>
            <p className="text-sm">검색 결과가 없습니다</p>
          </div>
        )}

        {!searchQuery && (
          <div className={`px-4 py-2 mb-2 text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            💡 팁: 대화 내용을 검색하려면 위 검색창을 사용하세요
          </div>
        )}

        {filteredConversations.map(conv => (
          <button
            key={conv.id}
            onClick={() => switchConversation(conv.id)}
            className={`w-full text-left p-3 rounded-lg mb-1 transition-colors ${
              activeConversation === conv.id
                ? darkMode ? 'bg-gray-700' : 'bg-gray-100'
                : darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
            }`}
          >
            <div className={`font-medium ${getFontSizeClass()} ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              {isSearching && searchMode !== 'content' ? 
                highlightText(conv.title, searchQuery, darkMode) : 
                conv.title
              }
            </div>
            <div className={`${fontSize === 'large' ? 'text-sm' : 'text-xs'} ${darkMode ? 'text-gray-400' : 'text-gray-500'} truncate mt-1`}>
              {conv.lastMessage}
            </div>
            <div className={`${fontSize === 'large' ? 'text-sm' : 'text-xs'} ${darkMode ? 'text-gray-500' : 'text-gray-400'} mt-1 flex items-center justify-between`}>
              <span>{conv.time}</span>
              {isSearching && searchMode !== 'title' && conv.messages?.some(msg => 
                msg.content.toLowerCase().includes(searchQuery.toLowerCase())
              ) && (
                <span className={`px-1.5 py-0.5 rounded ${fontSize === 'large' ? 'text-sm' : 'text-xs'} ${darkMode ? 'bg-blue-600/20 text-blue-400' : 'bg-blue-100 text-blue-600'}`}>
                  내용 일치
                </span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default Sidebar; 