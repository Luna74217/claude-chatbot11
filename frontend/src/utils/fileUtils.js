// 파일 관련 유틸리티 함수들

export const getFileIcon = (type) => {
  const iconMap = {
    'text/plain': 'FileText',
    'text/markdown': 'FileText',
    'application/json': 'Code',
    'application/javascript': 'Code',
    'text/javascript': 'Code',
    'text/css': 'Code',
    'text/html': 'Code',
    'image/': 'Image',
    'video/': 'FileVideo',
    'audio/': 'FileAudio',
    'application/pdf': 'File',
    'application/': 'File'
  };

  for (const [mimeType, icon] of Object.entries(iconMap)) {
    if (type.startsWith(mimeType)) {
      return icon;
    }
  }
  return 'File';
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const validateFile = (file) => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = [
    'text/plain',
    'text/markdown',
    'application/json',
    'application/javascript',
    'text/javascript',
    'text/css',
    'text/html',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf'
  ];

  if (file.size > maxSize) {
    throw new Error('파일 크기가 10MB를 초과합니다.');
  }

  if (!allowedTypes.some(type => file.type.startsWith(type))) {
    throw new Error('지원하지 않는 파일 형식입니다.');
  }

  return true;
}; 