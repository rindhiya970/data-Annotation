// src/services/api.js
// Centralized Axios instance for all API calls
import axios from 'axios'
import router from '../router'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
  withCredentials: false
  // ⚠️ CRITICAL: Do NOT set default Content-Type!
  // Let axios handle it automatically based on data type
})

// Request interceptor - Add JWT token to all requests
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // ⚠️ CRITICAL: Remove ALL Content-Type headers for FormData
    // Let browser set it automatically with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
      delete config.headers['content-type']
      if (config.headers.common) {
        delete config.headers.common['Content-Type']
        delete config.headers.common['content-type']
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle 401 errors globally
API.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default API
