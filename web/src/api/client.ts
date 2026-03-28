import axios from 'axios'

export class ApiError extends Error {
  code: number

  constructor(message: string, code: number = -1) {
    super(message)
    this.name = 'ApiError'
    this.code = code
  }
}

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
})

// 请求拦截器：自动附加 JWT token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：解包 { code, message, data } 格式，统一错误处理
client.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 0) {
      return res.data
    }
    return Promise.reject(new ApiError(res.message || '请求失败', res.code))
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      return Promise.reject(new ApiError('认证已过期，请重新登录', 401))
    }

    if (!error.response) {
      return Promise.reject(new ApiError('网络异常，请检查网络连接', -1))
    }

    const msg = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new ApiError(msg, error.response?.status ?? -1))
  },
)

export default client
