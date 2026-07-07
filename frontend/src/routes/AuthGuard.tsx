import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

export const AuthGuard: React.FC = () => {
  // Mock authentication check
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
