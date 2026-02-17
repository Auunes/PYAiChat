<template>
  <div class="p-3 sm:p-6 lg:p-8">
    <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800 mb-4 sm:mb-6 lg:mb-8 pl-12 lg:pl-0">统计面板</h2>

    <div v-if="loading" class="text-center py-10 sm:py-20">
      <p class="text-sm sm:text-base text-gray-600">加载中...</p>
    </div>

    <div v-else-if="stats" class="space-y-4 sm:space-y-6 lg:space-y-8">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
          <p class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">今日调用</p>
          <p class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800">{{ stats.today_calls }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
          <p class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">本周调用</p>
          <p class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800">{{ stats.week_calls }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
          <p class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">本月调用</p>
          <p class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800">{{ stats.month_calls }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
          <p class="text-xs sm:text-sm text-gray-600 mb-1 sm:mb-2">活跃用户</p>
          <p class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800">{{ stats.active_users }}</p>
        </div>
      </div>

      <!-- Token 统计 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
        <h3 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-800 mb-3 sm:mb-4">Token 消耗统计</h3>
        <div class="grid grid-cols-3 gap-2 sm:gap-3 lg:gap-4">
          <div>
            <p class="text-xs sm:text-sm text-gray-600">提问 Tokens</p>
            <p class="text-base sm:text-xl lg:text-2xl font-bold text-gray-800">{{ stats.token_stats.prompt_tokens.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-600">回答 Tokens</p>
            <p class="text-base sm:text-xl lg:text-2xl font-bold text-gray-800">{{ stats.token_stats.completion_tokens.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs sm:text-sm text-gray-600">总计 Tokens</p>
            <p class="text-base sm:text-xl lg:text-2xl font-bold text-gray-800">{{ stats.token_stats.total_tokens.toLocaleString() }}</p>
          </div>
        </div>
      </div>

      <!-- 模型使用占比 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
        <h3 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-800 mb-3 sm:mb-4">模型使用占比</h3>
        <div class="space-y-1 sm:space-y-2">
          <div v-for="(count, model) in stats.model_distribution" :key="model" class="flex items-center justify-between text-xs sm:text-sm lg:text-base">
            <span class="text-gray-700 truncate mr-2">{{ model }}</span>
            <span class="font-semibold text-gray-800 flex-shrink-0">{{ count }} 次</span>
          </div>
        </div>
      </div>

      <!-- 调用趋势 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
        <h3 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-800 mb-3 sm:mb-4">调用趋势（最近 7 天）</h3>
        <div class="space-y-1 sm:space-y-2">
          <div v-for="item in stats.trend_data" :key="item.date" class="flex items-center justify-between text-xs sm:text-sm lg:text-base">
            <span class="text-gray-700">{{ item.date }}</span>
            <span class="font-semibold text-gray-800">{{ item.count }} 次</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { Stats } from '@/types'

const stats = ref<Stats | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await adminApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
})
</script>
