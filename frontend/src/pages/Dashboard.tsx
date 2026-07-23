import React from 'react';
import { motion } from 'motion/react';
import { GraduationCap, FileArrowUp, FilePlus, Sparkle, Clock, ArrowUpRight, CheckCircle, Warning } from '@phosphor-icons/react';

export const Dashboard: React.FC = () => {
  // Stagger animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  } as const;

  const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
  } as const;

  // Mockup data
  const mockRecentSets = [
    {
      id: 1,
      title: "Đề thi giữa kỳ - Lập trình Web nâng cao",
      course: "Web nâng cao",
      questionsCount: 40,
      createdAt: "2 giờ trước",
      status: "success",
      statusLabel: "Hoàn thành"
    },
    {
      id: 2,
      title: "Trắc nghiệm ôn tập Chương 2 - RDBMS",
      course: "Cơ sở dữ liệu",
      questionsCount: 20,
      createdAt: "Hôm qua",
      status: "success",
      statusLabel: "Hoàn thành"
    },
    {
      id: 3,
      title: "Bộ câu hỏi kiểm tra nhanh - AI & Machine Learning",
      course: "Trí tuệ nhân tạo",
      questionsCount: 15,
      createdAt: "3 ngày trước",
      status: "draft",
      statusLabel: "Bản nháp"
    }
  ];

  const hasActivity = true; // Set true để hiển thị ds

  return (
    <motion.div
      className="dashboard-container"
      style={{ padding: '32px 32px 40px 32px', display: 'flex', flexDirection: 'column', gap: '24px' }}
      variants={containerVariants}
      initial={false}
      animate="show"
    >
      {/* Dashboard Welcome Header */}
      <motion.div className="dashboard-header" variants={itemVariants}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-text-main)', letterSpacing: '-0.02em', marginBottom: '6px' }}>
          Tổng quan
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem' }}>
          Dưới đây là tình hình các môn học của bạn hôm nay.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        className="dashboard-stats"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}
        variants={containerVariants}
      >
        {/* Stat 1 */}
        <motion.div
          className="card"
          variants={itemVariants}
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', position: 'relative', overflow: 'hidden' }}
        >
          <div>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text-muted)', marginBottom: '12px' }}>
              Tổng số môn học
            </h3>
            <p style={{ fontSize: '2.5rem', fontWeight: 600, color: 'var(--color-text-main)', letterSpacing: '-0.04em', lineHeight: 1 }}>
              12
            </p>
            <div style={{ marginTop: '16px', fontSize: '0.8rem', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
              <ArrowUpRight size={14} />
              <span>+2 môn mới học kỳ này</span>
            </div>
          </div>
          <div style={{ padding: '12px', borderRadius: '12px', background: 'rgba(79, 70, 229, 0.08)', color: 'var(--color-primary)' }}>
            <GraduationCap size={24} weight="duotone" />
          </div>
        </motion.div>

        {/* Stat 2 */}
        <motion.div
          className="card"
          variants={itemVariants}
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', position: 'relative', overflow: 'hidden' }}
        >
          <div>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text-muted)', marginBottom: '12px' }}>
              Tài liệu đã tải lên
            </h3>
            <p style={{ fontSize: '2.5rem', fontWeight: 600, color: 'var(--color-text-main)', letterSpacing: '-0.04em', lineHeight: 1 }}>
              48
            </p>
            <div style={{ marginTop: '16px', fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
              <ArrowUpRight size={14} />
              <span>+6 tài liệu tuần này</span>
            </div>
          </div>
          <div style={{ padding: '12px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.08)', color: '#10b981' }}>
            <FileArrowUp size={24} weight="duotone" />
          </div>
        </motion.div>

        {/* Stat 3 */}
        <motion.div
          className="card"
          variants={itemVariants}
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', position: 'relative', overflow: 'hidden' }}
        >
          <div>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text-muted)', marginBottom: '12px' }}>
              Câu hỏi đã tạo
            </h3>
            <p style={{ fontSize: '2.5rem', fontWeight: 600, color: 'var(--color-text-main)', letterSpacing: '-0.04em', lineHeight: 1 }}>
              1,204
            </p>
            <div style={{ marginTop: '16px', fontSize: '0.8rem', color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
              <ArrowUpRight size={14} />
              <span>+128 câu sinh trong 24h</span>
            </div>
          </div>
          <div style={{ padding: '12px', borderRadius: '12px', background: 'rgba(139, 92, 246, 0.08)', color: '#8b5cf6' }}>
            <Sparkle size={24} weight="duotone" />
          </div>
        </motion.div>
      </motion.div>

      {/* Recent Activity / Question Sets Section */}
      <motion.div className="dashboard-recent card" variants={itemVariants} style={{ padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-text-main)', letterSpacing: '-0.01em', margin: 0 }}>
            Bộ câu hỏi gần đây
          </h3>
          {hasActivity && (
            <button style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              border: 'none',
              background: 'none',
              color: 'var(--color-primary)',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}>
              <span>Xem tất cả</span>
              <ArrowUpRight size={16} />
            </button>
          )}
        </div>

        {hasActivity ? (
          /* Premium Table View */
          <div style={{ overflowX: 'auto', margin: '0 -28px -28px', padding: '0 28px 28px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(226, 232, 240, 0.8)' }}>
                  <th style={{ padding: '12px 16px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Tên bộ câu hỏi</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Môn học</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Số câu</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Thời gian</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {mockRecentSets.map((set) => (
                  <tr
                    key={set.id}
                    style={{
                      borderBottom: '1px solid rgba(241, 245, 249, 0.8)',
                      transition: 'background-color 0.2s ease',
                      cursor: 'pointer'
                    }}
                    className="hover-row"
                  >
                    <td style={{ padding: '16px', fontWeight: 500, color: 'var(--color-text-main)', fontSize: '0.95rem' }}>{set.title}</td>
                    <td style={{ padding: '16px', color: 'var(--color-text-muted)', fontSize: '0.95rem' }}>{set.course}</td>
                    <td style={{ padding: '16px', color: 'var(--color-text-main)', fontWeight: 600, fontSize: '0.95rem' }}>{set.questionsCount}</td>
                    <td style={{ padding: '16px', color: 'var(--color-text-muted)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Clock size={14} />
                      <span>{set.createdAt}</span>
                    </td>
                    <td style={{ padding: '16px' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '4px 10px',
                        borderRadius: '99px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        background: set.status === 'success' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(245, 158, 11, 0.08)',
                        color: set.status === 'success' ? '#10b981' : '#f59e0b'
                      }}>
                        {set.status === 'success' ? <CheckCircle size={12} weight="fill" /> : <Warning size={12} weight="fill" />}
                        <span>{set.statusLabel}</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Premium Illustrated Empty State */
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 0', textAlign: 'center' }}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '24px',
              background: 'rgba(241, 245, 249, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-text-muted)',
              marginBottom: '20px'
            }}>
              <FilePlus size={40} weight="duotone" style={{ opacity: 0.7 }} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '8px' }}>
              Chưa có bộ câu hỏi nào được tạo
            </h4>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', maxWidth: '380px', lineHeight: 1.5, marginBottom: '24px' }}>
              Chưa có hoạt động gần đây. Hãy tải lên tài liệu môn học để bắt đầu tạo câu hỏi trắc nghiệm đánh giá tự động.
            </p>
            <button style={{
              padding: '10px 20px',
              borderRadius: '10px',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              fontWeight: 600,
              fontSize: '0.9rem',
              boxShadow: '0 4px 12px rgba(79, 70, 229, 0.15)',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Sparkle size={16} weight="fill" />
              <span>Tạo bộ câu hỏi ngay</span>
            </button>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};
