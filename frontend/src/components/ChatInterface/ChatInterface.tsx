import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useSettings } from '../../hooks/useSettings';
import { useConversations } from '../../hooks/useConversations';
import { useWebSocket } from '../../hooks/useWebSocket';
import { createFileInfo, validateDroppedFiles, cleanupFileList } from '../../utils/fileUtils_improved';
import { isSearchActive } from '../../utils/searchUtils';
import { 
  ChatInterfaceProps, 
  Message, 
  FileInfo, 
  UIState 
} from '../../types';
import Sidebar from '../Sidebar/Sidebar';
import ChatArea from '../ChatArea/ChatArea';
import ArtifactPanel from '../ArtifactPanel/ArtifactPanel';
import SettingsModal from '../Settings/SettingsModal';
import TransformerSettings from './TransformerSettings';
import PersonaMonitor from '../PersonaMonitor/PersonaMonitor';

// Replit 환경에서 백엔드 URL (환경변수로 관리)
const API_URL = process.env.REACT_APP_API_URL || "https://your-backend-repl-url.repl.co";

const ChatInterface: React.FC<ChatInterfaceProps> = ({ apiUrl = API_URL }) => {
  // 커스텀 훅 사용
  const { darkMode, fontSize, toggleDarkMode, updateFontSize, resetSettings } = useSettings();
  const {
    conversations,
    activeConversation,
    filteredConversations,
    searchQuery,
    setSearchQuery,
    searchMode,
    setSearchMode,
    startNewChat,
    switchConversation,
    deleteConversation,
    deleteAllConversations,
    addMessage,
    updateConversationTitle
  } = useConversations();

  // WebSocket 연결
  const { isConnected, lastMessage, error, sendMessage, sendFile } = useWebSocket(apiUrl);

  // 로컬 상태
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [attachedFiles, setAttachedFiles] = useState<FileInfo[]>([]);
  const [selectedTransformers, setSelectedTransformers] = useState<any[]>([]);
  const [showTransformerSettings, setShowTransformerSettings] = useState(false);
  const [uiState, setUIState] = useState<UIState>({
    sidebarOpen: true,
    artifactOpen: true,
    showSettings: false,
    copiedId: null,
    isTyping: false,
    isDragging: false
  });
  
  // refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 검색 상태 관리
  const isSearching = isSearchActive(searchQuery);

  // 대화 변경 시 메시지 업데이트
  useEffect(() => {
    const currentConv = conversations.find(c => c.id === activeConversation);
    if (currentConv) {
      setMessages(currentConv.messages);
    } else {
      setMessages([]);
    }
  }, [activeConversation, conversations]);

  // WebSocket 메시지 처리
  useEffect(() => {
    if (lastMessage) {
      try {
        const messageData = typeof lastMessage === 'string' ? JSON.parse(lastMessage) : lastMessage;
        
        if (messageData.type === 'assistant') {
          const aiResponse: Message = {
            id: Date.now(),
            role: 'assistant',
            content: messageData.content || '',
            timestamp: messageData.timestamp,
            contextInfo: messageData.context_info || null,  // 🔥 컨텍스트 정보 추가
            personaInfo: messageData.persona_info || null   // 🌿 페르소나 정보 추가
          };
          
          if (activeConversation) {
            addMessage(activeConversation, aiResponse);
          }
          setMessages(prev => [...prev, aiResponse]);
          setUIState(prev => ({ ...prev, isTyping: false }));
        } else if (messageData.type === 'stream_start') {
          // 스트리밍 시작
          const streamResponse: Message = {
            id: Date.now(),
            role: 'assistant',
            content: '',
            timestamp: messageData.timestamp,
            isStreaming: true
          };
          
          addMessage(activeConversation, streamResponse);
          setMessages(prev => [...prev, streamResponse]);
        } else if (messageData.type === 'stream_chunk') {
          // 스트리밍 청크
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.isStreaming) {
              lastMessage.content += messageData.content || '';
            }
            return newMessages;
          });
        } else if (messageData.type === 'stream_end') {
          // 스트리밍 종료
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.isStreaming) {
              lastMessage.isStreaming = false;
            }
            return newMessages;
          });
          setUIState(prev => ({ ...prev, isTyping: false }));
        } else if (messageData.type === 'file_response') {
          const fileResponse: Message = {
            id: Date.now(),
            role: 'assistant',
            content: messageData.content || '',
            timestamp: messageData.timestamp
          };
          
          addMessage(activeConversation, fileResponse);
          setMessages(prev => [...prev, fileResponse]);
        }
      } catch (error) {
        console.error('메시지 처리 오류:', error);
      }
    }
  }, [lastMessage, addMessage, activeConversation]);

  // 메시지 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 컴포넌트 언마운트 시 파일 정리
  useEffect(() => {
    return () => {
      cleanupFileList(attachedFiles);
    };
  }, [attachedFiles]);

  // 폰트 크기 클래스
  const getFontSizeClass = useCallback((): string => {
    switch(fontSize) {
      case 'small': return 'text-xs';
      case 'large': return 'text-base';
      default: return 'text-sm';
    }
  }, [fontSize]);

  // 텍스트 하이라이팅
  const highlightText = useCallback((text: string, query: string, isDark: boolean): string => {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, `<mark class="${isDark ? 'bg-yellow-600/30 text-yellow-300' : 'bg-yellow-200 text-yellow-800'}">$1</mark>`);
  }, []);

  // 파일 처리
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>): void => {
    const files = Array.from(e.target.files || []);
    files.forEach(file => {
      try {
        const fileInfo = createFileInfo(file);
        setAttachedFiles(prev => [...prev, fileInfo]);
      } catch (error) {
        alert((error as Error).message);
      }
    });
    e.target.value = '';
  }, []);

  const removeFile = useCallback((fileId: number): void => {
    setAttachedFiles(prev => {
      const fileItem = prev.find(f => f.id === fileId);
      if (fileItem?.preview) {
        URL.revokeObjectURL(fileItem.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  }, []);

  // 드래그 앤 드롭
  const handleDragOver = useCallback((e: React.DragEvent): void => {
    e.preventDefault();
    setUIState(prev => ({ ...prev, isDragging: true }));
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent): void => {
    e.preventDefault();
    setUIState(prev => ({ ...prev, isDragging: false }));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent): void => {
    e.preventDefault();
    setUIState(prev => ({ ...prev, isDragging: false }));
    
    try {
      const validFiles = validateDroppedFiles(e.dataTransfer.files);
      validFiles.forEach(file => {
        const fileInfo = createFileInfo(file);
        setAttachedFiles(prev => [...prev, fileInfo]);
      });
    } catch (error) {
      alert((error as Error).message);
    }
  }, []);

  // 변환기 설정 적용
  const handleApplyTransformers = useCallback((configs: any[]): void => {
    setSelectedTransformers(configs);
  }, []);

  // 메시지 전송
  const handleSend = useCallback((): void => {
    if (!inputValue.trim() && attachedFiles.length === 0) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
      files: attachedFiles
    };

    // 사용자 메시지 추가
    addMessage(activeConversation, userMessage);
    setMessages(prev => [...prev, userMessage]);
    
    // 변환기가 선택된 경우 스트리밍 모드로 전송
    const messageData = {
      type: 'chat',
      message: inputValue.trim(),
      streaming: selectedTransformers.length > 0,
      transformers: selectedTransformers.length > 0 ? selectedTransformers : undefined,
      timestamp: new Date().toISOString()
    };
    
    // WebSocket으로 메시지 전송
    if (sendMessage(JSON.stringify(messageData))) {
      setUIState(prev => ({ ...prev, isTyping: true }));
    } else {
      alert('서버에 연결할 수 없습니다. 연결 상태를 확인해주세요.');
    }

    // 첨부 파일이 있다면 파일 정보도 전송
    attachedFiles.forEach(fileItem => {
      sendFile(fileItem);
    });

    setInputValue('');
    setAttachedFiles([]);
  }, [inputValue, attachedFiles, addMessage, activeConversation, sendMessage, sendFile, selectedTransformers]);

  // 메시지 복사
  const handleCopy = useCallback(async (text: string, messageId: number): Promise<void> => {
    try {
      await navigator.clipboard.writeText(text);
      setUIState(prev => ({ ...prev, copiedId: messageId }));
      setTimeout(() => setUIState(prev => ({ ...prev, copiedId: null })), 2000);
    } catch (error) {
      console.error('복사 실패:', error);
    }
  }, []);

  // UI 상태 업데이트 함수들
  const setSidebarOpen = useCallback((open: boolean): void => {
    setUIState(prev => ({ ...prev, sidebarOpen: open }));
  }, []);

  const setArtifactOpen = useCallback((open: boolean): void => {
    setUIState(prev => ({ ...prev, artifactOpen: open }));
  }, []);

  const setShowSettings = useCallback((show: boolean): void => {
    setUIState(prev => ({ ...prev, showSettings: show }));
  }, []);

  // 마크다운 스타일
  const markdownStyles = `
    .markdown-content {
      word-break: break-word;
    }
    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
      margin-top: 1rem;
      margin-bottom: 0.5rem;
      font-weight: 600;
    }
    .markdown-content h1 { font-size: 1.5rem; }
    .markdown-content h2 { font-size: 1.25rem; }
    .markdown-content h3 { font-size: 1.125rem; }
    .markdown-content p { margin-bottom: 0.5rem; }
    .markdown-content ul, .markdown-content ol {
      margin-left: 1.5rem;
      margin-bottom: 0.5rem;
    }
    .markdown-content li { margin-bottom: 0.25rem; }
    .markdown-content blockquote {
      border-left: 4px solid #e5e7eb;
      padding-left: 1rem;
      margin: 1rem 0;
      font-style: italic;
    }
    .markdown-content pre {
      background-color: #f3f4f6;
      padding: 1rem;
      border-radius: 0.5rem;
      overflow-x: auto;
      margin: 1rem 0;
    }
    .markdown-content code {
      background-color: #f3f4f6;
      padding: 0.125rem 0.25rem;
      border-radius: 0.25rem;
      font-family: 'Courier New', monospace;
    }
    .markdown-content pre code {
      background-color: transparent;
      padding: 0;
    }
    .markdown-content a {
      color: #3b82f6;
      text-decoration: underline;
    }
    .markdown-content a:hover {
      color: #2563eb;
    }
    .search-highlight {
      background-color: #fef3c7;
      padding: 0.125rem 0.25rem;
      border-radius: 0.25rem;
    }
    .dark .search-highlight {
      background-color: #92400e;
      color: #fef3c7;
    }
  `;

  return (
    <>
      {/* 연결 상태 표시 */}
      {!isConnected && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-2 rounded-lg ${
          error ? 'bg-red-500 text-white' : 'bg-yellow-500 text-black'
        }`}>
          {error ? `연결 오류: ${error}` : '서버에 연결 중...'}
        </div>
      )}

      <SettingsModal 
        showSettings={uiState.showSettings}
        setShowSettings={setShowSettings}
        darkMode={darkMode}
        setDarkMode={toggleDarkMode}
        fontSize={fontSize}
        setFontSize={updateFontSize}
        activeConversation={activeConversation}
        conversations={conversations}
        deleteConversation={deleteConversation}
        deleteAllConversations={deleteAllConversations}
        resetSettings={resetSettings}
      />
      
      <TransformerSettings
        isOpen={showTransformerSettings}
        onClose={() => setShowTransformerSettings(false)}
        onApply={handleApplyTransformers}
        darkMode={darkMode}
      />
      
      <div className={`flex h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
        <style dangerouslySetInnerHTML={{ __html: markdownStyles }} />

        <Sidebar
          sidebarOpen={uiState.sidebarOpen}
          darkMode={darkMode}
          fontSize={fontSize}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          searchMode={searchMode}
          setSearchMode={setSearchMode}
          conversations={conversations}
          activeConversation={activeConversation}
          filteredConversations={filteredConversations}
          isSearching={isSearching}
          startNewChat={startNewChat}
          switchConversation={switchConversation}
          highlightText={highlightText}
          getFontSizeClass={getFontSizeClass}
        />

        <ChatArea
          darkMode={darkMode}
          setDarkMode={toggleDarkMode}
          fontSize={fontSize}
          sidebarOpen={uiState.sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          artifactOpen={uiState.artifactOpen}
          setArtifactOpen={setArtifactOpen}
          showSettings={uiState.showSettings}
          setShowSettings={setShowSettings}
          conversations={conversations}
          activeConversation={activeConversation}
          messages={messages}
          isTyping={uiState.isTyping}
          inputValue={inputValue}
          setInputValue={setInputValue}
          attachedFiles={attachedFiles}
          isDragging={uiState.isDragging || false}
          searchQuery={searchQuery}
          isSearching={isSearching}
          copiedId={uiState.copiedId}
          messagesEndRef={messagesEndRef}
          textareaRef={textareaRef}
          fileInputRef={fileInputRef}
          handleSend={handleSend}
          handleFileSelect={handleFileSelect}
          handleDragOver={handleDragOver}
          handleDragLeave={handleDragLeave}
          handleDrop={handleDrop}
          removeFile={removeFile}
          handleCopy={handleCopy}
          getFontSizeClass={getFontSizeClass}
          onOpenTransformerSettings={() => setShowTransformerSettings(true)}
          selectedTransformers={selectedTransformers}
        />

        <ArtifactPanel
          artifactOpen={uiState.artifactOpen}
          setArtifactOpen={setArtifactOpen}
          darkMode={darkMode}
          searchQuery={searchQuery}
          filteredConversations={filteredConversations}
        />
      </div>
      
      {/* 🌿 AI 페르소나 모니터 */}
      <PersonaMonitor />
    </>
  );
};

export default ChatInterface; 