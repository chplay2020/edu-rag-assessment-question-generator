import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import './MainLayout.css';
import logo from '../assets/Logo.png';
import { House, BookBookmark, GraduationCap, SignOut, X } from '@phosphor-icons/react';
import { motion, AnimatePresence } from 'motion/react';

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showLogoutModal, setShowLogoutModal] = React.useState(false);
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);

  const handleLogout = () => {
    setIsLoggingOut(true);
    // Small delay for UX feedback before clearing
    setTimeout(() => {
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('access_token');
      navigate('/login');
    }, 350);
  };

  // Lấy thông tin user từ JWT token (hoặc fallback)
  const getUserInfo = () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const payloadStr = atob(token.split('.')[1]);
        const payload = JSON.parse(payloadStr);
        const email = payload.sub || 'admin@example.com';
        const roleStr = payload.role === 'admin' ? 'Quản trị viên' : 'Giảng viên';

        // Tạo tên hiển thị từ email (giả lập)
        const namePart = email.split('@')[0];
        const name = namePart.split('.').map((p: string) => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');

        // Lấy 2 chữ cái đầu làm avatar
        const initials = namePart.substring(0, 2).toUpperCase();

        return { name, email, role: roleStr, initials };
      }
    } catch (e) {
      console.error('Failed to parse JWT token', e);
    }

    // Fallback
    return {
      name: 'Nguyễn Văn An',
      email: 'admin@example.com',
      role: 'Giảng viên',
      initials: 'NA'
    };
  };

  const userInfo = getUserInfo();

  const navItems = [
    { path: '/', label: 'Tổng quan', icon: House },
    { path: '/questions', label: 'Ngân hàng câu hỏi', icon: BookBookmark },
    { path: '/courses', label: 'Môn học', icon: GraduationCap },
  ];

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <img src={logo} className="sidebar-logo" alt="Logo Edu RAG" />
          <h2>Edu<span className="brand-accent">RAG</span></h2>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <item.icon size={20} weight={isActive ? "duotone" : "regular"} />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeNavBg"
                    className="nav-item-active-bg"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Block Footer */}
        <div className="sidebar-footer">
          <div className="user-block">
            <div className="user-avatar">
              {userInfo.initials}
            </div>
            <div className="user-info">
              <span className="user-name">{userInfo.name}</span>
              <span className="user-role">{userInfo.role}</span>
            </div>
            <button
              className="btn-logout-icon"
              onClick={() => setShowLogoutModal(true)}
              title="Đăng xuất"
            >
              <SignOut size={18} weight="bold" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Page Content (Outlet) */}
        <main className="page-content">
          <div className="page-transition">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Xác nhận đăng xuất Modal */}
      <AnimatePresence>
        {showLogoutModal && (
          <motion.div
            key="logout-modal-backdrop"
            className="logout-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={(e) => {
              if (e.target === e.currentTarget && !isLoggingOut) {
                setShowLogoutModal(false);
              }
            }}
          >
            <motion.div
              className="logout-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="logout-modal-title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="logout-modal-header">
                <h3 id="logout-modal-title" className="logout-modal-title">
                  Đăng xuất khỏi hệ thống?
                </h3>
                <button
                  className="logout-modal-close"
                  onClick={() => setShowLogoutModal(false)}
                  disabled={isLoggingOut}
                  aria-label="Đóng"
                >
                  <X size={20} weight="regular" />
                </button>
              </div>

              <div className="logout-modal-body">
                <p className="logout-modal-desc">
                  Bạn sẽ được chuyển về trang đăng nhập. Hãy chắc chắn các thay đổi đã được lưu.
                </p>

                {/* Actions */}
                <div className="logout-modal-actions">
                  <button
                    className="logout-modal-btn-cancel"
                    onClick={() => setShowLogoutModal(false)}
                    disabled={isLoggingOut}
                  >
                    Trở lại
                  </button>
                  <button
                    className={`logout-modal-btn-confirm ${isLoggingOut ? 'loading' : ''}`}
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                  >
                    {isLoggingOut ? (
                      <span className="logout-spinner" />
                    ) : null}
                    <span>{isLoggingOut ? 'Đang xử lý…' : 'Đăng xuất'}</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
