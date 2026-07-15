import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';
import logo from '../assets/Logo.png';
import './Login.css';

export const Login: React.FC = () => {
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Giả lập đăng nhập thành công
    localStorage.setItem('isAuthenticated', 'true');
    navigate('/');
  };

  return (
    <div className="login-container">
      <div className="login-card glass-panel">
        <div className="login-header">
          <div className="login-logo-container">
            <img src={logo} className="login-logo" alt="Logo Edu RAG" />
            <h2>Edu RAG</h2>
          </div>
          <p>Hệ thống tạo câu hỏi từ tài liệu học phần</p>
        </div>
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label>Email / Tên đăng nhập</label>
            <input type="text" placeholder="Nhập email của bạn" defaultValue="admin@edurag.com" />
          </div>
          <div className="form-group">
            <label>Mật khẩu</label>
            <input type="password" placeholder="Nhập mật khẩu" defaultValue="password" />
          </div>
          <div className="login-actions">
            <Button type="submit" variant="primary" fullWidth>Đăng nhập</Button>
          </div>
        </form>
      </div>
    </div>
  );
};
