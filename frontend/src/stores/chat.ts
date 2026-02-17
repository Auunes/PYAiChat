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
          throw new Error(chunk.error.message)
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
      messages.value[assistantMessageIndex].content = `错误: ${error.message}`
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
