<template>
  <div class="p-8">
    <h2 class="text-3xl font-bold text-gray-800 mb-8">日志查询</h2>

    <!-- 筛选器 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
          <input v-model="filters.start_date" type="date" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
          <input v-model="filters.end_date" type="date" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">IP 地址</label>
          <input v-model="filters.ip_address" type="text" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button
          @click="loadLogs"
          class="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
        >
          查询
        </button>
        <button
          @click="exportLogs"
          class="px-6 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition"
        >
          导出 CSV
        </button>
      </div>
    </div>

    <!-- 日志表格 -->
    <div v-if="loading" class="text-center py-20">
      <p class="text-gray-600">加载中...</p>
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">模型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">输入Tokens</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">输出Tokens</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="log in logs" :key="log.id">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ new Date(log.created_at).toLocaleString() }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ log.ip_address }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ log.username || '游客' }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ log.model_id }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ log.prompt_tokens || 0 }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ log.completion_tokens || 0 }}</td>
          </tr>
        </tbody>
      </table>
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
