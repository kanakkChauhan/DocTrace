import React, { useState, useEffect } from 'react';

export const HeroTypewriter: React.FC = () => {
  const fullText = "Prove your code matches your specification.";
  const [displayText, setDisplayText] = useState("");

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setDisplayText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 45);

    return () => clearInterval(timer);
  }, []);

  return (
    <h1 style={{
      fontSize: '3.75rem',
      fontWeight: 850,
      letterSpacing: '-0.04em',
      color: '#2C221E',
      margin: '0 0 1.25rem 0',
      maxWidth: '820px',
      lineHeight: 1.1,
      minHeight: '4.5rem'
    }}>
      {displayText}
      <span style={{
        display: 'inline-block',
        width: '3px',
        height: '3.2rem',
        backgroundColor: '#5A3D31',
        verticalAlign: 'middle',
        marginLeft: '4px',
        animation: 'blink 0.8s infinite'
      }} />
    </h1>
  );
};