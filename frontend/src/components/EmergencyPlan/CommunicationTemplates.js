import React, { useState } from 'react';
import './CommunicationTemplates.css';

function CommunicationTemplates({ templates }) {
  const [copiedLang, setCopiedLang] = useState(null);

  if (!templates) {
    return (
      <section className="plan-section">
        <h3>📢 Communication Templates</h3>
        <p className="no-data">Communication templates not available</p>
      </section>
    );
  }

  const handleCopy = (lang, text) => {
    if (text) {
      navigator.clipboard.writeText(text);
      setCopiedLang(lang);
      setTimeout(() => setCopiedLang(null), 2000);
    }
  };

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧', font: 'default' },
    { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)', flag: '🇮🇳', font: 'punjabi' },
    { code: 'hi', name: 'Hindi (हिंदी)', flag: '🇮🇳', font: 'hindi' }
  ];

  const getCharacterCount = (text) => {
    return text ? text.length : 0;
  };

  const isSMSLength = (text) => {
    return text && text.length <= 160;
  };

  return (
    <section className="plan-section communication-section">
      <h3>📢 Multi-Language Emergency Communications</h3>
      <p className="section-description">
        Culturally-appropriate emergency alerts for Brampton's diverse population
      </p>

      <div className="templates-grid">
        {languages.map((lang) => {
          const text = templates[lang.code];
          const charCount = getCharacterCount(text);
          const smsReady = isSMSLength(text);

          return (
            <div key={lang.code} className={`template-card ${lang.font}`}>
              <div className="template-header">
                <div className="language-info">
                  <span className="language-flag">{lang.flag}</span>
                  <span className="language-name">{lang.name}</span>
                </div>
                <button
                  className={`copy-button ${copiedLang === lang.code ? 'copied' : ''}`}
                  onClick={() => handleCopy(lang.code, text)}
                  title="Copy to clipboard"
                >
                  {copiedLang === lang.code ? '✓ Copied' : '📋 Copy'}
                </button>
              </div>

              <div className="template-content">
                {text || 'Template not available'}
              </div>

              <div className="template-meta">
                <span className="character-count">
                  {charCount} characters
                </span>
                <span className={`sms-status ${smsReady ? 'ready' : 'long'}`}>
                  {smsReady ? '✓ SMS Ready' : '⚠️ Too long for SMS'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="deployment-channels">
        <h4 className="deployment-title">📡 Recommended Deployment Channels</h4>
        <div className="channels-grid">
          <div className="channel-item">
            <span className="channel-icon">📱</span>
            <span className="channel-name">Emergency SMS</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">🚨</span>
            <span className="channel-name">AlertReady Canada</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">📻</span>
            <span className="channel-name">Local Radio (AM 740, AM 1540)</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">📺</span>
            <span className="channel-name">Cable TV Crawl</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">🌐</span>
            <span className="channel-name">Social Media (Twitter/X, Facebook)</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">🔊</span>
            <span className="channel-name">Community Loudspeakers</span>
          </div>
        </div>
      </div>

      <div className="communication-note">
        <span className="note-icon">ℹ️</span>
        <p>
          Templates optimized for Brampton's demographics: 25% Punjabi speakers, 10% Hindi speakers.
          All messages include critical safety information and evacuation instructions.
        </p>
      </div>
    </section>
  );
}

export default CommunicationTemplates;