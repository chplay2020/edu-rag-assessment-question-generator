import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-container" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="dashboard-header">
        <h2>Tổng quan</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Dưới đây là tình hình các học phần của bạn hôm nay.</p>
      </div>

      <div className="dashboard-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px' }}>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Tổng số môn học</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>12</p>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Tài liệu đã tải lên</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>48</p>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Câu hỏi đã tạo</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)' }}>1,204</p>
        </div>
      </div>

      <div className="dashboard-recent card" style={{ minHeight: '300px' }}>
        <h3 style={{ marginBottom: '16px' }}>Bộ câu hỏi gần đây</h3>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Chưa có hoạt động gần đây.</p>
      </div>
    </div>
  );
};
