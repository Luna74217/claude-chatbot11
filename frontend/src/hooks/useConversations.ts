import { useState, useEffect, useMemo } from 'react';
import { loadConversations, saveConversations } from '../utils/storageUtils';
import { filterConversations } from '../utils/searchUtils';
import { Conversation, Message } from '../types';

export const useConversations = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchMode, setSearchMode] = useState<'all' | 'title' | 'content'>('all');

  // 초기 대화 로드
  useEffect(() => {
    const savedConversations = loadConversations();
    if (savedConversations.length > 0) {
      setConversations(savedConversations);
      setActiveConversation(savedConversations[0].id);
    } else {
      // 기본 대화 생성
      const defaultConversation: Conversation = {
        id: '1',
        title: "새 대화",
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      setConversations([defaultConversation]);
      setActiveConversation('1');
    }
  }, []);

  // 대화 변경 시 저장
  useEffect(() => {
    if (conversations.length > 0) {
      saveConversations(conversations);
    }
  }, [conversations]);

  // 검색 결과 필터링
  const filteredConversations = useMemo(() => {
    return filterConversations(conversations, searchQuery, searchMode);
  }, [conversations, searchQuery, searchMode]);

  // 새 대화 시작
  const startNewChat = (): void => {
    const newId = Date.now().toString();
    const newConversation: Conversation = {
      id: newId,
      title: "새 대화",
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversation(newId);
    setSearchQuery('');
  };

  // 대화 전환
  const switchConversation = (convId: string): void => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setActiveConversation(convId);
      setSearchQuery('');
    }
  };

  // 대화 삭제
  const deleteConversation = (convId: string): void => {
    if (window.confirm('이 대화를 삭제하시겠습니까?')) {
      setConversations(prev => prev.filter(c => c.id !== convId));

      // 삭제한 대화가 현재 활성 대화인 경우
      if (convId === activeConversation) {
        const remainingConvs = conversations.filter(c => c.id !== convId);
        if (remainingConvs.length > 0) {
          switchConversation(remainingConvs[0].id);
        } else {
          startNewChat();
        }
      }
    }
  };

  // 모든 대화 삭제
  const deleteAllConversations = (): void => {
    if (window.confirm('모든 대화 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      setConversations([]);
      startNewChat();
    }
  };

  // 메시지 추가
  const addMessage = (conversationId: string, message: Message): void => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        const updatedMessages = [...conv.messages, message];
        return {
          ...conv,
          messages: updatedMessages,
          updatedAt: new Date().toISOString()
        };
      }
      return conv;
    }));
  };

  // 대화 제목 업데이트
  const updateConversationTitle = (conversationId: string, title: string): void => {
    setConversations(prev => prev.map(conv => 
      conv.id === conversationId ? { ...conv, title, updatedAt: new Date().toISOString() } : conv
    ));
  };

  return {
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
  };
}; 