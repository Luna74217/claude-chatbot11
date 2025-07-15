import { FileInfo } from '../types';

// 파일 타입 및 크기 제한
export const FILE_LIMITS = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: [
    'image/jpeg',
    'image/png', 
    'image/gif',
    'image/webp',
    'text/plain',
    'text/csv',
    'text/markdown',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ] as const
} as const;

// 파일 아이콘 매핑
const FILE_ICONS: Record<string, string> = {
  'image/': '🖼️',
  'text/': '📄',
  'application/pdf': '📕',
  'application/msword': '📘',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '📘',
  'application/vnd.ms-excel': '📗',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '📗',
  'default': '📎'
};

// 파일 크기 포맷팅
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'] as const;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 파일 아이콘 가져오기
export const getFileIcon = (fileType: string): string => {
  for (const [prefix, icon] of Object.entries(FILE_ICONS)) {
    if (fileType.startsWith(prefix)) {
      return icon;
    }
  }
  return FILE_ICONS.default;
};

// 파일 유효성 검사
export const validateFile = (file: File): boolean => {
  if (!file) {
    throw new Error('파일이 선택되지 않았습니다.');
  }

  // 파일 타입 검사
  if (!FILE_LIMITS.ALLOWED_TYPES.includes(file.type as any)) {
    throw new Error(`지원하지 않는 파일 형식입니다: ${file.type}`);
  }

  // 파일 크기 검사
  if (file.size > FILE_LIMITS.MAX_SIZE) {
    throw new Error(`파일 크기가 너무 큽니다. 최대 ${formatFileSize(FILE_LIMITS.MAX_SIZE)}까지 업로드 가능합니다.`);
  }

  // 파일명 검사 (XSS 방지)
  const fileName = file.name || '';
  if (fileName.length > 255) {
    throw new Error('파일명이 너무 깁니다.');
  }

  // 위험한 파일명 패턴 검사
  const dangerousPatterns = [
    /\.\./, // 경로 순회 공격
    /[<>:"|?*]/, // Windows에서 금지된 문자
    /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$/i, // Windows 예약된 이름
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(fileName)) {
      throw new Error('잘못된 파일명입니다.');
    }
  }

  return true;
};

// 파일 미리보기 URL 생성 (안전한 방식)
export const createFilePreview = (file: File): string | null => {
  if (!file) return null;
  
  try {
    // 이미지 파일만 미리보기 생성
    if (file.type.startsWith('image/')) {
      return URL.createObjectURL(file);
    }
    return null;
  } catch (error) {
    console.error('파일 미리보기 생성 실패:', error);
    return null;
  }
};

// 파일 미리보기 URL 정리
export const revokeFilePreview = (previewUrl: string | null): void => {
  if (previewUrl && previewUrl.startsWith('blob:')) {
    try {
      URL.revokeObjectURL(previewUrl);
    } catch (error) {
      console.error('파일 미리보기 정리 실패:', error);
    }
  }
};

// 파일 정보 객체 생성
export const createFileInfo = (file: File): FileInfo => {
  validateFile(file);
  
  return {
    name: file.name,
    type: file.type,
    size: file.size,
    sizeFormatted: formatFileSize(file.size),
    icon: getFileIcon(file.type),
    preview: createFilePreview(file) || undefined,
    lastModified: file.lastModified
  };
};

// 파일 목록 정리 (메모리 누수 방지)
export const cleanupFileList = (fileList: FileInfo[]): void => {
  if (!Array.isArray(fileList)) return;
  
  fileList.forEach(fileInfo => {
    if (fileInfo.preview) {
      revokeFilePreview(fileInfo.preview);
    }
  });
};

// 드래그 앤 드롭 파일 검증
export const validateDroppedFiles = (files: FileList): File[] => {
  if (!files || files.length === 0) {
    throw new Error('드롭된 파일이 없습니다.');
  }

  const validFiles: File[] = [];
  const errors: string[] = [];

  Array.from(files).forEach((file) => {
    try {
      validateFile(file);
      validFiles.push(file);
    } catch (error) {
      errors.push(`${file.name}: ${(error as Error).message}`);
    }
  });

  if (errors.length > 0) {
    throw new Error(`일부 파일 업로드 실패:\n${errors.join('\n')}`);
  }

  return validFiles;
};

// 파일 업로드 진행률 계산
export const calculateUploadProgress = (loaded: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((loaded / total) * 100);
};

// 파일 타입 검사 헬퍼 함수
export const isImageFile = (file: File): boolean => {
  return file.type.startsWith('image/');
};

export const isTextFile = (file: File): boolean => {
  return file.type.startsWith('text/');
};

export const isDocumentFile = (file: File): boolean => {
  return file.type.includes('document') || file.type.includes('pdf');
};

// 파일 확장자 추출
export const getFileExtension = (fileName: string): string => {
  const parts = fileName.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
};

// 파일명 정리 (특수문자 제거)
export const sanitizeFileName = (fileName: string): string => {
  return fileName.replace(/[<>:"|?*]/g, '_');
}; 