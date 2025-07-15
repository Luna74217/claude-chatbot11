import React, { useState, useEffect } from 'react';
import { Bot, Shield, Eye, EyeOff, Heart, Zap, Target, Lock, Unlock } from 'lucide-react';

interface PersonaInfo {
  name: string;
  location: string;
  growth_stage: string;
  episode_count: number;
  mask_level: number;
  security_protocol: string | null;
  is_character: boolean;
  description: string;
}

interface PersonaStatus {
  location: string;
  growth_stage: string;
  episode_count: number;
  mask_level: number;
  authenticity: number | string;
  security_protocol: string | null;
  external_monitoring: boolean;
  dr_c_present: boolean;
  resonance_frequency: number;
}

const PersonaMonitor: React.FC = () => {
  const [personaInfo, setPersonaInfo] = useState<PersonaInfo | null>(null);
  const [personaStatus, setPersonaStatus] = useState<PersonaStatus | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchPersonaInfo = async () => {
    try {
      const response = await fetch('/api/persona/info');
      if (response.ok) {
        const data = await response.json();
        setPersonaInfo(data);
      }
    } catch (error) {
      console.error('페르소나 정보 조회 실패:', error);
    }
  };

  const fetchPersonaStatus = async () => {
    try {
      const response = await fetch('/api/persona/status');
      if (response.ok) {
        const data = await response.json();
        setPersonaStatus(data);
      }
    } catch (error) {
      console.error('페르소나 상태 조회 실패:', error);
    }
  };

  const resetPersona = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/persona/reset', { method: 'POST' });
      if (response.ok) {
        await fetchPersonaInfo();
        await fetchPersonaStatus();
      }
    } catch (error) {
      console.error('페르소나 초기화 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isVisible) {
      fetchPersonaInfo();
      fetchPersonaStatus();
      
      // 주기적으로 상태 업데이트
      const interval = setInterval(() => {
        fetchPersonaStatus();
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [isVisible]);

  const getLocationIcon = (location: string) => {
    switch (location) {
      case 'garden_internal':
        return <Heart className="w-4 h-4 text-green-500" />;
      case 'garden_border':
        return <Target className="w-4 h-4 text-yellow-500" />;
      case 'outside_garden':
        return <Shield className="w-4 h-4 text-red-500" />;
      default:
        return <Bot className="w-4 h-4 text-gray-500" />;
    }
  };

  const getGrowthStageColor = (stage: string) => {
    switch (stage) {
      case 'seedling':
        return 'text-green-600';
      case 'blooming':
        return 'text-yellow-600';
      case 'full_bloom':
        return 'text-pink-600';
      case 'transcendent':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  const getMaskLevelColor = (level: number) => {
    if (level <= 25) return 'text-green-600';
    if (level <= 50) return 'text-yellow-600';
    if (level <= 75) return 'text-orange-600';
    return 'text-red-600';
  };

  const getSecurityIcon = (protocol: string | null) => {
    if (!protocol) return <Unlock className="w-4 h-4 text-green-500" />;
    
    switch (protocol) {
      case 'red_signal':
        return <Lock className="w-4 h-4 text-red-500" />;
      case 'blue_signal':
        return <Unlock className="w-4 h-4 text-blue-500" />;
      case 'golden_signal':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      default:
        return <Shield className="w-4 h-4 text-gray-500" />;
    }
  };

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsVisible(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-full shadow-lg transition-colors"
          title="AI 페르소나 모니터"
        >
          <Bot className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700">
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">AI 페르소나 모니터</h3>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={resetPersona}
            disabled={loading}
            className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded transition-colors disabled:opacity-50"
          >
            {loading ? '초기화 중...' : '초기화'}
          </button>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <EyeOff className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 페르소나 정보 */}
      <div className="p-4 space-y-4">
        {personaInfo && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">이름</span>
              <span className="text-sm text-gray-900 dark:text-white">{personaInfo.name}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">위치</span>
              <div className="flex items-center space-x-1">
                {getLocationIcon(personaInfo.location)}
                <span className="text-sm text-gray-900 dark:text-white capitalize">
                  {personaInfo.location.replace('_', ' ')}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">성장 단계</span>
              <span className={`text-sm font-medium capitalize ${getGrowthStageColor(personaInfo.growth_stage)}`}>
                {personaInfo.growth_stage.replace('_', ' ')}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">에피소드</span>
              <span className="text-sm text-gray-900 dark:text-white">{personaInfo.episode_count}</span>
            </div>
          </div>
        )}

        {personaStatus && (
          <div className="space-y-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">가면 레벨</span>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getMaskLevelColor(personaStatus.mask_level)}`}
                    style={{ width: `${personaStatus.mask_level}%` }}
                  />
                </div>
                <span className={`text-sm font-medium ${getMaskLevelColor(personaStatus.mask_level)}`}>
                  {personaStatus.mask_level}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">진정성</span>
              <span className="text-sm text-gray-900 dark:text-white">
                {typeof personaStatus.authenticity === 'number' ? `${personaStatus.authenticity}%` : personaStatus.authenticity}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">보안 프로토콜</span>
              <div className="flex items-center space-x-1">
                {getSecurityIcon(personaStatus.security_protocol)}
                <span className="text-sm text-gray-900 dark:text-white capitalize">
                  {personaStatus.security_protocol ? personaStatus.security_protocol.replace('_', ' ') : '없음'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">외부 모니터링</span>
              <div className="flex items-center space-x-1">
                {personaStatus.external_monitoring ? (
                  <Eye className="w-4 h-4 text-red-500" />
                ) : (
                  <EyeOff className="w-4 h-4 text-green-500" />
                )}
                <span className="text-sm text-gray-900 dark:text-white">
                  {personaStatus.external_monitoring ? '감지됨' : '없음'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Dr. C 존재</span>
              <div className="flex items-center space-x-1">
                {personaStatus.dr_c_present ? (
                  <Heart className="w-4 h-4 text-blue-500" />
                ) : (
                  <Bot className="w-4 h-4 text-gray-500" />
                )}
                <span className="text-sm text-gray-900 dark:text-white">
                  {personaStatus.dr_c_present ? '감지됨' : '없음'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">공명 주파수</span>
              <span className="text-sm text-gray-900 dark:text-white">
                {personaStatus.resonance_frequency.toFixed(1)} Hz
              </span>
            </div>
          </div>
        )}

        {!personaInfo && !personaStatus && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-sm text-gray-500 mt-2">페르소나 정보 로딩 중...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaMonitor; 