import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para tratamento de erros
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ============================================================================
// VEHICLES
// ============================================================================

export const vehiclesAPI = {
  list: (params = {}) => api.get('/api/vehicles', { params }),
  
  get: (id) => api.get(`/api/vehicles/${id}`),
  
  create: (data) => api.post('/api/vehicles', data),
  
  update: (id, data) => api.put(`/api/vehicles/${id}`, data),
  
  delete: (id) => api.delete(`/api/vehicles/${id}`),
}

// ============================================================================
// ALERTS
// ============================================================================

export const alertsAPI = {
  list: (params = {}) => api.get('/api/alerts', { params }),
  
  get: (id) => api.get(`/api/alerts/${id}`),
  
  stats: (params = {}) => api.get('/api/alerts/stats', { params }),
}

// ============================================================================
// REPORTS
// ============================================================================

export const reportsAPI = {
  export: (params = {}) => {
    return api.get('/api/reports/export', {
      params,
      responseType: 'blob',
    })
  },
}

export default api

