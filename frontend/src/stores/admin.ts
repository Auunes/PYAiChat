import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useAdminStore = defineStore('admin', () => {
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const isLoggedIn = ref(!!token.value)

  const login = async (username: string, password: string) => {
    const response = await authApi.adminLogin(username, password)
    token.value = response.data.access_token
    localStorage.setItem('admin_token', token.value)
    localStorage.setItem('token', token.value) // 用于 API 请求
    isLoggedIn.value = true
  }

  const logout = () => {
    token.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('token')
    isLoggedIn.value = false
  }

  return {
    token,
    isLoggedIn,
    login,
    logout,
  }
})
