import { Settings, Conversation } from '../types';

// 로컬 스토리지 관련 유틸리티 함수들

const STORAGE_KEYS = {
  CHAT_SETTINGS: 'chatSettings',
  CONVERSATIONS: 'conversations',
  MESSAGES: 'messages'
} as const;

export const loadSettings = (): Settings => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedSettings = localStorage.getItem(STORAGE_KEYS.CHAT_SETTINGS);
      if (savedSettings) {
        return JSON.parse(savedSettings);
      }
    }
  } catch (error) {
    console.log('localStorage not available or invalid data');
  }
  return {
    darkMode: false,
    fontSize: 'medium'
  };
};

export const saveSettings = (settings: Settings): void => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(STORAGE_KEYS.CHAT_SETTINGS, JSON.stringify(settings));
    }
  } catch (error) {
    console.log('localStorage not available');
  }
};

export const loadConversations = (): Conversation[] => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedConversations = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      if (savedConversations) {
        return JSON.parse(savedConversations);
      }
    }
  } catch (error) {
    console.log('localStorage not available or invalid data');
  }
  return [];
};

export const saveConversations = (conversations: Conversation[]): void => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    }
  } catch (error) {
    console.log('localStorage not available');
  }
};

export const clearStorage = (): void => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(STORAGE_KEYS.CHAT_SETTINGS);
      localStorage.removeItem(STORAGE_KEYS.CONVERSATIONS);
      localStorage.removeItem(STORAGE_KEYS.MESSAGES);
    }
  } catch (error) {
    console.log('localStorage not available');
  }
}; 