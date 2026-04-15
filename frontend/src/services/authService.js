// src/services/authService.js
import API from './api'

export const authService = {
  /**
   * Register a new user
   * POST /api/auth/signup
   */
  async register(data) {
    try {
      const response = await API.post('/auth/signup', data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Login user
   * POST /api/auth/login
   */
  async login(data) {
    try {
      const response = await API.post('/auth/login', data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Logout user
   * POST /api/auth/logout
   */
  async logout() {
    try {
      const response = await API.post('/auth/logout')
      return response.data
    } catch (error) {
      throw error
    }
  },

  /**
   * Get current user
   * GET /api/auth/me
   */
  async getCurrentUser() {
    try {
      const response = await API.get('/auth/me')
      return response.data
    } catch (error) {
      throw error
    }
  }
}