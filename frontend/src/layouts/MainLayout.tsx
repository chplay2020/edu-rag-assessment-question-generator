import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import './MainLayout.css';
import { Button } from '../components/common/Button';
import logo from '../assets/Logo.png';
import { House, BookBookmark, GraduationCap, SignOut } from '@phosphor-icons/react';
import { motion } from 'motion/react';

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

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
          <h2>Edu RAG</h2>
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
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Header */}
        <header className="header glass-panel">
          <div className="header-title">
            <h3>Chào mừng trở lại, Giảng viên</h3>
          </div>
          <div className="header-actions">
            <Button variant="secondary" size="sm" onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <SignOut size={16} />
              <span>Đăng xuất</span>
            </Button>
          </div>
        </header>

        {/* Page Content (Outlet) */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
