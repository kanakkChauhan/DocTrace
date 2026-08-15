import React from 'react';

export type PipelineStage =
  | 'idle'
  | 'spec_loaded'
  | 'extracting_requirements'
  | 'analyzing_and_tracing'
  | 'calculating_compliance'
  | 'completed';

interface PipelineLoaderProps {
  currentStage: PipelineStage;
  error: string | null;
}

export const PipelineLoader: React.FC<PipelineLoaderProps> = ({ currentStage, error }) => {
  const stages: { key: PipelineStage; label: string }[] = [
    { key: 'spec_loaded', label: 'Creating specification document' },
    { key: 'extracting_requirements', label: 'Extracting semantic requirements & atomic claims' },
    { key: 'analyzing_and_tracing', label: 'Ingesting source, parsing AST & executing trace matching' },
    { key: 'calculating_compliance', label: 'Calculating project health & compliance metrics' },
  ];

  const stageOrder: PipelineStage[] = ['idle', 'spec_loaded', 'extracting_requirements', 'analyzing_and_tracing', 'calculating_compliance', 'completed'];
  const currentIndex = stageOrder.indexOf(currentStage);

  return (
    <div style={{
      maxWidth: '680px', margin: '5rem auto', background: '#FFFFFF', border: '1.5px solid #D4C4BC',
      borderRadius: '24px', padding: '3.5rem', boxShadow: '0 20px 40px -10px rgba(90, 61, 49, 0.08)', textAlign: 'left'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <span style={{
          display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%',
          backgroundColor: error ? '#DC2626' : '#5A3D31',
          animation: error || currentStage === 'completed' ? 'none' : 'pulse 2s infinite'
        }} />
        <span style={{
          fontSize: '0.75rem', fontWeight: 800, color: error ? '#DC2626' : '#9E857B',
          letterSpacing: '0.12em', textTransform: 'uppercase'
        }}>
          {error ? 'Pipeline Halted' : currentStage === 'completed' ? 'Verification Complete' : 'Verification Engine Active'}
        </span>
      </div>

      <h2 style={{ fontSize: '1.75rem', fontWeight: 850, color: '#2C221E', margin: '0 0 1.5rem 0', letterSpacing: '-0.03em' }}>
        {error ? 'Execution Failed' : currentStage === 'completed' ? 'Dashboard Ready' : 'Processing Engineering Pipeline...'}
      </h2>

      {/* Indeterminate Activity Bar */}
      <div style={{ width: '100vw', maxWidth: '100%', height: '8px', background: '#FAF7F5', borderRadius: '4px', overflow: 'hidden', border: '1px solid #D4C4BC', marginBottom: '2.5rem', position: 'relative' }}>
        {!error && currentStage !== 'completed' && (
          <div style={{ position: 'absolute', top: 0, left: 0, height: '100%', width: '30%', background: 'linear-gradient(90deg, transparent, #5A3D31, transparent)', animation: 'slide 1.5s infinite linear' }} />
        )}
        {(error || currentStage === 'completed') && (
          <div style={{ width: '100%', height: '100%', background: error ? '#DC2626' : '#5A3D31' }} />
        )}
      </div>

      {/* Truthful Stage List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {stages.map((stage, idx) => {
          const targetIndex = stageOrder.indexOf(stage.key);
          const isCompleted = currentIndex > targetIndex || currentStage === 'completed';
          const isActive = currentIndex === targetIndex;
          const isPending = currentIndex < targetIndex;
          const isError = isActive && error !== null;

          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', opacity: isPending ? 0.4 : 1, transition: 'opacity 0.3s ease' }}>
              <div style={{
                width: '26px', height: '26px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.7rem', fontWeight: 800, flexShrink: 0, marginTop: '2px',
                backgroundColor: isError ? '#DC2626' : isCompleted ? '#5A3D31' : isActive ? 'rgba(90, 61, 49, 0.1)' : '#FAF7F5',
                color: isError || isCompleted ? '#FFFFFF' : isActive ? '#5A3D31' : '#9E857B',
                border: `1.5px solid ${isError ? '#DC2626' : isCompleted || isActive ? '#5A3D31' : '#D4C4BC'}`
              }}>
                {isError ? '✕' : isCompleted ? '✓' : idx + 1}
              </div>

              <div style={{ width: '100%' }}>
                <div style={{ fontSize: '0.95rem', fontWeight: isActive ? 700 : 500, color: isError ? '#DC2626' : isActive ? '#2C221E' : isCompleted ? '#6B574F' : '#9E857B' }}>
                  {stage.label}
                  {isActive && !isError && <span style={{ marginLeft: '8px', fontSize: '0.8rem', color: '#9E857B', fontStyle: 'italic' }}>Running...</span>}
                </div>

                {isError && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#DC2626', background: 'rgba(220, 38, 38, 0.1)', padding: '10px 12px', borderRadius: '6px', fontWeight: 600 }}>
                    {error}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <style>{`@keyframes slide { 0% { left: -30%; } 100% { left: 100%; } }`}</style>
    </div>
  );
};