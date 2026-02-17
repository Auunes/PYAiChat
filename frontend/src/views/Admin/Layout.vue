<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 text-white flex flex-col">
      <div class="p-6 border-b border-gray-800">
        <h1 class="text-xl font-bold">AI Chat 管理</h1>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <router-link
          to="/admin/dashboard"
          class="block px-4 py-3 rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
        >
          📊 统计面板
        </router-link>
        <router-link
          to="/admin/channels"
          class="block px-4 py-3 rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
        >
          🔌 渠道管理
        </router-link>
        <router-link
          to="/admin/logs"
          class="block px-4 py-3 rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
        >
          📝 日志查询
        </router-link>
        <router-link
          to="/admin/settings"
          class="block px-4 py-3 rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
        >
          ⚙️ 系统设置
        </router-link>
      </nav>

      <div class="p-4 border-t border-gray-800">
        <button
          @click="handleLogout"
          class="w-full px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg transition"
        >
          退出登录
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const adminStore = useAdminStore()

const handleLogout = () => {
  adminStore.logout()
  router.push('/admin/login')
}
</script>
