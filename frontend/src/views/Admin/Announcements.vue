<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">公告管理</h2>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
      >
        新建公告
      </button>
    </div>

    <!-- 公告列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">标题</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in announcements" :key="item.id">
            <td class="px-6 py-4 text-sm text-gray-900">{{ item.title }}</td>
            <td class="px-6 py-4 text-sm">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs',
                  item.is_enabled
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800',
                ]"
              >
                {{ item.is_enabled ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ new Date(item.created_at).toLocaleString() }}
            </td>
            <td class="px-6 py-4 text-sm space-x-2">
              <button
                @click="openEditModal(item)"
                class="text-primary-600 hover:text-primary-900"
              >
                编辑
              </button>
              <button
                @click="handleDelete(item.id)"
                class="text-red-600 hover:text-red-900"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 编辑/创建弹窗 -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4" @click.stop>
        <h3 class="text-lg font-semibold text-gray-800 mb-4">
          {{ editingId ? '编辑公告' : '新建公告' }}
        </h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标题</label>
            <input
              v-model="formData.title"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
              placeholder="输入公告标题"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">内容</label>
            <textarea
              v-model="formData.content"
              rows="8"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
              placeholder="输入公告内容"
            ></textarea>
          </div>

          <div class="flex items-center">
            <input
              v-model="formData.is_enabled"
              type="checkbox"
              id="is_enabled"
              class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label for="is_enabled" class="ml-2 text-sm text-gray-700">启用公告</label>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="showModal = false"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            取消
          </button>
          <button
            @click="handleSave"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { Announcement, AnnouncementCreate } from '@/types'

const announcements = ref<Announcement[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const formData = ref<AnnouncementCreate>({
  title: '',
  content: '',
  is_enabled: true,
})

const loadAnnouncements = async () => {
  try {
    const response = await adminApi.getAnnouncements()
    announcements.value = response.data
  } catch (error) {
    console.error('加载公告失败:', error)
  }
}

const openCreateModal = () => {
  editingId.value = null
  formData.value = {
    title: '',
    content: '',
    is_enabled: true,
  }
  showModal.value = true
}

const openEditModal = (item: Announcement) => {
  editingId.value = item.id
  formData.value = {
    title: item.title,
    content: item.content,
    is_enabled: item.is_enabled,
  }
  showModal.value = true
}

const handleSave = async () => {
  try {
    if (editingId.value) {
      await adminApi.updateAnnouncement(editingId.value, formData.value)
    } else {
      await adminApi.createAnnouncement(formData.value)
    }
    showModal.value = false
    await loadAnnouncements()
  } catch (error) {
    console.error('保存公告失败:', error)
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('确定要删除这条公告吗？')) return

  try {
    await adminApi.deleteAnnouncement(id)
    await loadAnnouncements()
  } catch (error) {
    console.error('删除公告失败:', error)
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>
