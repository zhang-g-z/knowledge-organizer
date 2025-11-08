import axios from 'axios'

const api = axios.create({
  baseURL: '/api', // 所有 API 以 /api 前缀
  timeout: 10000,
})

// Attach Authorization header if token present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api