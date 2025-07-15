// 메시지 타입 및 관련 상수들

export const MessageRole = {
  USER: 'user',
  ASSISTANT: 'assistant'
} as const;

export type MessageRoleType = typeof MessageRole[keyof typeof MessageRole];

export const MessageType = {
  CHAT: 'chat',
  FILE: 'file',
  SYSTEM: 'system'
} as const;

export type MessageTypeType = typeof MessageType[keyof typeof MessageType];

export const SearchMode = {
  ALL: 'all',
  TITLE: 'title',
  CONTENT: 'content'
} as const;

export type SearchModeType = typeof SearchMode[keyof typeof SearchMode];

export const FontSize = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large'
} as const;

export type FontSizeType = typeof FontSize[keyof typeof FontSize];

export const UIState = {
  TYPING: 'typing',
  IDLE: 'idle',
  ERROR: 'error',
  SUCCESS: 'success'
} as const;

export type UIStateType = typeof UIState[keyof typeof UIState]; 