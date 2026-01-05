import axios from 'axios';
import type { Job } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const authAPI = {
  register: (email: string, password: string, preferences: string[]) =>
    api.post('/api/auth/register', { email, password, preferences }),

  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),

  loginWithTwitter: () => {
    try {
      // log the computed URL so it's visible in the browser console for debugging
      const url = `${API_URL}/api/auth/twitter/login`;
      // eslint-disable-next-line no-console
      console.log('Navigating to Twitter login URL:', url);
      window.location.href = url;
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to navigate to Twitter login URL', err);
      throw err;
    }
  },

  onboarding: (email: string, telegram_id: string | null, preferences: string[], alert_speed: string, in_app_notifications: boolean) =>
    api.post('/api/auth/onboarding', {
      email,
      telegram_id,
      preferences,
      alert_speed,
      in_app_notifications,
    }),

  connectGoogle: () =>
    api.get('/api/auth/google/connect').then(res => res.data),
};

// Jobs endpoints
export const jobsAPI = {
  getJobs: (category?: string, limit?: number, search?: string): Promise<Job[]> => {
    console.log(`API: Fetching jobs for category=${category}, limit=${limit}, search=${search}`);
    return api.get('/api/jobs', { params: { category, limit, search } }).then(res => {
      console.log(`API: Received ${res.data?.length || 0} jobs`);
      return res.data;
    });
  },

  getSavedJobs: (): Promise<Job[]> =>
    api.get('/api/jobs/saved').then(res => res.data),
};

// User endpoints
export const userAPI = {
  getCurrentUser: () =>
    api.get('/api/auth/me').then(res => res.data),

  getUserDashboard: (timeRange = 'week') =>
    api.get(`/api/analytics/user/dashboard?time_range=${timeRange}`).then(res => res.data),

  getStats: () =>
    api.get('/api/analytics/user/stats').then(res => res.data),
};

// Admin endpoints
export const adminAPI = {
  getAdminOverview: () =>
    api.get('/api/admin/overview').then(res => res.data),

  getAdminUsers: (page: number = 1, search: string = '', status?: string) =>
    api.get('/api/admin/users', {
      params: {
        skip: (page - 1) * 50,
        limit: 50,
        search,
        status: status || undefined
      }
    }).then(res => res.data),

  triggerScrape: (sync: boolean = false) =>
    api.post(`/api/admin/system/trigger-scrape?sync=${sync}`).then(res => res.data),

  migrateCategories: () =>
    api.post('/api/admin/system/migrate-categories').then(res => res.data),

  sendTestNotification: (userId: number) =>
    api.post(`/api/admin/system/send-test-notification?user_id=${userId}`).then(res => res.data),

  bulkUserAction: (userIds: number[], action: 'activate' | 'deactivate' | 'delete' | 'verify' | 'promote_admin' | 'demote_admin') =>
    api.post('/api/admin/users/bulk-action', {
      user_ids: userIds,
      action
    }).then(res => res.data),

  getUserDetails: (userId: number) =>
    api.get(`/api/admin/users/${userId}`).then(res => res.data),

  cleanupDuplicates: () =>
    api.post('/api/admin/jobs/cleanup-duplicates').then(res => res.data),

  resetSystemStatus: () =>
    api.post('/api/admin/system/reset-status').then(res => res.data),

  updateCookies: (cookies: string) =>
    api.post('/api/admin/system/update-cookies', { cookies }).then(res => res.data),

  exportUserData: async () => {
    const response = await api.get('/api/admin/users/export', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `users-export-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return { message: 'Export downloaded successfully' };
  },
};

export default api;