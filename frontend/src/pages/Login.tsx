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
            <img src={logo} className="login-logo" alt="Edu RAG Logo" />
            <h2>Edu RAG</h2>
          </div>
          <p>Assessment Question Generator</p>
        </div>
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label>Email / Username</label>
            <input type="text" placeholder="Enter your email" defaultValue="admin@edurag.com" />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" placeholder="Enter your password" defaultValue="password" />
          </div>
          <div className="login-actions">
            <Button type="submit" variant="primary" fullWidth>Sign In</Button>
          </div>
        </form>
      </div>
    </div>
  );
};
