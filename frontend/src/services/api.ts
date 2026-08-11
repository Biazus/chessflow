import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para lidar com erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const analyzePosition = async (fen: string, depth: number = 20) => {
  return api.post('/api/analysis/position', { fen, depth })
}

export const triggerGameAnalysis = async (gameId: number) => {
  return api.post(`/api/analysis/game/${gameId}`)
}

export const getGameAnalysis = async (gameId: number) => {
  return api.get(`/api/analysis/game/${gameId}`)
}

export default api