import { Conversation } from '../types';

// 검색 관련 유틸리티 함수들

export const filterConversations = (
  conversations: Conversation[], 
  searchQuery: string, 
  searchMode: 'all' | 'title' | 'content'
): Conversation[] => {
  if (!searchQuery.trim()) {
    return conversations;
  }

  const query = searchQuery.toLowerCase();

  return conversations.filter(conv => {
    switch (searchMode) {
      case 'title':
        return conv.title.toLowerCase().includes(query);
      case 'content':
        return conv.messages && conv.messages.some(msg => 
          msg.content.toLowerCase().includes(query)
        );
      case 'all':
      default:
        return conv.title.toLowerCase().includes(query) ||
               (conv.messages && conv.messages.some(msg => 
                 msg.content.toLowerCase().includes(query)
               ));
    }
  });
};

export const highlightSearchQuery = (
  text: string, 
  searchQuery: string, 
  isSearching: boolean
): string => {
  if (!searchQuery || !isSearching) return text;

  const regex = new RegExp(`(${searchQuery})`, 'gi');
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
};

export const isSearchActive = (searchQuery: string): boolean => {
  return searchQuery.trim().length > 0;
}; 