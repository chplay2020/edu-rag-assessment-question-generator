import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { authService } from '../services/auth';
import logo from '../assets/Logo.png';
import { Envelope, Lock, Eye, EyeSlash } from '@phosphor-icons/react';
import { motion } from 'motion/react';
import './Login.css';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@edurag.com');
  const [password, setPassword] = useState('password');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const data = await authService.login(email, password);
      // Lưu token vào localStorage
      localStorage.setItem('token', data.access_token);
      // Xóa flag isAuthenticated cũ nếu có
      localStorage.removeItem('isAuthenticated');
      
      // Redirect về dashboard
      navigate('/');
    } catch (err) {
      const error = err as any;
      setError(error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, scale: 0.96 },
    show: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring" as const,
        stiffness: 260,
        damping: 24
      }
    }
  } as const;

  return (
    <div className="login-container">
      <motion.div
        className="login-card glass-panel"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        <div className="login-header">
          <div className="login-logo-container">
            <img src={logo} className="login-logo" alt="Logo Edu RAG" />
            <h2>Edu RAG</h2>
          </div>
          <p>Hệ thống tạo câu hỏi từ tài liệu học phần</p>
        </div>
        
        {error && <div className="login-error" style={{ color: 'red', marginBottom: '16px', textAlign: 'center', fontSize: '0.875rem' }}>{error}</div>}

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label>Email / Tên đăng nhập</label>
            <div className="input-wrapper">
              <input 
                type="text" 
                placeholder="Nhập email của bạn" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Envelope size={18} />
            </div>
          </div>

          <div className="form-group">
            <label>Mật khẩu</label>
            <div className="input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Nhập mật khẩu"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  display: 'block',
                  boxSizing: 'border-box',
                  paddingRight: '44px'
                }}
              />
              <Lock size={18} />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px',
                  zIndex: 10
                }}
              >
                {showPassword ? <EyeSlash size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="login-helpers">
            <label className="remember-me">
              <input type="checkbox" />
              <span>Ghi nhớ đăng nhập</span>
            </label>
            <a href="#" className="forgot-password" onClick={(e) => e.preventDefault()}>
              Quên mật khẩu?
            </a>
          </div>

          <div className="login-actions">
            <Button type="submit" variant="primary" fullWidth disabled={isLoading}>
              {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};
