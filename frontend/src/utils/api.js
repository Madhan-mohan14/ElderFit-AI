import axios from 'axios'

// Get API base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
// Increased timeout for plan generation which can take longer
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '60000', 10) // 60 seconds

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens, etc.
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
    }
    return response
  },
  (error) => {
    // Enhanced error handling
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      if (status === 404) {
        error.backendNotRunning = true
        error.message = 'API endpoint not found. Please ensure the backend server is running.'
      } else if (status === 500) {
        error.message = data?.message || 'Internal server error. Please try again later.'
      } else if (status === 422) {
        error.message = data?.message || 'Validation error. Please check your input.'
      } else if (status === 400) {
        error.message = data?.detail || data?.message || 'Bad request. Please check your input.'
      }
      
      if (import.meta.env.DEV) {
        console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${status}:`, data)
      }
    } else if (error.request) {
      // Request made but no response
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        error.backendNotRunning = true
        error.message = 'Backend server is not running. Please start it on http://localhost:8000'
      } else if (error.code === 'ECONNABORTED') {
        error.message = 'Request timeout. Please try again.'
      } else {
        error.message = 'Network error. Please check your connection.'
      }
    } else {
      // Something else happened
      error.message = error.message || 'An unexpected error occurred.'
    }
    
    return Promise.reject(error)
  }
)

// Health check function
export const checkBackendHealth = async () => {
  try {
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    const response = await axios.get(`${backendUrl}/health`, {
      timeout: 3000,
    })
    return {
      healthy: response.status === 200,
      data: response.data
    }
  } catch (error) {
    return {
      healthy: false,
      error: error.message
    }
  }
}

export default api

