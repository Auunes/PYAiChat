import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 token
api.interceptors.request.use((config) => {
  // 管理员接口使用 admin_token，其他接口使用 token
  const isAdminRoute = config.url?.startsWith('/admin/')
  const token = isAdminRoute
    ? localStorage.getItem('admin_token')
    : localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      const currentPath = window.location.pathname

      // 如果是管理员登录接口本身失败，不做任何处理，让登录页面显示错误
      if (url === '/auth/admin/login') {
        return Promise.reject(error)
      }

      // 如果是管理员区域的其他接口（需要认证的），清除token并跳转到管理员登录页
      if (url.includes('/admin') || currentPath.startsWith('/admin')) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('token')
        window.location.href = '/admin/login'
        return Promise.reject(error)
      }

      // 普通用户接口401错误：跳转到用户登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
