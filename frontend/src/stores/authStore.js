// src/stores/authStore.js
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authService } from '../services/authService'

/**
 * Decode a JWT token payload without a library.
 * Returns null if the token is invalid or expired.
 */
function decodeToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    // Check expiry if present
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      return null
    }
    return payload
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  // ─── State ────────────────────────────────────────────────────────────────
  const token = ref(null)
  const user  = ref(null)   // { id, email, name }
  const loading = ref(false)
  const error   = ref(null)

  // ─── Getters ──────────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!token.value)

  // ─── Helpers ──────────────────────────────────────────────────────────────
  function hydrateUserFromToken(rawToken) {
    const payload = decodeToken(rawToken)
    if (!payload) return false

    // Flask-JWT-Extended stores user ID as string in 'sub'
    // Example payload: { sub: "123", exp: 1234567890, ... }
    const userId = payload.sub

    user.value = {
      id: userId,
      email: payload.email || null,
      name: payload.name || null,
    }
    return true
  }

  // ─── Actions ──────────────────────────────────────────────────────────────
  async function login(credentials) {
    loading.value = true
    error.value   = null
    try {
      const response = await authService.login(credentials)
      
      // Backend returns: { success, message, data: { access_token, user } }
      if (!response.success || !response.data) {
        throw new Error(response.message || 'Login failed')
      }

      const rawToken = response.data.access_token
      const userData = response.data.user

      token.value = rawToken
      localStorage.setItem('token', rawToken)

      // Use user data from backend response (most reliable)
      if (userData) {
        user.value = userData
      } else {
        // Fallback: try to decode from token
        hydrateUserFromToken(rawToken)
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Login failed. Please check your credentials.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(data) {
    loading.value = true
    error.value   = null
    try {
      const response = await authService.register(data)

      // Backend returns: { success, message, data: { user } }
      // Note: Signup doesn't return a token, user must login after
      if (!response.success) {
        throw new Error(response.message || 'Registration failed')
      }

      return response
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Registration failed. Please try again.'
      throw err
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value  = null
    error.value = null
    localStorage.removeItem('token')
  }

  /**
   * Called once in main.js on app boot.
   * Restores session from localStorage so page refreshes don't log the user out.
   */
  function initializeAuth() {
    const storedToken = localStorage.getItem('token')
    if (!storedToken) return

    const valid = hydrateUserFromToken(storedToken)
    if (valid) {
      token.value = storedToken
    } else {
      // Token expired – clean up silently
      localStorage.removeItem('token')
    }
  }

  return {
    // state
    token,
    user,
    loading,
    error,
    // getters
    isAuthenticated,
    // actions
    login,
    register,
    logout,
    initializeAuth,
  }
})