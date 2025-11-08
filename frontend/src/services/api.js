import axios from 'axios'

const api = axios.create({
  baseURL: '/api', // 所有 API 以 /api 前缀
  timeout: 10000,
})

export default api