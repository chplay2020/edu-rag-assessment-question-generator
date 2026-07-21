import api from './api';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  login: async (email: string, password: string):Promise<LoginResponse> => {
    try {
      // Using application/x-www-form-urlencoded as it's common for OAuth2 Password Bearer in FastAPI
      const params = new URLSearchParams();
      params.append('username', email); // backend expects 'username' for OAuth2
      params.append('password', password);
      
      const response = await api.post<LoginResponse>('/api/v1/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      console.warn('API login failed, falling back to mock login for FE testing', error);
      // Mock login fallback if backend isn't ready
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            access_token: 'mock-jwt-token-12345',
            token_type: 'bearer'
          });
        }, 500);
      });
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  }
};
