import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api/chat'
import type { ChatMessage, ModelInfo } from '@/types'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const models = ref<ModelInfo[]>([])
  const selectedModel = ref<string>('')
  const isStreaming = ref(false)
  const systemPrompt = ref<string>('')

  const loadModels = async () => {
    const response = await chatApi.getModels()
    models.value = response.data
    if (models.value.length > 0 && !selectedModel.value) {
      selectedModel.value = models.value[0].id
    }
  }

  const sendMessage = async (content: string) => {
    messages.value.push({ role: 'user', content })
    isStreaming.value = true

    const assistantMessageIndex = messages.value.length
    messages.value.push({ role: 'assistant', content: '', reasoning: '' })

    try {
      // 构建消息列表，如果有系统提示词则添加到开头
      const messagesToSend: ChatMessage[] = []
      if (systemPrompt.value.trim()) {
        console.log('添加系统提示词:', systemPrompt.value)
        messagesToSend.push({ role: 'system', content: systemPrompt.value })
      }
      messagesToSend.push(...messages.value.slice(0, -1))

      console.log('发送的消息列表:', messagesToSend)

      const stream = chatApi.streamChatCompletion({
        model: selectedModel.value,
        messages: messagesToSend,
        stream: true,
      })

      for await (const chunk of stream) {
        if (chunk.error) {
          // 根据错误类型显示不同的消息
          if (chunk.error.type === 'upstream_rate_limit') {
            messages.value[assistantMessageIndex].content = '问的人太多啦，换一个模型试试吧'
          } else {
            messages.value[assistantMessageIndex].content = chunk.error.message
          }
          return
        }

        if (chunk.choices && chunk.choices[0]?.delta) {
          const delta = chunk.choices[0].delta

          // 处理思考内容（reasoning models like o1）
          if (delta.reasoning_content) {
            if (!messages.value[assistantMessageIndex].reasoning) {
              messages.value[assistantMessageIndex].reasoning = ''
            }
            messages.value[assistantMessageIndex].reasoning += delta.reasoning_content
          }

          // 处理回复内容
          if (delta.content) {
            messages.value[assistantMessageIndex].content += delta.content
          }
        }
      }
    } catch (error: any) {
      // 处理 HTTP 429 错误（用户限流）
      if (error.status === 429 && error.errorType === 'user_rate_limit') {
        messages.value[assistantMessageIndex].content = '提问速度太快啦～请休息一下，稍后再尝试。'
      }
      // 处理其他 429 错误
      else if (error.status === 429) {
        messages.value[assistantMessageIndex].content = error.message || '请求过于频繁，请稍后再试'
      }
      // 处理其他错误
      else {
        messages.value[assistantMessageIndex].content = error.message || '发送消息失败，请稍后重试'
      }
    } finally {
      isStreaming.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  const setSystemPrompt = (prompt: string) => {
    systemPrompt.value = prompt
  }

  return {
    messages,
    models,
    selectedModel,
    isStreaming,
    systemPrompt,
    loadModels,
    sendMessage,
    clearMessages,
    setSystemPrompt,
  }
})
