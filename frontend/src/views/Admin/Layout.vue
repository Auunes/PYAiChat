<template>
  <div class="flex bg-gray-100" style="min-height: 100dvh; height: 100dvh;">
    <!-- Mobile Menu Button -->
    <button
      @click="showMobileMenu = !showMobileMenu"
      class="fixed top-3 left-3 z-50 lg:hidden p-2 bg-gray-900 text-white rounded-lg"
    >
      <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Overlay for mobile -->
    <div
      v-if="showMobileMenu"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      @click="showMobileMenu = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-gray-900 text-white flex flex-col transition-transform duration-300 z-40',
        'fixed lg:static inset-y-0 left-0',
        'w-64',
        showMobileMenu ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <div class="p-4 sm:p-6 border-b border-gray-800">
        <h1 class="text-lg sm:text-xl font-bold pl-12 lg:pl-0">AI Chat 管理</h1>
      </div>

      <nav class="flex-1 p-3 sm:p-4 space-y-1 sm:space-y-2 overflow-y-auto">
        <router-link
          to="/admin/dashboard"
          class="block px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
          @click="showMobileMenu = false"
        >
          📊 统计面板
        </router-link>
        <router-link
          to="/admin/channels"
          class="block px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
          @click="showMobileMenu = false"
        >
          🔌 渠道管理
        </router-link>
        <router-link
          to="/admin/logs"
          class="block px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
          @click="showMobileMenu = false"
        >
          📝 日志查询
        </router-link>
        <router-link
          to="/admin/settings"
          class="block px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
          @click="showMobileMenu = false"
        >
          ⚙️ 系统设置
        </router-link>
        <router-link
          to="/admin/announcements"
          class="block px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-lg hover:bg-gray-800 transition"
          active-class="bg-gray-800"
          @click="showMobileMenu = false"
        >
          📢 公告管理
        </router-link>
      </nav>

      <div class="p-3 sm:p-4 border-t border-gray-800">
        <button
          @click="handleLogout"
          class="w-full px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base bg-red-600 hover:bg-red-700 rounded-lg transition"
        >
          退出登录
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto min-h-0 w-full lg:w-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const adminStore = useAdminStore()
const showMobileMenu = ref(false)

const handleLogout = () => {
  adminStore.logout()
  router.push('/admin/login')
}
</script>
