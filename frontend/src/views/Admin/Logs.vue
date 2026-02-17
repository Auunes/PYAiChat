<template>
  <div class="p-3 sm:p-6 lg:p-8">
    <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800 mb-4 sm:mb-6 lg:mb-8 pl-12 lg:pl-0">日志查询</h2>

    <!-- 筛选器 -->
    <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6 mb-4 sm:mb-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <div>
          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">开始日期</label>
          <input v-model="filters.start_date" type="date" class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">结束日期</label>
          <input v-model="filters.end_date" type="date" class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg" />
        </div>
        <div class="sm:col-span-2 lg:col-span-1">
          <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">IP 地址</label>
          <input v-model="filters.ip_address" type="text" class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg" />
        </div>
      </div>
      <div class="mt-3 sm:mt-4 flex flex-col sm:flex-row gap-2">
        <button
          @click="loadLogs"
          class="px-4 sm:px-6 py-2 text-sm sm:text-base bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
        >
          查询
        </button>
        <button
          @click="exportLogs"
          class="px-4 sm:px-6 py-2 text-sm sm:text-base border border-gray-300 hover:bg-gray-50 rounded-lg transition"
        >
          导出 CSV
        </button>
      </div>
    </div>

    <!-- 日志表格 -->
    <div v-if="loading" class="text-center py-10 sm:py-20">
      <p class="text-sm sm:text-base text-gray-600">加载中...</p>
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <!-- 移动端卡片视图 -->
      <div class="lg:hidden divide-y divide-gray-200">
        <div v-for="log in logs" :key="log.id" class="p-3 sm:p-4">
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">时间:</span>
              <span class="text-gray-900 font-medium">{{ new Date(log.created_at).toLocaleString() }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">IP:</span>
              <span class="text-gray-900">{{ log.ip_address }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">用户:</span>
              <span class="text-gray-900">{{ log.username || '游客' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">模型:</span>
              <span class="text-gray-900">{{ log.model_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Tokens:</span>
              <span class="text-gray-900">{{ log.prompt_tokens || 0 }} / {{ log.completion_tokens || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 桌面端表格视图 -->
      <div class="hidden lg:block overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">模型</th>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">输入Tokens</th>
              <th class="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">输出Tokens</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="log in logs" :key="log.id">
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">
                {{ new Date(log.created_at).toLocaleString() }}
              </td>
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">{{ log.ip_address }}</td>
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">{{ log.username || '游客' }}</td>
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">{{ log.model_id }}</td>
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">{{ log.prompt_tokens || 0 }}</td>
              <td class="px-4 lg:px-6 py-4 text-sm text-gray-900">{{ log.completion_tokens || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { ChatLog } from '@/types'

const logs = ref<ChatLog[]>([])
const loading = ref(true)
const filters = ref({
  start_date: '',
  end_date: '',
  ip_address: '',
})

const loadLogs = async () => {
  loading.value = true
  try {
    const response = await adminApi.getLogs(filters.value)
    logs.value = response.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

const exportLogs = async () => {
  try {
    const response = await adminApi.exportLogs(filters.value)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'chat_logs.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Failed to export logs:', error)
  }
}

onMounted(loadLogs)
</script>
