import React, { useState, useRef, useEffect } from 'react';
import { useSettings } from '../../hooks/useSettings';
import { useConversations } from '../../hooks/useConversations';
import { getFileIcon, validateFile } from '../../utils/fileUtils';
import { isSearchActive } from '../../utils/searchUtils';
import { MessageRole } from '../../constants/messageTypes';
import Sidebar from '../Sidebar/Sidebar';
import ChatArea from '../ChatArea/ChatArea';
import ArtifactPanel from '../ArtifactPanel/ArtifactPanel';
import SettingsModal from '../Settings/SettingsModal';

// 샘플 대화 데이터
const sampleConversations = [
  { 
    id: 1, 
    title: "React 컴포넌트 최적화", 
    lastMessage: "useMemo와 useCallback의 차이점은...", 
    time: "2분 전",
    messages: [
      { id: 1, role: MessageRole.USER, content: "React 앱이 느려요. **useMemo**와 **useCallback** 언제 써야 하나요?" },
      { id: 2, role: MessageRole.ASSISTANT, content: "React 성능 최적화를 위한 Hook 사용법을 설명드리겠습니다.\n\n## useMemo vs useCallback\n\n### useMemo\n- 계산 비용이 높은 값을 메모이제이션\n- 의존성 배열의 값이 변경될 때만 재계산\n\n```javascript\nconst expensiveValue = useMemo(() => {\n  return computeExpensiveValue(a, b);\n}, [a, b]);\n```\n\n### useCallback\n- 함수를 메모이제이션\n- 자식 컴포넌트에 콜백을 전달할 때 유용" }
    ]
  },
  { 
    id: 2, 
    title: "Python 데이터 분석", 
    lastMessage: "Pandas DataFrame 병합 방법", 
    time: "1시간 전",
    messages: [
      { id: 1, role: MessageRole.USER, content: "**Pandas**로 CSV 파일 읽고 데이터 병합하는 방법 알려주세요" },
      { id: 2, role: MessageRole.ASSISTANT, content: "Pandas를 사용한 데이터 병합 방법입니다:\n\n```python\nimport pandas as pd\n\n# CSV 파일 읽기\ndf1 = pd.read_csv('file1.csv')\ndf2 = pd.read_csv('file2.csv')\n\n# 병합하기\nmerged = pd.merge(df1, df2, on='key_column')\n```" }
    ]
  },
  { 
    id: 3, 
    title: "API 설계 패턴", 
    lastMessage: "RESTful vs GraphQL 비교", 
    time: "어제",
    messages: [
      { id: 1, role: MessageRole.USER, content: "**RESTful API**와 **GraphQL** 중 뭐가 더 좋아요?" },
      { id: 2, role: MessageRole.ASSISTANT, content: "각각의 장단점을 비교해드리겠습니다:\n\n## REST\n- 간단하고 직관적\n- HTTP 메서드 활용\n- 캐싱 용이\n\n## GraphQL\n- 필요한 데이터만 요청\n- 단일 엔드포인트\n- 실시간 구독 지원" }
    ]
  },
];

const ChatInterface = () => {
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

  // 로컬 상태
  const [messages, setMessages] = useState(sampleConversations[0]?.messages || []);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [artifactOpen, setArtifactOpen] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  
  // refs
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // 검색 상태 관리
  const isSearching = isSearchActive(searchQuery);

  // 대화 변경 시 메시지 업데이트
  useEffect(() => {
    const currentConv = conversations.find(c => c.id === activeConversation);
    if (currentConv) {
      setMessages(currentConv.messages || []);
    }
  }, [activeConversation, conversations]);

  // 메시지 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 폰트 크기 클래스
  const getFontSizeClass = () => {
    switch(fontSize) {
      case 'small': return 'text-xs';
      case 'large': return 'text-base';
      default: return 'text-sm';
    }
  };

  // 텍스트 하이라이팅
  const highlightText = (text, query, isDark) => {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, `<mark class="${isDark ? 'bg-yellow-600/30 text-yellow-300' : 'bg-yellow-200 text-yellow-800'}">$1</mark>`);
  };

  // 파일 처리
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      try {
        validateFile(file);
        const fileId = Date.now() + Math.random();
        const fileItem = {
          id: fileId,
          file,
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
        };
        setAttachedFiles(prev => [...prev, fileItem]);
      } catch (error) {
        alert(error.message);
      }
    });
    e.target.value = '';
  };

  const removeFile = (fileId) => {
    setAttachedFiles(prev => {
      const fileItem = prev.find(f => f.id === fileId);
      if (fileItem?.preview) {
        URL.revokeObjectURL(fileItem.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  // 드래그 앤 드롭
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
      try {
        validateFile(file);
        const fileId = Date.now() + Math.random();
        const fileItem = {
          id: fileId,
          file,
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
        };
        setAttachedFiles(prev => [...prev, fileItem]);
      } catch (error) {
        alert(error.message);
      }
    });
  };

  // 메시지 전송
  const handleSend = () => {
    if (!inputValue.trim() && attachedFiles.length === 0) return;

    const userMessage = {
      id: Date.now(),
      role: MessageRole.USER,
      content: inputValue.trim(),
      files: attachedFiles.map(f => ({
        name: f.file.name,
        type: f.file.type,
        size: f.file.size,
        preview: f.preview
      }))
    };

    // 사용자 메시지 추가
    addMessage(activeConversation, userMessage);
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setAttachedFiles([]);

    // AI 응답 시뮬레이션
    setIsTyping(true);
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        role: MessageRole.ASSISTANT,
        content: `사용자 메시지에 대한 AI 응답입니다: "${userMessage.content}"\n\n이것은 시뮬레이션된 응답입니다.`
      };
      
      addMessage(activeConversation, aiResponse);
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  // 메시지 복사
  const handleCopy = async (text, messageId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('복사 실패:', error);
    }
  };

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
      <SettingsModal 
        showSettings={showSettings}
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
      
      <div className={`flex h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
        <style dangerouslySetInnerHTML={{ __html: markdownStyles }} />

        <Sidebar
          sidebarOpen={sidebarOpen}
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
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          artifactOpen={artifactOpen}
          setArtifactOpen={setArtifactOpen}
          showSettings={showSettings}
          setShowSettings={setShowSettings}
          conversations={conversations}
          activeConversation={activeConversation}
          messages={messages}
          isTyping={isTyping}
          inputValue={inputValue}
          setInputValue={setInputValue}
          attachedFiles={attachedFiles}
          isDragging={isDragging}
          searchQuery={searchQuery}
          isSearching={isSearching}
          copiedId={copiedId}
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
        />

        <ArtifactPanel
          artifactOpen={artifactOpen}
          setArtifactOpen={setArtifactOpen}
          darkMode={darkMode}
          searchQuery={searchQuery}
          filteredConversations={filteredConversations}
        />
      </div>
    </>
  );
};

export default ChatInterface; 