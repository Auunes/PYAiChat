export interface User {
  id: number
  email: string
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Channel {
  id: number
  name: string
  base_url: string
  api_key: string
  model_id: string
  rpm_limit: number
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface ChannelCreate {
  name: string
  base_url: string
  api_key: string
  model_id: string
  rpm_limit: number
  is_enabled: boolean
}

export interface ModelInfo {
  id: string
  name: string
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatCompletionRequest {
  model: string
  messages: ChatMessage[]
  stream: boolean
  temperature?: number
  max_tokens?: number
}

export interface SystemConfig {
  guest_rpm: number
  user_rpm: number
  log_retention_days: number
}

export interface BlockedIP {
  id: number
  ip_address: string
  reason?: string
  created_at: string
}

export interface ChatLog {
  id: number
  user_id?: number
  username?: string
  ip_address: string
  channel_id?: number
  model_id: string
  prompt_tokens?: number
  completion_tokens?: number
  created_at: string
}

export interface Stats {
  today_calls: number
  week_calls: number
  month_calls: number
  model_distribution: Record<string, number>
  trend_data: Array<{ date: string; count: number }>
  token_stats: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  active_users: number
}

export interface ErrorResponse {
  error: {
    type: string
    message: string
    retry_after?: number
  }
}

export interface Announcement {
  id: number
  title: string
  content: string
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface AnnouncementCreate {
  title: string
  content: string
  is_enabled: boolean
}
