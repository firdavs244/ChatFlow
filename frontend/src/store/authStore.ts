// ===========================================
// ChatFlow - Auth Store (Zustand)
// ===========================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';
import { api } from '@/lib/api';
import { wsClient } from '@/lib/websocket';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.login(email, password);
          set({ 
            user: response.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          // Connect WebSocket
          wsClient.connect(response.access_token);
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login xatosi', 
            isLoading: false 
          });
          throw error;
        }
      },

      register: async (email: string, username: string, fullName: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.register(email, username, fullName, password);
          set({ 
            user: response.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          // Connect WebSocket
          wsClient.connect(response.access_token);
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Ro\'yxatdan o\'tish xatosi', 
            isLoading: false 
          });
          throw error;
        }
      },

      logout: () => {
        api.logout();
        wsClient.disconnect();
        set({ user: null, isAuthenticated: false, isLoading: false });
      },

      updateUser: async (data: Partial<User>) => {
        try {
          const updatedUser = await api.updateProfile(data);
          set({ user: updatedUser });
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Yangilash xatosi' });
          throw error;
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isLoading: false, isAuthenticated: false });
          return;
        }

        try {
          const user = await api.getMe();
          set({ user, isAuthenticated: true, isLoading: false });
          // Connect WebSocket
          wsClient.connect(token);
        } catch (error) {
          api.logout();
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

