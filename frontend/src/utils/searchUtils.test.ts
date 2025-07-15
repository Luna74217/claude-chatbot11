import {
  filterConversations,
  highlightSearchQuery,
  isSearchActive
} from './searchUtils';
import { Conversation } from '@/types';

describe('searchUtils', () => {
  const mockConversations: Conversation[] = [
    {
      id: '1',
      title: 'React 개발 가이드',
      messages: [
        { id: 1, role: 'user', content: 'React 컴포넌트 만들기', timestamp: '2024-01-01T10:00:00Z' },
        { id: 2, role: 'assistant', content: 'React 컴포넌트는 함수형으로 작성할 수 있습니다', timestamp: '2024-01-01T10:01:00Z' }
      ],
      createdAt: '2024-01-01T10:00:00Z',
      updatedAt: '2024-01-01T10:01:00Z'
    },
    {
      id: '2',
      title: 'TypeScript 학습',
      messages: [
        { id: 3, role: 'user', content: 'TypeScript 타입 정의', timestamp: '2024-01-02T10:00:00Z' },
        { id: 4, role: 'assistant', content: 'TypeScript는 정적 타입 검사를 제공합니다', timestamp: '2024-01-02T10:01:00Z' }
      ],
      createdAt: '2024-01-02T10:00:00Z',
      updatedAt: '2024-01-02T10:01:00Z'
    },
    {
      id: '3',
      title: 'JavaScript 기초',
      messages: [
        { id: 5, role: 'user', content: 'JavaScript 변수 선언', timestamp: '2024-01-03T10:00:00Z' },
        { id: 6, role: 'assistant', content: 'JavaScript에서 let, const, var를 사용합니다', timestamp: '2024-01-03T10:01:00Z' }
      ],
      createdAt: '2024-01-03T10:00:00Z',
      updatedAt: '2024-01-03T10:01:00Z'
    }
  ];

  describe('filterConversations', () => {
    it('should return all conversations when search query is empty', () => {
      const result = filterConversations(mockConversations, '', 'all');
      expect(result).toEqual(mockConversations);
    });

    it('should return all conversations when search query is only whitespace', () => {
      const result = filterConversations(mockConversations, '   ', 'all');
      expect(result).toEqual(mockConversations);
    });

    it('should filter by title when search mode is title', () => {
      const result = filterConversations(mockConversations, 'React', 'title');
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('React 개발 가이드');
    });

    it('should filter by content when search mode is content', () => {
      const result = filterConversations(mockConversations, '컴포넌트', 'content');
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('React 개발 가이드');
    });

    it('should filter by both title and content when search mode is all', () => {
      const result = filterConversations(mockConversations, 'TypeScript', 'all');
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('TypeScript 학습');
    });

    it('should be case insensitive', () => {
      const result = filterConversations(mockConversations, 'react', 'title');
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('React 개발 가이드');
    });

    it('should return empty array when no matches found', () => {
      const result = filterConversations(mockConversations, 'Python', 'all');
      expect(result).toHaveLength(0);
    });

    it('should handle conversations without messages', () => {
      const conversationsWithoutMessages: Conversation[] = [
        {
          id: '1',
          title: 'Empty conversation',
          messages: [],
          createdAt: '2024-01-01T10:00:00Z',
          updatedAt: '2024-01-01T10:00:00Z'
        }
      ];

      const result = filterConversations(conversationsWithoutMessages, 'Empty', 'content');
      expect(result).toHaveLength(0);
    });
  });

  describe('highlightSearchQuery', () => {
    it('should return original text when search query is empty', () => {
      const text = 'Hello World';
      const result = highlightSearchQuery(text, '', false);
      expect(result).toBe(text);
    });

    it('should return original text when not searching', () => {
      const text = 'Hello World';
      const result = highlightSearchQuery(text, 'World', false);
      expect(result).toBe(text);
    });

    it('should highlight search query when searching', () => {
      const text = 'Hello World';
      const result = highlightSearchQuery(text, 'World', true);
      expect(result).toBe('Hello <mark class="search-highlight">World</mark>');
    });

    it('should highlight multiple occurrences', () => {
      const text = 'Hello World, Hello Universe';
      const result = highlightSearchQuery(text, 'Hello', true);
      expect(result).toBe('<mark class="search-highlight">Hello</mark> World, <mark class="search-highlight">Hello</mark> Universe');
    });

    it('should be case insensitive', () => {
      const text = 'Hello World';
      const result = highlightSearchQuery(text, 'world', true);
      expect(result).toBe('Hello <mark class="search-highlight">World</mark>');
    });

    it('should handle special regex characters', () => {
      const text = 'Hello (World)';
      const result = highlightSearchQuery(text, '(World)', true);
      expect(result).toBe('Hello (<mark class="search-highlight">World</mark>)');
    });

    it('should handle empty text', () => {
      const result = highlightSearchQuery('', 'test', true);
      expect(result).toBe('');
    });
  });

  describe('isSearchActive', () => {
    it('should return false for empty string', () => {
      expect(isSearchActive('')).toBe(false);
    });

    it('should return false for whitespace only', () => {
      expect(isSearchActive('   ')).toBe(false);
    });

    it('should return true for non-empty string', () => {
      expect(isSearchActive('test')).toBe(true);
    });

    it('should return true for string with content and whitespace', () => {
      expect(isSearchActive('  test  ')).toBe(true);
    });

    it('should return true for single character', () => {
      expect(isSearchActive('a')).toBe(true);
    });
  });
}); 