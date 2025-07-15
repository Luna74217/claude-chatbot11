import React from 'react';
import { highlightSearchQuery } from '../../utils/searchUtils';

const MarkdownRenderer = ({ content, darkMode, searchQuery = '', isSearching = false }) => {
  const renderMarkdown = (text) => {
    // 먼저 검색어 하이라이팅 적용
    text = highlightSearchQuery(text, searchQuery, isSearching);

    // 코드 블록 처리 (```로 감싸진 부분)
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre class="markdown-code-block ${darkMode ? 'dark' : 'light'}"><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`;
    });

    // 인라인 코드 처리
    text = text.replace(/`([^`]+)`/g, '<code class="markdown-inline-code">$1</code>');

    // 굵은 글씨
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // 기울임체
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 제목 처리
    text = text.replace(/^### (.*$)/gim, '<h3 class="markdown-h3">$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2 class="markdown-h2">$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1 class="markdown-h1">$1</h1>');

    // 목록 처리
    text = text.replace(/^\- (.*$)/gim, '<li class="markdown-list-item">$1</li>');
    text = text.replace(/(<li class="markdown-list-item">.*<\/li>)/s, '<ul class="markdown-list">$1</ul>');

    // 숫자 목록
    text = text.replace(/^\d+\. (.*$)/gim, '<li class="markdown-ordered-item">$1</li>');

    // 링크 처리
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="markdown-link" target="_blank" rel="noopener noreferrer">$1</a>');

    // 인용구
    text = text.replace(/^> (.*$)/gim, '<blockquote class="markdown-quote">$1</blockquote>');

    // 줄바꿈 처리
    text = text.replace(/\n/g, '<br />');

    return text;
  };

  return (
    <div 
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  );
};

export default MarkdownRenderer; 