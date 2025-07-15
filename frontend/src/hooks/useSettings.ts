import { useState, useEffect } from 'react';
import { loadSettings, saveSettings } from '../utils/storageUtils';
import { Settings } from '../types';

export const useSettings = () => {
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [fontSize, setFontSize] = useState<Settings['fontSize']>('medium');

  // 초기 설정 로드
  useEffect(() => {
    const settings = loadSettings();
    setDarkMode(settings.darkMode);
    setFontSize(settings.fontSize);
  }, []);

  // 설정 변경 시 저장
  useEffect(() => {
    const settings: Settings = { darkMode, fontSize };
    saveSettings(settings);
  }, [darkMode, fontSize]);

  const toggleDarkMode = (): void => {
    setDarkMode(prev => !prev);
  };

  const updateFontSize = (size: Settings['fontSize']): void => {
    setFontSize(size);
  };

  const resetSettings = (): void => {
    setDarkMode(false);
    setFontSize('medium');
  };

  return {
    darkMode,
    fontSize,
    toggleDarkMode,
    updateFontSize,
    resetSettings
  };
}; 