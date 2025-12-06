import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/token/', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  getToken: () => localStorage.getItem('access_token'),
};

// Sensor Readings API
export const sensorAPI = {
  create: (data) => api.post('/sensor-readings/', data),
  list: (plotId = null) => {
    const params = plotId ? { plot: plotId } : {};
    return api.get('/sensor-readings/list/', { params });
  },
};

// Anomalies API
export const anomalyAPI = {
  list: () => api.get('/anomalies/'),
};

// Recommendations API
export const recommendationAPI = {
  list: () => api.get('/recommendations/'),
};

// Plots API
export const plotsAPI = {
  list: () => api.get('/plots/'),
};

// Registration API
export const registerAPI = {
  register: (data) => api.post('/register/', data),
};

export default api;

