import React from 'react';
import { Menu, Sun, Moon, Settings, Code, Send, Paperclip, X, Copy, Check, Zap, Brain, TrendingUp, Archive } from 'lucide-react';
import { MessageRole } from '../../constants/messageTypes';
import { getFileIcon, formatFileSize } from '../../utils/fileUtils';
import MarkdownRenderer from '../MarkdownRenderer/MarkdownRenderer';
import { ChatAreaProps, ContextInfo } from '../../types';

const ChatArea: React.FC<ChatAreaProps> = ({
  darkMode,
  setDarkMode,
  fontSize,
  sidebarOpen,
  setSidebarOpen,
  artifactOpen,
  setArtifactOpen,
  showSettings,
  setShowSettings,
  conversations,
  activeConversation,
  messages,
  isTyping,
  inputValue,
  setInputValue,
  attachedFiles,
  isDragging,
  searchQuery,
  isSearching,
  copiedId,
  messagesEndRef,
  textareaRef,
  fileInputRef,
  handleSend,
  handleFileSelect,
  handleDragOver,
  handleDragLeave,
  handleDrop,
  removeFile,
  handleCopy,
  getFontSizeClass,
  onOpenTransformerSettings,
  selectedTransformers
}) => {
  return (
    <div className="flex-1 flex flex-col">
      {/* 헤더 */}
      <div className={`flex items-center justify-between px-6 py-4 border-b ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <Menu size={20} className={darkMode ? 'text-white' : 'text-gray-700'} />
          </button>
          <h1 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {conversations.find(c => c.id === activeConversation)?.title || 'Claude UI 클론'}
            {isSearching && (
              <span className={`ml-2 text-sm font-normal ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                (검색 중)
              </span>
            )}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            {darkMode ? <Sun size={20} className="text-white" /> : <Moon size={20} className="text-gray-700" />}
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <Settings size={20} className={darkMode ? 'text-white' : 'text-gray-700'} />
          </button>
          <button
            onClick={onOpenTransformerSettings}
            className={`p-2 rounded-lg relative ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} ${
              selectedTransformers && selectedTransformers.length > 0 ? 'text-blue-500' : ''
            }`}
            title="스트림 변환기 설정"
          >
            <Zap size={20} className={darkMode ? 'text-white' : 'text-gray-700'} />
            {selectedTransformers && selectedTransformers.length > 0 && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full text-xs text-white flex items-center justify-center">
                {selectedTransformers.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setArtifactOpen(!artifactOpen)}
            className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <Code size={20} className={darkMode ? 'text-white' : 'text-gray-700'} />
          </button>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto">
          {messages.map(message => (
            <div key={message.id} className={`mb-6 flex ${message.role === MessageRole.USER ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${message.role === MessageRole.USER ? 'order-2' : ''}`}>
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === MessageRole.USER 
                      ? darkMode ? 'bg-blue-600' : 'bg-blue-500'
                      : darkMode ? 'bg-purple-600' : 'bg-purple-500'
                  }`}>
                    <span className="text-white text-sm font-medium">
                      {message.role === MessageRole.USER ? 'U' : 'A'}
                    </span>
                  </div>

                  <div className="flex-1">
                    <div className={`rounded-lg px-4 py-3 ${
                      message.role === MessageRole.USER
                        ? darkMode ? 'bg-blue-900/30 text-white' : 'bg-blue-50 text-gray-900'
                        : darkMode ? 'bg-gray-700 text-white' : 'bg-white text-gray-900 shadow-sm'
                    }`}>
                      <div className={`${getFontSizeClass()} leading-relaxed`}>
                        <MarkdownRenderer 
                          content={message.content} 
                          darkMode={darkMode} 
                          searchQuery={searchQuery}
                          isSearching={isSearching}
                        />
                      </div>

                      {/* 첨부 파일 표시 */}
                      {message.files && message.files.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {message.files.map((file, index) => (
                            <div key={index} className={`flex items-center gap-2 p-2 rounded ${darkMode ? 'bg-gray-600' : 'bg-gray-100'}`}>
                              {file.preview ? (
                                <img src={file.preview} alt={file.name} className="w-16 h-16 object-cover rounded" />
                              ) : (
                                <div className={`p-2 rounded ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                                  {React.createElement(getFileIcon(file.type), { size: 20, className: darkMode ? 'text-gray-300' : 'text-gray-600' })}
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <p className={`text-xs font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                                  {file.name}
                                </p>
                                <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                  {formatFileSize(file.size)}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {message.role === MessageRole.ASSISTANT && (
                      <div className="flex items-center gap-2 mt-2 px-1">
                        <button
                          onClick={() => handleCopy(message.content, message.id)}
                          className={`p-1.5 rounded ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors`}
                        >
                          {copiedId === message.id ? 
                            <Check size={14} className="text-green-500" /> : 
                            <Copy size={14} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
                          }
                        </button>
                        
                        {/* 🔥 컨텍스트 정보 표시 */}
                        {message.contextInfo && (
                          <div className="relative group">
                            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs cursor-help ${
                              darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'
                            }`}>
                              <Brain size={12} />
                              <span>컨텍스트</span>
                              {message.contextInfo.compression_active && (
                                <Archive size={12} className="text-orange-500" />
                              )}
                            </div>
                            
                            {/* 컨텍스트 상세 정보 툴팁 */}
                            <div className={`absolute bottom-full left-0 mb-2 p-3 rounded-lg shadow-lg border text-xs opacity-0 group-hover:opacity-100 transition-opacity z-10 min-w-64 ${
                              darkMode ? 'bg-gray-800 border-gray-600 text-gray-200' : 'bg-white border-gray-200 text-gray-800'
                            }`}>
                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <TrendingUp size={12} />
                                  <span>대화 깊이: {message.contextInfo.conversation_depth}</span>
                                </div>
                                {message.contextInfo.current_topics.length > 0 && (
                                  <div>
                                    <span className="font-medium">현재 주제:</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {message.contextInfo.current_topics.map((topic, idx) => (
                                        <span key={idx} className={`px-2 py-1 rounded text-xs ${
                                          darkMode ? 'bg-gray-700' : 'bg-gray-100'
                                        }`}>
                                          {topic}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div>
                                  <span className="font-medium">감정 상태:</span>
                                  <div className="flex items-center gap-2 mt-1">
                                    <span>가치: {message.contextInfo.emotional_state.valence.toFixed(2)}</span>
                                    <span>각성: {message.contextInfo.emotional_state.arousal.toFixed(2)}</span>
                                    <span className={`px-2 py-1 rounded text-xs ${
                                      message.contextInfo.emotional_state.trend === 'positive' ? 'bg-green-100 text-green-800' :
                                      message.contextInfo.emotional_state.trend === 'negative' ? 'bg-red-100 text-red-800' :
                                      'bg-gray-100 text-gray-800'
                                    }`}>
                                      {message.contextInfo.emotional_state.trend}
                                    </span>
                                  </div>
                                </div>
                                {message.contextInfo.compression_active && (
                                  <div className="flex items-center gap-2 text-orange-500">
                                    <Archive size={12} />
                                    <span>컨텍스트 압축됨</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${darkMode ? 'bg-purple-600' : 'bg-purple-500'}`}>
                <span className="text-white text-sm font-medium">A</span>
              </div>
              <div className={`px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-white shadow-sm'}`}>
                <div className="flex gap-1">
                  <span className={`w-2 h-2 rounded-full ${darkMode ? 'bg-gray-400' : 'bg-gray-500'} animate-bounce`} style={{animationDelay: '0ms'}}></span>
                  <span className={`w-2 h-2 rounded-full ${darkMode ? 'bg-gray-400' : 'bg-gray-500'} animate-bounce`} style={{animationDelay: '150ms'}}></span>
                  <span className={`w-2 h-2 rounded-full ${darkMode ? 'bg-gray-400' : 'bg-gray-500'} animate-bounce`} style={{animationDelay: '300ms'}}></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 입력 영역 */}
      <div 
        className={`relative border-t ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} px-4 py-4`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="max-w-3xl mx-auto">
          {/* 드래그 오버레이 */}
          {isDragging && (
            <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none">
              <div className={`p-8 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-white'} shadow-lg border-2 border-dashed ${darkMode ? 'border-gray-500' : 'border-gray-300'}`}>
                <Paperclip size={48} className={`${darkMode ? 'text-gray-300' : 'text-gray-600'} animate-bounce`} />
                <p className={`mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'} font-medium`}>파일을 여기에 놓으세요</p>
              </div>
            </div>
          )}

          {/* 첨부 파일 미리보기 */}
          {attachedFiles.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {attachedFiles.map(fileItem => (
                <div key={fileItem.id} className={`relative group flex items-center gap-2 px-3 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
                  {fileItem.preview ? (
                    <img src={fileItem.preview} alt={fileItem.name} className="w-10 h-10 object-cover rounded" />
                  ) : (
                    React.createElement(getFileIcon(fileItem.type), { size: 16, className: darkMode ? 'text-gray-400' : 'text-gray-600' })
                  )}
                  <span className={`text-xs ${darkMode ? 'text-gray-300' : 'text-gray-700'} max-w-[100px] truncate`}>
                    {fileItem.name}
                  </span>
                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className={`ml-1 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-200'}`}
                  >
                    <X size={14} className={darkMode ? 'text-gray-400' : 'text-gray-600'} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className={`flex items-end gap-2 px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
            />

            <button 
              onClick={() => fileInputRef.current?.click()}
              className={`p-2 ${darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-200'} rounded-lg transition-colors`}
            >
              <Paperclip size={20} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
            </button>

            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="메시지를 입력하세요..."
              className={`flex-1 resize-none outline-none bg-transparent ${darkMode ? 'text-white placeholder-gray-400' : 'text-gray-900 placeholder-gray-500'} ${getFontSizeClass()}`}
              rows={1}
              style={{ maxHeight: '200px' }}
            />

            <button
              onClick={handleSend}
              disabled={!inputValue.trim() && attachedFiles.length === 0}
              className={`p-2 rounded-lg transition-colors ${
                (inputValue.trim() || attachedFiles.length > 0)
                  ? darkMode ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'
                  : darkMode ? 'bg-gray-600 text-gray-400' : 'bg-gray-300 text-gray-400'
              }`}
            >
              <Send size={20} />
            </button>
          </div>

          <div className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} text-center mt-2`}>
            Dr. Chen이 도와드립니다. Shift+Enter로 줄바꿈, Enter로 전송 | 파일 드래그 앤 드롭 가능 (최대 10MB)
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatArea; 