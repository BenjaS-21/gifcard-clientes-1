<template>
  <div class="stat-card fade-in" :style="{ animationDelay: delay + 'ms' }">
    <div class="stat-icon" :style="{ background: iconBg }">
      <span v-html="icon"></span>
    </div>
    <div>
      <div class="stat-value">{{ displayValue }}</div>
      <div class="stat-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: [Number, String], default: 0 },
  label: { type: String, default: '' },
  icon: { type: String, default: '&#9733;' },
  iconBg: { type: String, default: 'rgba(227,24,55,0.1)' },
  prefix: { type: String, default: '' },
  isMoney: { type: Boolean, default: false },
  delay: { type: Number, default: 0 }
})

const displayValue = computed(() => {
  if (props.isMoney) {
    return props.prefix + Number(props.value || 0).toLocaleString('es-VE', { minimumFractionDigits: 2 })
  }
  return props.prefix + (props.value ?? 0).toLocaleString('es-VE')
})
</script>
