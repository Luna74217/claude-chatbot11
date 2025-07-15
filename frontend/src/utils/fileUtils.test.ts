import {
  formatFileSize,
  getFileIcon,
  sanitizeFileName,
  getFileExtension
} from './fileUtils';

describe('fileUtils', () => {
  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
    });
  });

  describe('getFileIcon', () => {
    it('should return correct icon for image files', () => {
      expect(getFileIcon('image/jpeg')).toBe('🖼️');
      expect(getFileIcon('image/png')).toBe('🖼️');
    });

    it('should return correct icon for text files', () => {
      expect(getFileIcon('text/plain')).toBe('📄');
      expect(getFileIcon('text/csv')).toBe('📄');
    });

    it('should return default icon for unknown types', () => {
      expect(getFileIcon('application/unknown')).toBe('📎');
    });
  });

  describe('sanitizeFileName', () => {
    it('should remove dangerous characters', () => {
      expect(sanitizeFileName('file<script>alert("xss")</script>.txt')).toBe('file_script_alert("xss")_/script_.txt');
      expect(sanitizeFileName('file/with\\path:name*.txt')).toBe('file_with_path_name_.txt');
    });

    it('should preserve safe characters', () => {
      expect(sanitizeFileName('my-file_123.txt')).toBe('my-file_123.txt');
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extension correctly', () => {
      expect(getFileExtension('test.txt')).toBe('txt');
      expect(getFileExtension('image.jpg')).toBe('jpg');
      expect(getFileExtension('document.pdf')).toBe('pdf');
    });

    it('should handle files without extension', () => {
      expect(getFileExtension('test')).toBe('');
      expect(getFileExtension('')).toBe('');
    });
  });
}); 