import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import './MainLayout.css';
import { Button } from '../components/common/Button';
import logo from '../assets/Logo.png';

export const MainLayout: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="sidebar-header">
          <img src={logo} className="sidebar-logo" alt="Edu RAG Logo" />
          <h2>Edu RAG</h2>
        </div>
        <nav className="sidebar-nav">
          <Link to="/" className="nav-item active">Dashboard</Link>
          <Link to="/questions" className="nav-item">Question Bank</Link>
          <Link to="/courses" className="nav-item">Courses</Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Header */}
        <header className="header glass-panel">
          <div className="header-title">
            <h3>Welcome back, Lecturer</h3>
          </div>
          <div className="header-actions">
            <Button variant="secondary" size="sm" onClick={handleLogout}>Logout</Button>
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
