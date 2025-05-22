'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'reader' | 'author' | 'administrator' | 'auditor';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  username: string;
  avatar?: string;
  did_protected?: boolean;
}

export interface Article {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  author: string;
  author_id?: string;
  author_anonymous: boolean;
  author_wallet_address?: string;
  tags: string[];
  published_at: string;
  likes: number;
  bookmarked?: boolean;
  image_url?: string;
  category?: string;
  subcategory?: string;
  language?: string;
  reading_time?: number;
  word_count?: number;
  status?: string;
  engagement_score?: number;
  quality_score?: number;
  trending_score?: number;
  view_count?: number;
  comment_count?: number;
  share_count?: number;
}

interface AppState {
  user: User | null;
  token: string | null;
  theme: 'light' | 'dark';
  chatOpen: boolean;
  currentArticle: Article | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  toggleTheme: () => void;
  toggleChat: (article?: Article) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      theme: 'light',
      chatOpen: false,
      currentArticle: null,

      setUser: (user) => {
        const data = localStorage.getItem('news-platform-storage');
        if (data) {
          const parsedData = JSON.parse(data);
          if (parsedData.user && parsedData.user.id === user?.id) {
            set({ user });
          } else {
            set({ user, token: null }); // Reset token if user changes
          }
        } else {
          set({ user });
        }
      },
      setToken: (token) => set({ token }),
      toggleTheme: () => set((state) => ({ 
        theme: state.theme === 'light' ? 'dark' : 'light' 
      })),
      toggleChat: (article) => set((state) => ({
        chatOpen: !state.chatOpen,
        currentArticle: article || state.currentArticle
      })),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: 'news-platform-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        theme: state.theme 
      }),
    }
  )
);