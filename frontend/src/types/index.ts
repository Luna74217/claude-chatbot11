import React from 'react';

// 컨텍스트 정보 타입
export interface ContextInfo {
  conversation_depth: number;
  current_topics: string[];
  emotional_state: {
    valence: number;
    arousal: number;
    trend: string;
  };
  compression_active: boolean;
}

// AI 페르소나 정보 타입
export interface PersonaInfo {
  location: string;
  growth_stage: string;
  episode_count: number;
  mask_level: number;
  security_protocol: string | null;
}

// 메시지 관련 타입
export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  files?: FileInfo[];
  isStreaming?: boolean;
  contextInfo?: ContextInfo | null;  // 🔥 컨텍스트 정보 추가
  personaInfo?: PersonaInfo | null;  // 🌿 페르소나 정보 추가
}

export interface FileInfo {
  id: number;
  name: string;
  type: string;
  size: number;
  sizeFormatted?: string;
  icon?: string;
  preview?: string;
  lastModified?: number;
}

// 대화 관련 타입
export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// 설정 관련 타입
export interface Settings {
  darkMode: boolean;
  fontSize: 'small' | 'medium' | 'large';
}

// WebSocket 관련 타입
export interface WebSocketMessage {
  type: 'chat' | 'file' | 'assistant' | 'file_response' | 'error' | 'stream_start' | 'stream_chunk' | 'stream_end';
  message?: string;
  content?: string;
  file?: FileInfo;
  timestamp: string;
  code?: number;
}

export interface WebSocketError {
  type: 'error';
  code: number;
  message: string;
  timestamp: string;
}

// 검색 관련 타입
export interface SearchState {
  query: string;
  mode: 'all' | 'title' | 'content';
  isActive: boolean;
}

// 파일 업로드 관련 타입
export interface FileUploadState {
  files: FileInfo[];
  isDragging: boolean;
  uploadProgress: number;
}

// UI 상태 타입
export interface UIState {
  sidebarOpen: boolean;
  artifactOpen: boolean;
  showSettings: boolean;
  copiedId: number | null;
  isTyping: boolean;
  isDragging: boolean;
}

// WebSocket 훅 반환 타입
export interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  error: string | null;
  sendMessage: (message: string) => boolean;
  sendFile: (fileInfo: FileInfo) => boolean;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  reconnectAttempts: number;
}

// 컴포넌트 Props 타입
export interface ChatInterfaceProps {
  apiUrl?: string;
}

export interface SidebarProps {
  sidebarOpen: boolean;
  darkMode: boolean;
  fontSize: Settings['fontSize'];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchMode: 'all' | 'title' | 'content';
  setSearchMode: (mode: 'all' | 'title' | 'content') => void;
  conversations: Conversation[];
  activeConversation: string;
  filteredConversations: Conversation[];
  isSearching: boolean;
  startNewChat: () => void;
  switchConversation: (id: string) => void;
  highlightText: (text: string, query: string, isDark: boolean) => string;
  getFontSizeClass: () => string;
}

export interface ChatAreaProps {
  darkMode: boolean;
  setDarkMode: (darkMode: boolean) => void;
  fontSize: Settings['fontSize'];
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  artifactOpen: boolean;
  setArtifactOpen: (open: boolean) => void;
  showSettings: boolean;
  setShowSettings: (show: boolean) => void;
  conversations: Conversation[];
  activeConversation: string;
  messages: Message[];
  isTyping: boolean;
  inputValue: string;
  setInputValue: (value: string) => void;
  attachedFiles: FileInfo[];
  isDragging: boolean;
  searchQuery: string;
  isSearching: boolean;
  copiedId: number | null;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  fileInputRef: React.RefObject<HTMLInputElement>;
  handleSend: () => void;
  handleFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleDragOver: (e: React.DragEvent) => void;
  handleDragLeave: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => void;
  removeFile: (fileId: number) => void;
  handleCopy: (text: string, messageId: number) => void;
  getFontSizeClass: () => string;
  onOpenTransformerSettings?: () => void;
  selectedTransformers?: any[];
}

export interface ArtifactPanelProps {
  artifactOpen: boolean;
  setArtifactOpen: (open: boolean) => void;
  darkMode: boolean;
  searchQuery: string;
  filteredConversations: Conversation[];
}

export interface SettingsModalProps {
  showSettings: boolean;
  setShowSettings: (show: boolean) => void;
  darkMode: boolean;
  setDarkMode: (darkMode: boolean) => void;
  fontSize: Settings['fontSize'];
  setFontSize: (fontSize: Settings['fontSize']) => void;
  activeConversation: string;
  conversations: Conversation[];
  deleteConversation: (id: string) => void;
  deleteAllConversations: () => void;
  resetSettings: () => void;
}

// 유틸리티 함수 타입
export type FileValidator = (file: File) => boolean;
export type FileIconGetter = (fileType: string) => string;
export type FileSizeFormatter = (bytes: number) => string;
export type TextHighlighter = (text: string, query: string, isDark: boolean) => string;
export type FontSizeClassGetter = () => string;

// 환경 변수 타입
export interface Environment {
  REACT_APP_API_URL: string;
  REACT_APP_DEV_MODE: string;
}

// API 응답 타입
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

// 에러 타입
export interface AppError {
  code: number;
  message: string;
  details?: string;
  timestamp: string;
} 