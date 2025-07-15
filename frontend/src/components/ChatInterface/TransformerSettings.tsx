import React, { useState, useEffect } from 'react';
import { Settings, Zap, X, Check } from 'lucide-react';

interface TransformerConfig {
  type: string;
  name: string;
  description: string;
  config: Record<string, any>;
}

interface TransformerSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (configs: TransformerConfig[]) => void;
  darkMode: boolean;
}

const TransformerSettings: React.FC<TransformerSettingsProps> = ({
  isOpen,
  onClose,
  onApply,
  darkMode
}) => {
  const [availableTransformers, setAvailableTransformers] = useState<TransformerConfig[]>([]);
  const [selectedTransformers, setSelectedTransformers] = useState<TransformerConfig[]>([]);
  const [loading, setLoading] = useState(false);

  // 사용 가능한 변환기 목록 가져오기
  useEffect(() => {
    if (isOpen) {
      fetchAvailableTransformers();
    }
  }, [isOpen]);

  const fetchAvailableTransformers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/transformers');
      const data = await response.json();
      setAvailableTransformers(data.transformers || []);
    } catch (error) {
      console.error('변환기 목록 가져오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTransformer = (transformer: TransformerConfig) => {
    setSelectedTransformers(prev => {
      const isSelected = prev.some(t => t.type === transformer.type);
      if (isSelected) {
        return prev.filter(t => t.type !== transformer.type);
      } else {
        return [...prev, transformer];
      }
    });
  };

  const isSelected = (type: string) => {
    return selectedTransformers.some(t => t.type === type);
  };

  const handleApply = () => {
    onApply(selectedTransformers);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${darkMode ? 'bg-black/50' : 'bg-black/30'}`}>
      <div className={`relative w-full max-w-2xl mx-4 p-6 rounded-lg shadow-xl ${
        darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
      }`}>
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-blue-500" />
            <h2 className="text-xl font-semibold">스트림 변환기 설정</h2>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg hover:bg-opacity-80 ${
              darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
            }`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 설명 */}
        <p className={`mb-6 text-sm ${
          darkMode ? 'text-gray-300' : 'text-gray-600'
        }`}>
          AI 응답을 실시간으로 변환하는 도구들을 선택하세요. 여러 변환기를 조합하여 사용할 수 있습니다.
        </p>

        {/* 변환기 목록 */}
        <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-2 text-sm">변환기 목록을 불러오는 중...</p>
            </div>
          ) : (
            availableTransformers.map((transformer) => (
              <div
                key={transformer.type}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected(transformer.type)
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : darkMode
                    ? 'border-gray-600 hover:border-gray-500'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleTransformer(transformer)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium">{transformer.name}</h3>
                      {isSelected(transformer.type) && (
                        <Check className="w-4 h-4 text-blue-500" />
                      )}
                    </div>
                    <p className={`text-sm ${
                      darkMode ? 'text-gray-300' : 'text-gray-600'
                    }`}>
                      {transformer.description}
                    </p>
                    <div className="mt-2 text-xs text-gray-500">
                      설정: {JSON.stringify(transformer.config)}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* 선택된 변환기 */}
        {selectedTransformers.length > 0 && (
          <div className="mb-6">
            <h3 className="font-medium mb-2">선택된 변환기 ({selectedTransformers.length})</h3>
            <div className="flex flex-wrap gap-2">
              {selectedTransformers.map((transformer) => (
                <span
                  key={transformer.type}
                  className={`px-3 py-1 rounded-full text-sm ${
                    darkMode
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {transformer.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 버튼 */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${
              darkMode
                ? 'bg-gray-700 hover:bg-gray-600'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            취소
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center space-x-2"
          >
            <Zap className="w-4 h-4" />
            <span>적용</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransformerSettings; 