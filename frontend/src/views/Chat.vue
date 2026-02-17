<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">AI Chat</h1>
      <div class="flex items-center gap-4">
        <select
          v-model="chatStore.selectedModel"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
        >
          <option v-for="model in chatStore.models" :key="model.id" :value="model.id">
            {{ model.name }}
          </option>
        </select>

        <div v-if="userStore.isLoggedIn" class="flex items-center gap-2">
          <span class="text-sm text-gray-600">已登录</span>
          <button
            @click="handleLogout"
            class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            退出
          </button>
        </div>
        <router-link
          v-else
          to="/login"
          class="px-4 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition"
        >
          登录
        </router-link>
      </div>
    </header>

    <!-- Chat Messages -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      <div v-if="chatStore.messages.length === 0" class="text-center text-gray-500 mt-20">
        <p class="text-lg">开始与 AI 对话吧！</p>
      </div>

      <div
        v-for="(message, index) in chatStore.messages"
        :key="index"
        :class="[
          'flex',
          message.role === 'user' ? 'justify-end' : 'justify-start',
        ]"
      >
        <div
          :class="[
            'max-w-3xl px-6 py-4 rounded-2xl',
            message.role === 'user'
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-gray-200 text-gray-800',
          ]"
        >
          <div class="whitespace-pre-wrap">{{ message.content }}</div>
        </div>
      </div>

      <div v-if="chatStore.isStreaming" class="flex justify-start">
        <div class="bg-white border border-gray-200 px-6 py-4 rounded-2xl">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="bg-white border-t border-gray-200 px-6 py-4">
      <form @submit.prevent="handleSend" class="flex gap-4">
        <input
          v-model="inputMessage"
          type="text"
          :disabled="chatStore.isStreaming"
          placeholder="输入消息..."
          class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition disabled:opacity-50"
        />
        <button
          type="submit"
          :disabled="!inputMessage.trim() || chatStore.isStreaming"
          class="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
        >
          发送
        </button>
        <button
          type="button"
          @click="chatStore.clearMessages"
          :disabled="chatStore.isStreaming"
          class="px-6 py-3 border border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold rounded-lg transition disabled:opacity-50"
        >
          清空
        </button>
      </form>
    </div>

    <!-- Error Modal -->
    <div
      v-if="errorMessage"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="errorMessage = ''"
    >
      <div class="bg-white rounded-lg p-6 max-w-md mx-4" @click.stop>
        <h3 class="text-lg font-semibold text-red-600 mb-2">错误</h3>
        <p class="text-gray-700">{{ errorMessage }}</p>
        <button
          @click="errorMessage = ''"
          class="mt-4 w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const chatStore = useChatStore()
const userStore = useUserStore()

const inputMessage = ref('')
const errorMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  try {
    await chatStore.loadModels()
  } catch (error: any) {
    errorMessage.value = '加载模型列表失败'
  }
})

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value
  inputMessage.value = ''

  try {
    await chatStore.sendMessage(message)
  } catch (error: any) {
    if (error.response?.status === 429) {
      const detail = error.response.data.detail
      errorMessage.value = detail.error?.message || '请求过于频繁，请稍后再试'
    } else {
      errorMessage.value = '发送消息失败，请稍后重试'
    }
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>
