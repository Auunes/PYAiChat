import api from './index'
import type { Token } from '@/types'

export const authApi = {
  register(email: string, password: string) {
    return api.post('/auth/register', { email, password })
  },

  login(email: string, password: string) {
    return api.post<Token>('/auth/login', { email, password })
  },

  adminLogin(username: string, password: string) {
    return api.post<Token>('/auth/admin/login', { username, password })
  },
}
