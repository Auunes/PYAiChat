import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoggedIn = ref(!!token.value)

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    isLoggedIn.value = true
  }

  const register = async (email: string, password: string) => {
    await authApi.register(email, password)
  }

  const logout = () => {
    token.value = null
    localStorage.removeItem('token')
    isLoggedIn.value = false
  }

  return {
    token,
    isLoggedIn,
    login,
    register,
    logout,
  }
})
