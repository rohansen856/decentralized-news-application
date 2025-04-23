'use client';

import axios from 'axios';
import { Article, useStore } from './store';

// API Configuration
const FLASK_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Create API instances
const flaskAPI = axios.create({
  baseURL: FLASK_BASE_URL,
  timeout: 10000,
});

const fastAPI = axios.create({
  baseURL: FASTAPI_BASE_URL,
  timeout: 10000,
});

// Request interceptors to add auth headers
[flaskAPI, fastAPI].forEach(api => {
  api.interceptors.request.use((config) => {
    const token = useStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response interceptor for error handling
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        useStore.getState().logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
});

// Auth API (Flask)
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await flaskAPI.post('/api/v1/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email: string, password: string, username: string, role: string) => {
    const payload = { email, password, username, role }
    console.log(payload)
    const response = await flaskAPI.post('/api/v1/auth/register', payload);
    return response.data;
  },
  
  me: async () => {
    const response = await flaskAPI.get('/auth/me');
    return response.data;
  },
  
  updateProfile: async (data: any) => {
    const response = await flaskAPI.put('/auth/profile', data);
    return response.data;
  }
};

// Articles API (FastAPI)
export const articlesAPI = {
  getAll: async (params?: any): Promise<Article[]> => {
    const response = await fastAPI.get('/api/v1/articles', { params });
    const {data} = response
    if(data.success === false) {
      return []
    }
    return data.data;
  },
  
  getById: async (id: string): Promise<Article | null> => {
    const response = await fastAPI.get(`/api/v1/articles/${id}`);
    const {data} = response
    return data;
  },
  
  create: async (article: any) => {
    const response = await fastAPI.post('/api/v1/articles', article);
    return response.data;
  },
  
  update: async (id: string, article: any) => {
    const response = await fastAPI.put(`/api/v1/articles/${id}`, article);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await fastAPI.delete(`/api/v1/articles/${id}`);
    return response.data;
  },
  
  search: async (query: string, filters?: any) => {
    const response = await fastAPI.get('/api/v1/search', { 
      params: { q: query, ...filters } 
    });
    return response.data;
  },
  
  getRecommendations: async () => {
    const response = await fastAPI.get('/api/v1/recommendations');
    return response.data;
  },
  
  getTrending: async () => {
    const response = await fastAPI.get('/api/v1/trending');
    return response.data;
  }
};

// Chat API (FastAPI - Ollama integration)
export const chatAPI = {
  sendMessage: async (articleId: string, message: string, history?: any[]) => {
    const response = await fastAPI.post('/api/v1/chat', {
      article_id: articleId,
      message,
      history: history || []
    });
    return response.data;
  }
};

// Analytics API (Flask)
export const analyticsAPI = {
  getUserStats: async () => {
    const response = await flaskAPI.get('/api/v1/analytics/user');
    return response.data;
  },
  
  getArticleStats: async (articleId: string) => {
    const response = await flaskAPI.get(`/api/v1/analytics/article/${articleId}`);
    return response.data;
  },
  
  getAdminStats: async () => {
    const response = await flaskAPI.get('/api/v1/analytics/admin');
    return response.data;
  }
};

// Interactions API (FastAPI)
export const interactionsAPI = {
  like: async (articleId: string) => {
    const response = await fastAPI.post(`/api/v1/interactions/${articleId}/like`);
    return response.data;
  },
  
  bookmark: async (articleId: string) => {
    const response = await fastAPI.post(`/api/v1/interactions/${articleId}/bookmark`);
    return response.data;
  },
  
  share: async (articleId: string, platform: string) => {
    const response = await fastAPI.post(`/api/v1/interactions/${articleId}/share`, { platform });
    return response.data;
  },
  
  getStatus: async (articleId: string) => {
    const response = await fastAPI.get(`/api/v1/interactions/${articleId}/status`);
    return response.data;
  },
  
  recordView: async (articleId: string, timeSpent: number = 0, readingProgress: number = 0) => {
    const response = await fastAPI.post('/api/v1/interactions', {
      article_id: articleId,
      interaction_type: 'view',
      interaction_strength: Math.min(readingProgress, 1.0),
      reading_progress: readingProgress,
      time_spent: timeSpent,
      device_type: typeof window !== 'undefined' ? (window.innerWidth < 768 ? 'mobile' : 'desktop') : 'unknown'
    });
    return response.data;
  }
};