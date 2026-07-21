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

  const [email, setEmail] = useState(
    localStorage.getItem('remembered_email') || ''
  );
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(
    Boolean(localStorage.getItem('remembered_email'))
  );
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    setError(null);
    setIsLoading(true);

    try {
      const data = await authService.login(email.trim(), password);

      if (!data?.access_token) {
        setError('Đăng nhập thất bại: Không nhận được token.');
        return;
      }

      // Thống nhất toàn bộ ứng dụng sử dụng key access_token
      localStorage.setItem('access_token', data.access_token);

      // Xóa key cũ để tránh xung đột với phiên bản trước
      localStorage.removeItem('token');
      localStorage.removeItem('isAuthenticated');

      if (rememberMe) {
        localStorage.setItem('remembered_email', email.trim());
      } else {
        localStorage.removeItem('remembered_email');
      }

      navigate('/', { replace: true });
    } catch (err: unknown) {
      console.error('Login error:', err);

      let message = 'Đăng nhập thất bại. Vui lòng kiểm tra lại.';

      if (
        typeof err === 'object' &&
        err !== null &&
        'response' in err
      ) {
        const axiosError = err as {
          response?: {
            data?: {
              detail?: string;
              message?: string;
            };
          };
        };

        message =
          axiosError.response?.data?.detail ||
          axiosError.response?.data?.message ||
          message;
      }

      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: {
      opacity: 0,
      scale: 0.96
    },
    show: {
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring' as const,
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
            <img
              src={logo}
              className="login-logo"
              alt="Logo Edu RAG"
            />
            <h2>Edu<span className="brand-accent">RAG</span></h2>
          </div>

          <p>Hệ thống tạo câu hỏi từ tài liệu học phần</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          {error && (
            <div
              className="login-error"
              role="alert"
              style={{
                color: '#dc2626',
                backgroundColor: '#fef2f2',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '14px',
                marginBottom: '16px',
                textAlign: 'center'
              }}
            >
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email / Tên đăng nhập</label>

            <div className="input-wrapper">
              <input
                id="email"
                name="email"
                type="text"
                placeholder="Nhập email của bạn"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
                required
              />

              <Envelope size={18} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>

            <div className="input-wrapper">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Nhập mật khẩu"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
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
                aria-label={
                  showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'
                }
                onClick={() => setShowPassword((current) => !current)}
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
                {showPassword ? (
                  <EyeSlash size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          <div className="login-helpers">
            <label className="remember-me">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span>Ghi nhớ đăng nhập</span>
            </label>

            <a
              href="/forgot-password"
              className="forgot-password"
              onClick={(e) => e.preventDefault()}
            >
              Quên mật khẩu?
            </a>
          </div>

          <div className="login-actions">
            <Button
              type="submit"
              variant="primary"
              fullWidth
              disabled={isLoading}
            >
              {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};