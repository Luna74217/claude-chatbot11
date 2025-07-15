import {
  loadSettings,
  saveSettings,
  loadConversations,
  saveConversations
} from './storageUtils';
import { Settings, Conversation } from '@/types';

// setupTests.ts에서 이미 설정된 localStorage mock 사용
// 추가 mock 설정 불필요

describe('storageUtils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (localStorage.getItem as jest.Mock).mockReturnValue(null);
    (localStorage.setItem as jest.Mock).mockImplementation(() => {});
  });

  describe('loadSettings', () => {
    it('should return default settings when localStorage is empty', () => {
      const result = loadSettings();
      expect(result).toEqual({
        darkMode: false,
        fontSize: 'medium'
      });
    });

    it('should return saved settings from localStorage', () => {
      const savedSettings: Settings = {
        darkMode: true,
        fontSize: 'large'
      };

      (localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(savedSettings));

      const result = loadSettings();
      expect(result).toEqual(savedSettings);
    });
  });

  describe('saveSettings', () => {
    it('should save settings to localStorage', () => {
      const settings: Settings = {
        darkMode: true,
        fontSize: 'large'
      };

      saveSettings(settings);

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'chatSettings',
        JSON.stringify(settings)
      );
    });
  });

  describe('loadConversations', () => {
    it('should return empty array when localStorage is empty', () => {
      const result = loadConversations();
      expect(result).toEqual([]);
    });

    it('should return saved conversations from localStorage', () => {
      const savedConversations: Conversation[] = [
        {
          id: '1',
          title: 'Test Conversation',
          messages: [
            { id: 1, role: 'user', content: 'Hello', timestamp: '2024-01-01T10:00:00Z' }
          ],
          createdAt: '2024-01-01T10:00:00Z',
          updatedAt: '2024-01-01T10:00:00Z'
        }
      ];

      (localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(savedConversations));

      const result = loadConversations();
      expect(result).toEqual(savedConversations);
    });
  });

  describe('saveConversations', () => {
    it('should save conversations to localStorage', () => {
      const conversations: Conversation[] = [
        {
          id: '1',
          title: 'Test Conversation',
          messages: [
            { id: 1, role: 'user', content: 'Hello', timestamp: '2024-01-01T10:00:00Z' }
          ],
          createdAt: '2024-01-01T10:00:00Z',
          updatedAt: '2024-01-01T10:00:00Z'
        }
      ];

      saveConversations(conversations);

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'conversations',
        JSON.stringify(conversations)
      );
    });
  });
}); 