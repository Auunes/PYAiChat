<template>
  <div class="p-3 sm:p-6 lg:p-8">
    <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-800 mb-4 sm:mb-6 lg:mb-8 pl-12 lg:pl-0">系统设置</h2>

    <div class="space-y-4 sm:space-y-6">
      <!-- 限流配置 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
        <h3 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-800 mb-3 sm:mb-4">限流配置</h3>
        <form @submit.prevent="saveConfig" class="space-y-3 sm:space-y-4">
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
              游客 RPM 限制
            </label>
            <input
              v-model.number="config.guest_rpm"
              type="number"
              min="1"
              required
              class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
              已登录用户 RPM 限制
            </label>
            <input
              v-model.number="config.user_rpm"
              type="number"
              min="1"
              required
              class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg"
            />
          </div>
          <div>
            <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
              日志保留天数
            </label>
            <input
              v-model.number="config.log_retention_days"
              type="number"
              min="1"
              required
              class="w-full px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg"
            />
          </div>
          <div class="flex items-center justify-between">
            <div>
              <label class="block text-xs sm:text-sm font-medium text-gray-700 mb-1">
                允许用户注册
              </label>
              <p class="text-xs text-gray-500">关闭后新用户将无法注册账号</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="config.allow_registration"
                type="checkbox"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          <button
            type="submit"
            class="w-full sm:w-auto px-4 sm:px-6 py-1.5 sm:py-2 text-sm sm:text-base bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
          >
            保存配置
          </button>
        </form>
      </div>

      <!-- IP 黑名单 -->
      <div class="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
        <h3 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-800 mb-3 sm:mb-4">IP 黑名单</h3>
        <div class="flex flex-col sm:flex-row gap-2 mb-3 sm:mb-4">
          <input
            v-model="newIP"
            type="text"
            placeholder="IP 地址或 CIDR (如 192.168.1.0/24)"
            class="flex-1 px-2 sm:px-3 py-1.5 sm:py-2 text-sm border rounded-lg"
          />
          <button
            @click="addBlockedIP"
            class="px-4 sm:px-6 py-1.5 sm:py-2 text-sm sm:text-base bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
          >
            添加
          </button>
        </div>
        <div class="space-y-2">
          <div
            v-for="ip in blockedIPs"
            :key="ip.id"
            class="flex items-center justify-between p-2 sm:p-3 border rounded-lg"
          >
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-800 text-sm sm:text-base truncate">{{ ip.ip_address }}</p>
              <p v-if="ip.reason" class="text-xs sm:text-sm text-gray-600 truncate">{{ ip.reason }}</p>
            </div>
            <button
              @click="deleteBlockedIP(ip.id)"
              class="text-red-600 hover:text-red-700 font-medium text-xs sm:text-sm ml-2 flex-shrink-0"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { SystemConfig, BlockedIP } from '@/types'

const config = ref<SystemConfig>({
  guest_rpm: 10,
  user_rpm: 60,
  log_retention_days: 90,
  allow_registration: true,
})

const blockedIPs = ref<BlockedIP[]>([])
const newIP = ref('')

const loadConfig = async () => {
  try {
    const response = await adminApi.getConfig()
    config.value = response.data
  } catch (error) {
    console.error('Failed to load config:', error)
  }
}

const saveConfig = async () => {
  try {
    await adminApi.updateConfig(config.value)
    alert('配置已保存')
  } catch (error) {
    console.error('Failed to save config:', error)
  }
}

const loadBlockedIPs = async () => {
  try {
    const response = await adminApi.getBlockedIPs()
    blockedIPs.value = response.data
  } catch (error) {
    console.error('Failed to load blocked IPs:', error)
  }
}

const addBlockedIP = async () => {
  if (!newIP.value.trim()) return
  try {
    await adminApi.createBlockedIP(newIP.value)
    newIP.value = ''
    await loadBlockedIPs()
  } catch (error) {
    console.error('Failed to add blocked IP:', error)
  }
}

const deleteBlockedIP = async (id: number) => {
  try {
    await adminApi.deleteBlockedIP(id)
    await loadBlockedIPs()
  } catch (error) {
    console.error('Failed to delete blocked IP:', error)
  }
}

onMounted(() => {
  loadConfig()
  loadBlockedIPs()
})
</script>
