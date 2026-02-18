import api from './index'
import type {
  Channel,
  ChannelCreate,
  SystemConfig,
  BlockedIP,
  ChatLog,
  Stats,
  Announcement,
  AnnouncementCreate,
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

  testChannel(data: ChannelCreate) {
    return api.post<{ success: boolean; message: string }>('/admin/channels/test', data)
  },

  reorderChannels(channelOrders: Array<{ id: number; sort_order: number }>) {
    return api.put('/admin/channels/reorder', channelOrders)
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

  // 公告管理
  getAnnouncements() {
    return api.get<Announcement[]>('/admin/announcements')
  },

  createAnnouncement(data: AnnouncementCreate) {
    return api.post<Announcement>('/admin/announcements', data)
  },

  updateAnnouncement(id: number, data: Partial<AnnouncementCreate>) {
    return api.put<Announcement>(`/admin/announcements/${id}`, data)
  },

  deleteAnnouncement(id: number) {
    return api.delete(`/admin/announcements/${id}`)
  },

  // 管理员个人资料
  getAdminProfile() {
    return api.get<{ username: string }>('/admin/profile')
  },

  updateAdminProfile(data: {
    username?: string
    current_password?: string
    new_password?: string
  }) {
    return api.put('/admin/profile', data)
  },
}
