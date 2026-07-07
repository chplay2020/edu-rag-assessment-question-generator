import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-container" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="dashboard-header">
        <h2>Dashboard Overview</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Here is what's happening with your courses today.</p>
      </div>

      <div className="dashboard-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px' }}>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Total Courses</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>12</p>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Materials Uploaded</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>48</p>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Questions Generated</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>1,204</p>
        </div>
      </div>

      <div className="dashboard-recent card" style={{ minHeight: '300px' }}>
        <h3 style={{ marginBottom: '16px' }}>Recent Question Sets</h3>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>No recent activity to show.</p>
      </div>
    </div>
  );
};
