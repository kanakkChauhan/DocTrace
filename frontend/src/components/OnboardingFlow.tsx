import React, { useState, useEffect } from 'react';

interface OnboardingFlowProps {
  mode: 'spec-flow' | 'github-flow';
  onComplete: (data: { title: string; content: string; source: string; filepath: string }) => void;
  onBack: () => void;
  isLoading?: boolean;
}

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ mode, onComplete, onBack, isLoading = false }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [sourceCode, setSourceCode] = useState('');
  const [filePath, setFilePath] = useState('src/auth.py');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleLoadPreset = (type: 'auth' | 'stripe' | 'rate') => {
    if (isLoading) return;
    setValidationError(null);
    if (type === 'auth') {
      setTitle('OAuth2 & Token Security Spec');
      setContent('1. Access tokens must use RS256 signing algorithms.\n2. Refresh tokens must be stored in secure HTTP-only cookies.\n3. Failed login attempts must trigger account lockout after 5 tries.');
      setSourceCode('import jwt\n\ndef verify_token(token):\n    return jwt.decode(token, algorithms=["RS256"])');
      setFilePath(mode === 'github-flow' ? 'https://github.com/org/auth-service' : 'src/security/oauth.py');
    } else if (type === 'stripe') {
      setTitle('Stripe Webhook & Ledger Engine');
      setContent('1. All webhook signatures must be cryptographically verified using the Stripe webhook secret.\n2. Ledger transactions must be fully atomic to prevent double-charging.');
      setSourceCode('import stripe\n\ndef verify_webhook(payload, sig):\n    return stripe.Webhook.construct_event(payload, sig)');
      setFilePath(mode === 'github-flow' ? 'https://github.com/org/billing-engine' : 'src/services/stripe.py');
    } else {
      setTitle('API Rate Limiting Middleware');
      setContent('1. Public endpoints must enforce a strict rate limit of 60 requests per minute per IP address.\n2. Exceeded limits must return a 429 Too Many Requests status header.');
      setSourceCode('def check_rate_limit(ip):\n    return redis.incr(ip) < 60');
      setFilePath(mode === 'github-flow' ? 'https://github.com/org/api-gateway' : 'src/middleware/throttle.py');
    }
  };

  const headingText = "How DocTrace Verifies Code.";
  const subtitleText = "Our deterministic analysis engine bridges high-level documentation and low-level AST nodes to eliminate compliance drift across your lifecycle.";

  const [displayedHeading, setDisplayedHeading] = useState('');
  const [displayedSubtitle, setDisplayedSubtitle] = useState('');

  const steps = [
    { num: '01', title: 'Specification Ingestion', desc: 'Parses markdown or text documents into atomic, machine-readable requirements.' },
    { num: '02', title: 'Deep AST Parsing', desc: 'Traverses your codebase abstract syntax tree to map exact functions, classes, and parameters.' },
    { num: '03', title: 'Deterministic Matching', desc: 'Cross-references semantic claims directly against code logic with confidence scoring.' },
    { num: '04', title: 'Compliance Matrix', desc: 'Generates live verification ratios and continuous verification tracking.' },
  ];

  const [displayedStepNums, setDisplayedStepNums] = useState<string[]>(['', '', '', '']);
  const [displayedStepTitles, setDisplayedStepTitles] = useState<string[]>(['', '', '', '']);
  const [displayedStepDescs, setDisplayedStepDescs] = useState<string[]>(['', '', '', '']);

  useEffect(() => {
    let i = 0;
    const headingInterval = setInterval(() => {
      setDisplayedHeading(headingText.slice(0, i + 1));
      i++;
      if (i >= headingText.length) {
        clearInterval(headingInterval);

        let subIndex = 0;
        const subInterval = setInterval(() => {
          setDisplayedSubtitle(subtitleText.slice(0, subIndex + 1));
          subIndex++;
          if (subIndex >= subtitleText.length) {
            clearInterval(subInterval);

            steps.forEach((step, index) => {
              setTimeout(() => {
                let numIndex = 0;
                const numInterval = setInterval(() => {
                  setDisplayedStepNums(prev => {
                    const updated = [...prev];
                    updated[index] = step.num.slice(0, numIndex + 1);
                    return updated;
                  });
                  numIndex++;
                  if (numIndex >= step.num.length) {
                    clearInterval(numInterval);

                    let charIndex = 0;
                    const stepTitleInterval = setInterval(() => {
                      setDisplayedStepTitles(prev => {
                        const updated = [...prev];
                        updated[index] = step.title.slice(0, charIndex + 1);
                        return updated;
                      });
                      charIndex++;
                      if (charIndex >= step.title.length) {
                        clearInterval(stepTitleInterval);

                        let descIndex = 0;
                        const stepDescInterval = setInterval(() => {
                          setDisplayedStepDescs(prev => {
                            const updated = [...prev];
                            updated[index] = step.desc.slice(0, descIndex + 1);
                            return updated;
                          });
                          descIndex++;
                          if (descIndex >= step.desc.length) {
                            clearInterval(stepDescInterval);
                          }
                        }, 10);
                      }
                    }, 25);
                  }
                }, 30);
              }, index * 350);
            });
          }
        }, 15);
      }
    }, 30);

    return () => clearInterval(headingInterval);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    if (!title.trim() || (mode === 'spec-flow' && (!content.trim() || !sourceCode.trim())) || !filePath.trim()) {
      setValidationError("Please fill in all required configuration fields before initializing the trace engine.");
      return;
    }
    setValidationError(null);
    onComplete({ title, content, source: sourceCode, filepath: filePath });
  };

  return (
    <div style={{
      maxWidth: '1280px',
      margin: '2rem auto 4rem auto',
      padding: '0 2rem',
      textAlign: 'left'
    }}>
      <button
        onClick={onBack}
        disabled={isLoading}
        style={{
          background: 'none',
          border: 'none',
          color: isLoading ? '#D4C4BC' : '#6B574F',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          marginBottom: '2rem',
          fontSize: '0.85rem',
          fontWeight: 700,
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          transition: 'color 0.2s'
        }}
        onMouseEnter={(e) => { if(!isLoading) e.currentTarget.style.color = '#2C221E'; }}
        onMouseLeave={(e) => { if(!isLoading) e.currentTarget.style.color = '#6B574F'; }}
      >
        ← Back to overview
      </button>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 1fr',
        gap: '4rem',
        alignItems: 'start',
        opacity: isLoading ? 0.6 : 1,
        transition: 'opacity 0.3s ease'
      }}>
        <div style={{ padding: '0.5rem 0', pointerEvents: isLoading ? 'none' : 'auto' }}>
          <div style={{
            fontSize: '0.75rem',
            fontWeight: 800,
            color: '#9E857B',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            marginBottom: '0.75rem'
          }}>
            {mode === 'spec-flow' ? 'Workflow Pipeline 01 : Specification Ingestion' : 'Workflow Pipeline 02 : Repository Linkage'}
          </div>

          <h2 style={{ fontSize: '2.5rem', fontWeight: 850, color: '#2C221E', margin: '0 0 1rem 0', letterSpacing: '-0.03em', lineHeight: 1.15, minHeight: '5.5rem' }}>
            {displayedHeading}
          </h2>

          <p style={{ color: '#6B574F', fontSize: '1.05rem', marginBottom: '3rem', lineHeight: 1.65, fontWeight: 500, minHeight: '3.5rem' }}>
            {displayedSubtitle}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
            {steps.map((_, idx) => {
              const hasStarted = displayedStepNums[idx].length > 0;
              return (
                <div key={idx} style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                  <div style={{
                    background: '#FFFFFF',
                    border: hasStarted ? '1.5px solid #D4C4BC' : '1.5px solid transparent',
                    borderRadius: '12px',
                    width: '38px',
                    height: '38px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.8rem',
                    fontWeight: 800,
                    color: '#5A3D31',
                    flexShrink: '0',
                    boxShadow: hasStarted ? '0 4px 12px rgba(90, 61, 49, 0.05)' : 'none',
                    transition: 'all 0.3s ease'
                  }}>
                    {displayedStepNums[idx]}
                  </div>
                  <div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#2C221E', marginBottom: '0.25rem', minHeight: '1.4rem' }}>
                      {displayedStepTitles[idx]}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#6B574F', lineHeight: 1.55, minHeight: '2.5rem' }}>
                      {displayedStepDescs[idx]}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.7)',
            border: '1.5px dashed #D4C4BC',
            borderRadius: '20px',
            padding: '1.5rem 2rem',
            textAlign: 'left',
            pointerEvents: isLoading ? 'none' : 'auto'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#5A3D31', textTransform: 'uppercase', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
              ⚡ Quick-Fill Engineering Samples
            </div>
            <div style={{ fontSize: '0.85rem', color: '#6B574F', marginBottom: '1rem' }}>
              Click any sample preset below to instantly populate parameters with production data:
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                type="button"
                disabled={isLoading}
                onClick={() => handleLoadPreset('auth')}
                style={{ fontSize: '0.8rem', padding: '8px 14px', borderRadius: '10px', border: '1px solid #D4C4BC', background: '#FFFFFF', color: '#5A3D31', cursor: 'pointer', fontWeight: 700, boxShadow: '0 2px 5px rgba(90,61,49,0.05)' }}
              >
                🔐 OAuth2 Security
              </button>
              <button
                type="button"
                disabled={isLoading}
                onClick={() => handleLoadPreset('stripe')}
                style={{ fontSize: '0.8rem', padding: '8px 14px', borderRadius: '10px', border: '1px solid #D4C4BC', background: '#FFFFFF', color: '#5A3D31', cursor: 'pointer', fontWeight: 700, boxShadow: '0 2px 5px rgba(90,61,49,0.05)' }}
              >
                💳 Stripe Webhook
              </button>
              <button
                type="button"
                disabled={isLoading}
                onClick={() => handleLoadPreset('rate')}
                style={{ fontSize: '0.8rem', padding: '8px 14px', borderRadius: '10px', border: '1px solid #D4C4BC', background: '#FFFFFF', color: '#5A3D31', cursor: 'pointer', fontWeight: 700, boxShadow: '0 2px 5px rgba(90,61,49,0.05)' }}
              >
                ⚡ Rate Limiting
              </button>
            </div>
          </div>

          <div style={{
            background: '#FFFFFF',
            border: '1.5px solid #D4C4BC',
            borderRadius: '24px',
            padding: '2.5rem',
            boxShadow: '0 20px 40px -10px rgba(90, 61, 49, 0.12)',
            position: 'relative'
          }}>
            <div style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              color: '#5A3D31',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              marginBottom: '0.4rem'
            }}>
              Configuration Parameters
            </div>

            <h3 style={{ fontSize: '1.6rem', fontWeight: 850, color: '#2C221E', margin: '0 0 1.25rem 0', letterSpacing: '-0.02em' }}>
              {mode === 'spec-flow' ? 'Configure Specification' : 'Connect GitHub Repository'}
            </h3>

            {validationError && (
              <div style={{ color: '#DC2626', background: 'rgba(220, 38, 38, 0.1)', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600, marginBottom: '1.25rem', border: '1px solid rgba(220, 38, 38, 0.2)' }}>
                {validationError}
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#5A3D31', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Document Title
                </label>
                <input
                  type="text"
                  disabled={isLoading}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder={mode === 'spec-flow' ? "e.g., OAuth2 & Token Security Spec" : "e.g., Backend Core API"}
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    background: isLoading ? '#F0EBE8' : '#FAF7F5',
                    border: '1.5px solid #D4C4BC',
                    borderRadius: '12px',
                    color: '#2C221E',
                    fontSize: '0.925rem',
                    fontWeight: 500,
                    boxSizing: 'border-box',
                    outline: 'none',
                    transition: 'border-color 0.2s ease'
                  }}
                  onFocus={(e) => { e.target.style.borderColor = '#5A3D31'; }}
                  onBlur={(e) => { e.target.style.borderColor = '#D4C4BC'; }}
                />
              </div>

              {mode === 'spec-flow' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#5A3D31', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Specification Content / Requirements
                  </label>
                  <textarea
                    rows={4}
                    disabled={isLoading}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder={"1. Access tokens must use RS256 signing algorithms.\n2. Refresh tokens must be stored in secure HTTP-only cookies."}
                    style={{
                      width: '100%',
                      padding: '11px 14px',
                      background: isLoading ? '#F0EBE8' : '#FAF7F5',
                      border: '1.5px solid #D4C4BC',
                      borderRadius: '12px',
                      color: '#2C221E',
                      fontSize: '0.925rem',
                      fontWeight: 500,
                      fontFamily: 'inherit',
                      boxSizing: 'border-box',
                      outline: 'none',
                      lineHeight: 1.5,
                      transition: 'border-color 0.2s ease'
                    }}
                    onFocus={(e) => { e.target.style.borderColor = '#5A3D31'; }}
                    onBlur={(e) => { e.target.style.borderColor = '#D4C4BC'; }}
                  />
                </div>
              )}

              {mode === 'spec-flow' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#5A3D31', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Source Code Content (Python)
                  </label>
                  <textarea
                    rows={6}
                    disabled={isLoading}
                    value={sourceCode}
                    onChange={(e) => setSourceCode(e.target.value)}
                    placeholder={"import bcrypt\n\ndef hash_password(password):\n    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())"}
                    style={{
                      width: '100%',
                      padding: '11px 14px',
                      background: isLoading ? '#F0EBE8' : '#FAF7F5',
                      border: '1.5px solid #D4C4BC',
                      borderRadius: '12px',
                      color: '#2C221E',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                      fontFamily: 'monospace',
                      boxSizing: 'border-box',
                      outline: 'none',
                      lineHeight: 1.5,
                      transition: 'border-color 0.2s ease'
                    }}
                    onFocus={(e) => { e.target.style.borderColor = '#5A3D31'; }}
                    onBlur={(e) => { e.target.style.borderColor = '#D4C4BC'; }}
                  />
                </div>
              )}

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#5A3D31', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {mode === 'github-flow' ? 'GitHub Repository URL' : 'Target Code File Path'}
                </label>
                <input
                  type="text"
                  disabled={isLoading}
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  placeholder={mode === 'github-flow' ? "https://github.com/org/doctrace-backend" : "src/auth.py"}
                  style={{
                    width: '100%',
                    padding: '11px 14px',
                    background: isLoading ? '#F0EBE8' : '#FAF7F5',
                    border: '1.5px solid #D4C4BC',
                    borderRadius: '12px',
                    color: '#2C221E',
                    fontSize: '0.925rem',
                    fontWeight: 500,
                    boxSizing: 'border-box',
                    outline: 'none',
                    transition: 'border-color 0.2s ease'
                  }}
                  onFocus={(e) => { e.target.style.borderColor = '#5A3D31'; }}
                  onBlur={(e) => { e.target.style.borderColor = '#D4C4BC'; }}
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                style={{
                  marginTop: '0.75rem',
                  background: isLoading ? '#D4C4BC' : 'linear-gradient(135deg, #5A3D31 0%, #3E2920 100%)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '14px',
                  padding: '1rem',
                  fontSize: '1rem',
                  fontWeight: 800,
                  cursor: isLoading ? 'wait' : 'pointer',
                  boxShadow: isLoading ? 'none' : '0 10px 25px rgba(90, 61, 49, 0.3)',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if(!isLoading) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 15px 30px rgba(90, 61, 49, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  if(!isLoading) {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 10px 25px rgba(90, 61, 49, 0.3)';
                  }
                }}
              >
                {isLoading ? '⏳ Processing Trace Pipeline...' : 'Initialize Trace Engine →'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};