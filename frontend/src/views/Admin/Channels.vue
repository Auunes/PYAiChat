<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-bold text-gray-800">渠道管理</h2>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition"
      >
        添加渠道
      </button>
    </div>

    <div v-if="loading" class="text-center py-20">
      <p class="text-gray-600">加载中...</p>
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">模型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RPM 限制</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="channel in channels" :key="channel.id">
            <td class="px-6 py-4 text-sm text-gray-900">{{ channel.name }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ channel.model_id }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ channel.rpm_limit }}</td>
            <td class="px-6 py-4 text-sm">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  channel.is_enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                ]"
              >
                {{ channel.is_enabled ? '已启用' : '已禁用' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm space-x-2">
              <button
                @click="editChannel(channel)"
                class="text-primary-600 hover:text-primary-700 font-medium"
              >
                编辑
              </button>
              <button
                @click="deleteChannelConfirm(channel.id)"
                class="text-red-600 hover:text-red-700 font-medium"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal (simplified) -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4" @click.stop>
        <h3 class="text-xl font-semibold mb-4">{{ editingChannel ? '编辑渠道' : '添加渠道' }}</h3>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">名称</label>
            <input v-model="formData.name" required class="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
            <input v-model="formData.base_url" required class="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <div class="relative">
              <input
                v-model="formData.api_key"
                :type="showApiKey ? 'text' : 'password'"
                :placeholder="editingChannel ? '留空则不修改' : ''"
                :required="!editingChannel"
                class="w-full px-3 py-2 pr-10 border rounded-lg"
              />
              <button
                type="button"
                @click="showApiKey = !showApiKey"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <svg v-if="!showApiKey" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Model ID</label>
            <input v-model="formData.model_id" required class="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">RPM 限制</label>
            <input v-model.number="formData.rpm_limit" type="number" required class="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div class="flex items-center">
            <input v-model="formData.is_enabled" type="checkbox" class="mr-2" />
            <label class="text-sm text-gray-700">启用</label>
          </div>
          <div class="flex gap-2">
            <button type="submit" class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg">
              {{ editingChannel ? '更新' : '创建' }}
            </button>
            <button type="button" @click="showCreateModal = false" class="flex-1 px-4 py-2 border rounded-lg">
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { Channel, ChannelCreate } from '@/types'

const channels = ref<Channel[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const editingChannel = ref<Channel | null>(null)
const showApiKey = ref(false)
const formData = ref<ChannelCreate>({
  name: '',
  base_url: '',
  api_key: '',
  model_id: '',
  rpm_limit: 60,
  is_enabled: true,
})

const loadChannels = async () => {
  try {
    const response = await adminApi.getChannels()
    channels.value = response.data
  } catch (error) {
    console.error('Failed to load channels:', error)
  } finally {
    loading.value = false
  }
}

const editChannel = (channel: Channel) => {
  console.log('编辑渠道数据:', channel)
  console.log('API Key:', channel.api_key)
  editingChannel.value = channel
  formData.value = {
    name: channel.name,
    base_url: channel.base_url,
    api_key: channel.api_key,
    model_id: channel.model_id,
    rpm_limit: channel.rpm_limit,
    is_enabled: channel.is_enabled,
  }
  console.log('表单数据:', formData.value)
  showApiKey.value = false
  showCreateModal.value = true
}

const handleSubmit = async () => {
  try {
    if (editingChannel.value) {
      await adminApi.updateChannel(editingChannel.value.id, formData.value)
    } else {
      await adminApi.createChannel(formData.value)
    }
    showCreateModal.value = false
    editingChannel.value = null
    await loadChannels()
  } catch (error) {
    console.error('Failed to save channel:', error)
  }
}

const deleteChannelConfirm = async (id: number) => {
  if (confirm('确定要删除此渠道吗？')) {
    try {
      await adminApi.deleteChannel(id)
      await loadChannels()
    } catch (error) {
      console.error('Failed to delete channel:', error)
    }
  }
}

onMounted(loadChannels)
</script>
