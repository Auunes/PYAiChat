import api from './index'
import type { ModelInfo, ChatCompletionRequest } from '@/types'

export const chatApi = {
  getModels() {
    return api.get<ModelInfo[]>('/chat/models')
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
