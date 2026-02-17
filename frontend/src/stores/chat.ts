import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api/chat'
import type { ChatMessage, ModelInfo } from '@/types'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const models = ref<ModelInfo[]>([])
  const selectedModel = ref<string>('')
  const isStreaming = ref(false)

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
    messages.value.push({ role: 'assistant', content: '' })

    try {
      const stream = chatApi.streamChatCompletion({
        model: selectedModel.value,
        messages: messages.value.slice(0, -1),
        stream: true,
      })

      for await (const chunk of stream) {
        if (chunk.error) {
          throw new Error(chunk.error.message)
        }

        if (chunk.choices && chunk.choices[0]?.delta?.content) {
          // 使用索引直接更新，确保响应式
          messages.value[assistantMessageIndex].content += chunk.choices[0].delta.content
        }
      }
    } catch (error: any) {
      messages.value[assistantMessageIndex].content = `错误: ${error.message}`
    } finally {
      isStreaming.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    models,
    selectedModel,
    isStreaming,
    loadModels,
    sendMessage,
    clearMessages,
  }
})
