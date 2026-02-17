import api from './index'
import type {
  Channel,
  ChannelCreate,
  SystemConfig,
  BlockedIP,
  ChatLog,
  Stats,
} from '@/types'

export const adminApi = {
  // 渠道管理
  getChannels() {
    return api.get<Channel[]>('/admin/channels')
  },

  createChannel(data: ChannelCreate) {
    return api.post<Channel>('/admin/channels', data)
  },

  updateChannel(id: number, data: Partial<ChannelCreate>) {
    return api.put<Channel>(`/admin/channels/${id}`, data)
  },

  deleteChannel(id: number) {
    return api.delete(`/admin/channels/${id}`)
  },

  // 系统配置
  getConfig() {
    return api.get<SystemConfig>('/admin/config')
  },

  updateConfig(data: Partial<SystemConfig>) {
    return api.put<SystemConfig>('/admin/config', data)
  },

  // IP 管理
  getBlockedIPs() {
    return api.get<BlockedIP[]>('/admin/blocked-ips')
  },

  createBlockedIP(ip_address: string, reason?: string) {
    return api.post<BlockedIP>('/admin/blocked-ips', { ip_address, reason })
  },

  deleteBlockedIP(id: number) {
    return api.delete(`/admin/blocked-ips/${id}`)
  },

  // 日志查询
  getLogs(params?: {
    start_date?: string
    end_date?: string
    username?: string
    ip_address?: string
    model_id?: string
    limit?: number
    offset?: number
  }) {
    return api.get<ChatLog[]>('/admin/logs', { params })
  },

  exportLogs(params?: { start_date?: string; end_date?: string }) {
    return api.get('/admin/logs/export', {
      params,
      responseType: 'blob',
    })
  },

  // 统计数据
  getStats() {
    return api.get<Stats>('/admin/stats')
  },
}
