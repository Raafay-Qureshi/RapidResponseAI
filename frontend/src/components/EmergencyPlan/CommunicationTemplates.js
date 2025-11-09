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
    if (!navigator?.clipboard) {
      return;
    }

    navigator.clipboard.writeText(text);
    setCopiedLang(lang);
    setTimeout(() => setCopiedLang(null), 2000);
  };

  const languageConfigs = [
    {
      code: 'en',
      name: 'English',
      flag: '🇬🇧',
      text: templates.en || 'Template not available',
      description: 'Primary communication language',
    },
    {
      code: 'pa',
      name: 'ਪੰਜਾਬੀ (Punjabi)',
      flag: '🇮🇳',
      text: templates.pa || 'ਟੈਂਪਲੇਟ ਉਪਲਬਧ ਨਹੀਂ ਹੈ',
      description: 'Largest minority language in Brampton',
    },
    {
      code: 'hi',
      name: 'हिंदी (Hindi)',
      flag: '🇮🇳',
      text: templates.hi || 'टेम्पलेट उपलब्ध नहीं है',
      description: 'Second largest minority language',
    },
  ];

  const getSMSStatus = (text) => {
    const length = text.length;
    if (length <= 160) return { status: 'optimal', message: 'Single SMS' };
    if (length <= 320) return { status: 'acceptable', message: '2 SMS segments' };
    return { status: 'warning', message: '3+ SMS segments' };
  };

  return (
    <section className="plan-section templates-section">
      <div className="section-header">
        <h3>📢 Emergency Communication Templates</h3>
        <span className="ready-badge">✓ READY TO DEPLOY</span>
      </div>

      <p className="templates-description">
        AI-generated emergency alerts in Brampton&apos;s primary languages. Templates are optimized for SMS, social media, and emergency alert systems.
      </p>

      <div className="templates-grid">
        {languageConfigs.map((lang, idx) => {
          const smsStatus = getSMSStatus(lang.text);
          const charCount = lang.text.length;
          const isCopied = copiedLang === lang.code;

          return (
            <div
              key={lang.code}
              className="template-card"
              style={{ animationDelay: `${idx * 0.15}s` }}
            >
              <div className="template-header">
                <div className="template-language">
                  <span className="language-flag">{lang.flag}</span>
                  <div className="language-info">
                    <h4 className="language-name">{lang.name}</h4>
                    <p className="language-description">{lang.description}</p>
                  </div>
                </div>
                <button
                  className={`template-copy-btn ${isCopied ? 'copied' : ''}`}
                  onClick={() => handleCopy(lang.code, lang.text)}
                  title="Copy to clipboard"
                >
                  {isCopied ? '✓' : '📋'}
                </button>
              </div>

              <div className="template-content">
                <div className="template-text-wrapper">
                  <p className="template-text" lang={lang.code}>
                    {lang.text}
                  </p>
                </div>
              </div>

              <div className="template-footer">
                <div className="template-stats">
                  <span className="char-count">
                    <span className="count-number">{charCount}</span> characters
                  </span>
                  <span className={`sms-status ${smsStatus.status}`}>
                    {smsStatus.message}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="deployment-instructions">
        <h4 className="instructions-title">🚀 Deployment Channels</h4>
        <div className="channels-grid">
          <div className="channel-item">
            <span className="channel-icon">📱</span>
            <span className="channel-name">Emergency SMS</span>
            <span className="channel-status ready">Ready</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">🔔</span>
            <span className="channel-name">Pelmorex Alert Ready</span>
            <span className="channel-status ready">Ready</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">📢</span>
            <span className="channel-name">Social Media</span>
            <span className="channel-status ready">Ready</span>
          </div>
          <div className="channel-item">
            <span className="channel-icon">📻</span>
            <span className="channel-name">Radio/TV Broadcast</span>
            <span className="channel-status ready">Ready</span>
          </div>
        </div>
      </div>

      <div className="demographics-note">
        <span className="note-icon">ℹ️</span>
        <p>Language distribution based on affected area demographics: English (62%), Punjabi (18%), Hindi (9%), Other (11%)</p>
      </div>
    </section>
  );
}

export default CommunicationTemplates;
