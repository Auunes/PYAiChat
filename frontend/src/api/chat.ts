import api from './index'
import type { ModelInfo, ChatCompletionRequest, Announcement } from '@/types'

export const chatApi = {
  getModels() {
    return api.get<ModelInfo[]>('/chat/models')
  },

  getAnnouncement() {
    return api.get<Announcement | null>('/chat/announcement')
  },

  async *streamChatCompletion(request: ChatCompletionRequest) {
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch('/api/chat/completions', {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      // 处理 429 错误，解析错误详情
      if (response.status === 429) {
        try {
          const errorData = await response.json()
          const error: any = new Error(errorData.detail?.error?.message || '请求过于频繁')
          error.status = 429
          error.errorType = errorData.detail?.error?.type || 'rate_limit'
          throw error
        } catch (e: any) {
          if (e.status === 429) throw e
          // JSON 解析失败，抛出通用错误
          const error: any = new Error('请求过于频繁')
          error.status = 429
          throw error
        }
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('No response body')
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            return
          }
          try {
            yield JSON.parse(data)
          } catch (e) {
            console.error('Failed to parse SSE data:', data)
          }
        }
      }
    }
  },
}
