<template>
  <div
    v-if="reasoning"
    class="mt-3 border-t border-gray-200 pt-3"
  >
    <button
      @click="isExpanded = !isExpanded"
      class="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition"
    >
      <svg
        :class="['w-4 h-4 transition-transform', isExpanded ? 'rotate-90' : '']"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
      <span class="font-medium">思考过程</span>
      <span v-if="!isExpanded" class="text-xs text-gray-400">
        ({{ reasoning.length }} 字符)
      </span>
    </button>

    <div
      v-if="isExpanded"
      class="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200"
    >
      <div class="text-sm text-gray-700 whitespace-pre-wrap font-mono">
        {{ reasoning }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  reasoning?: string
}

const props = defineProps<Props>()
const isExpanded = ref(false)
</script>
