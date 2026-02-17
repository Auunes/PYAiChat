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
          <div
            v-if="message.role === 'user'"
            class="whitespace-pre-wrap"
          >
            {{ message.content }}
          </div>
          <div v-else>
            <div
              class="markdown-body prose prose-sm max-w-none"
              v-html="renderMarkdown(message.content)"
            ></div>
            <ThinkingPanel :reasoning="message.reasoning" />
          </div>
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
          type="button"
          @click="openPromptModal"
          :disabled="chatStore.isStreaming"
          class="px-6 py-3 border border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold rounded-lg transition disabled:opacity-50"
        >
          提示词
        </button>
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

    <!-- Prompt Modal -->
    <div
      v-if="showPromptModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showPromptModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4" @click.stop>
        <h3 class="text-lg font-semibold text-gray-800 mb-4">系统提示词设置</h3>
        <p class="text-sm text-gray-600 mb-4">
          系统提示词会在每次对话时自动添加到消息开头，用于设定 AI 的角色、行为和回复风格。
        </p>

        <!-- 预设提示词 -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">快速选择预设</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="preset in promptPresets"
              :key="preset.name"
              @click="tempPrompt = preset.content"
              class="px-4 py-2 text-sm text-left border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              <div class="font-medium text-gray-800">{{ preset.name }}</div>
              <div class="text-xs text-gray-500 truncate">{{ preset.description }}</div>
            </button>
          </div>
        </div>

        <!-- 自定义提示词 -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">自定义提示词</label>
          <textarea
            v-model="tempPrompt"
            rows="6"
            placeholder="输入自定义系统提示词..."
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition resize-none"
          ></textarea>
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="tempPrompt = ''"
            class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            清空
          </button>
          <button
            @click="showPromptModal = false"
            class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            取消
          </button>
          <button
            @click="savePrompt"
            class="px-4 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition"
          >
            保存
          </button>
        </div>
      </div>
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

    <!-- Success Toast -->
    <div
      v-if="successMessage"
      class="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in"
    >
      {{ successMessage }}
    </div>

    <!-- Announcement Modal -->
    <div
      v-if="showAnnouncementModal && announcement"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showAnnouncementModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" @click.stop>
        <h3 class="text-xl font-semibold text-gray-800 mb-4">{{ announcement.title }}</h3>
        <div
          class="markdown-body prose prose-sm max-w-none text-gray-700 mb-6"
          v-html="renderMarkdown(announcement.content)"
        ></div>
        <button
          @click="showAnnouncementModal = false"
          class="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
        >
          我知道了
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
import { chatApi } from '@/api/chat'
import { marked } from 'marked'
import hljs from 'highlight.js'
import ThinkingPanel from '@/components/ThinkingPanel.vue'

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const router = useRouter()
const chatStore = useChatStore()
const userStore = useUserStore()

const inputMessage = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const showPromptModal = ref(false)
const tempPrompt = ref('')
const showAnnouncementModal = ref(false)
const announcement = ref<any>(null)

// 预设提示词
const promptPresets = [
  {
    name: '默认助手',
    description: '友好、专业的 AI 助手',
    content: '你是一个友好、专业的 AI 助手，请用简洁、准确的语言回答用户的问题。',
  },
  {
    name: '编程专家',
    description: '精通各种编程语言',
    content: '你是一位经验丰富的编程专家，精通多种编程语言和框架。请提供清晰的代码示例和详细的技术解释。',
  },
  {
    name: '写作助手',
    description: '帮助改进文字表达',
    content: '你是一位专业的写作助手，擅长文字润色、语法纠正和内容优化。请帮助用户改进文字表达。',
  },
  {
    name: '翻译专家',
    description: '准确翻译多种语言',
    content: '你是一位专业的翻译专家，能够准确翻译多种语言。请保持原文的语气和风格，提供自然流畅的翻译。',
  },
  {
    name: '数学导师',
    description: '解答数学问题',
    content: '你是一位耐心的数学导师，擅长用简单易懂的方式解释数学概念和解题步骤。',
  },
  {
    name: '创意顾问',
    description: '提供创意和灵感',
    content: '你是一位富有创意的顾问，善于从不同角度思考问题，提供新颖的想法和解决方案。',
  },
]

const renderMarkdown = (content: string) => {
  if (!content) return ''
  return marked(content)
}

const savePrompt = () => {
  console.log('保存提示词:', tempPrompt.value)
  chatStore.setSystemPrompt(tempPrompt.value)
  console.log('当前 systemPrompt:', chatStore.systemPrompt)
  showPromptModal.value = false
  successMessage.value = '提示词设置成功'
  setTimeout(() => {
    successMessage.value = ''
  }, 2000)
}

const openPromptModal = () => {
  tempPrompt.value = chatStore.systemPrompt
  showPromptModal.value = true
}

onMounted(async () => {
  try {
    await chatStore.loadModels()
    tempPrompt.value = chatStore.systemPrompt
  } catch (error: any) {
    errorMessage.value = '加载模型列表失败'
  }

  // 加载公告（独立处理，失败不影响主功能）
  try {
    const response = await chatApi.getAnnouncement()
    if (response.data) {
      announcement.value = response.data
      showAnnouncementModal.value = true
    }
  } catch (error: any) {
    // 公告加载失败不显示错误，静默处理
    console.log('加载公告失败:', error)
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

// 监听消息内容变化，确保流式输出时也能滚动
watch(
  () => chatStore.messages.map(m => m.content).join(''),
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
