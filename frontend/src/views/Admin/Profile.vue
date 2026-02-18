<template>
  <div class="p-3 sm:p-6 lg:p-8">
    <h2 class="text-xl sm:text-2xl font-bold text-gray-800 mb-4 sm:mb-6 pl-12 lg:pl-0">个人设置</h2>

    <div class="bg-white rounded-lg shadow p-4 sm:p-6 max-w-2xl">
      <form @submit.prevent="handleSave" class="space-y-4 sm:space-y-6">
        <!-- 管理员用户名 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">管理员用户名</label>
          <input
            v-model="formData.username"
            type="text"
            class="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            placeholder="输入新用户名"
          />
        </div>

        <!-- 当前密码 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">当前密码</label>
          <input
            v-model="formData.current_password"
            type="password"
            class="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            placeholder="修改密码时需要填写"
          />
        </div>

        <!-- 新密码 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">新密码</label>
          <input
            v-model="formData.new_password"
            type="password"
            class="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            placeholder="留空则不修改密码"
          />
        </div>

        <!-- 确认新密码 -->
        <div v-if="formData.new_password">
          <label class="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            placeholder="再次输入新密码"
          />
        </div>

        <!-- 提示信息 -->
        <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>

        <div v-if="successMessage" class="p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-sm text-green-600">{{ successMessage }}</p>
        </div>

        <!-- 按钮 -->
        <div class="flex gap-3 pt-4">
          <button
            type="submit"
            :disabled="saving"
            class="px-4 sm:px-6 py-2 text-sm sm:text-base bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存更改' }}
          </button>
          <button
            type="button"
            @click="resetForm"
            class="px-4 sm:px-6 py-2 text-sm sm:text-base border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg transition"
          >
            重置
          </button>
        </div>

        <!-- 警告提示 -->
        <div class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-xs sm:text-sm text-yellow-800">
            <strong>注意：</strong>修改用户名或密码后，需要重新登录。修改密码后建议重启应用以确保完全生效。
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import { useRouter } from 'vue-router'

const router = useRouter()

const formData = ref({
  username: '',
  current_password: '',
  new_password: '',
})

const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const saving = ref(false)
const originalUsername = ref('')

const loadProfile = async () => {
  try {
    const response = await adminApi.getAdminProfile()
    formData.value.username = response.data.username
    originalUsername.value = response.data.username
  } catch (error) {
    console.error('加载个人信息失败:', error)
  }
}

const resetForm = () => {
  formData.value.username = originalUsername.value
  formData.value.current_password = ''
  formData.value.new_password = ''
  confirmPassword.value = ''
  errorMessage.value = ''
  successMessage.value = ''
}

const handleSave = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  // 验证
  if (formData.value.new_password && formData.value.new_password !== confirmPassword.value) {
    errorMessage.value = '两次输入的新密码不一致'
    return
  }

  if (formData.value.new_password && formData.value.new_password.length < 6) {
    errorMessage.value = '新密码至少需要 6 个字符'
    return
  }

  if (formData.value.new_password && !formData.value.current_password) {
    errorMessage.value = '修改密码需要提供当前密码'
    return
  }

  if (!formData.value.username || formData.value.username.length < 3) {
    errorMessage.value = '用户名至少需要 3 个字符'
    return
  }

  saving.value = true

  try {
    await adminApi.updateAdminProfile(formData.value)
    successMessage.value = '保存成功！3 秒后将跳转到登录页面...'

    // 3秒后跳转到登录页
    setTimeout(() => {
      localStorage.removeItem('admin_token')
      router.push('/admin/login')
    }, 3000)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '保存失败，请重试'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>
