// frontend/src/services/auth.ts
import api from './api';

export const authService = {
  register: (email: string, password: string) =>
    api.post('/api/auth/register', { email, password }),

  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),

  logout: () => {
    localStorage.removeItem('user');
  },
};