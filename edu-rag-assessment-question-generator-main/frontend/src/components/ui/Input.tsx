import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, style, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const containerStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      marginBottom: '1rem',
    };

    const labelStyle: React.CSSProperties = {
      fontSize: '0.875rem',
      fontWeight: 500,
      color: '#374151',
    };

    const inputStyle: React.CSSProperties = {
      padding: '8px 12px',
      fontSize: '1rem',
      border: `1px solid ${error ? '#ef4444' : '#d1d5db'}`,
      borderRadius: '6px',
      outline: 'none',
      transition: 'border-color 0.2s ease',
      width: '100%',
      boxSizing: 'border-box',
      ...style,
    };

    const errorStyle: React.CSSProperties = {
      fontSize: '0.75rem',
      color: '#ef4444',
    };

    return (
      <div style={containerStyle}>
        {label && <label htmlFor={inputId} style={labelStyle}>{label}</label>}
        <input
          id={inputId}
          ref={ref}
          style={inputStyle}
          {...props}
        />
        {error && <span style={errorStyle}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
