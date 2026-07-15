<template>
  <span class="badge" :class="badgeClass">
    <span class="badge-dot" v-if="showDot"></span>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'activa' },
  showDot: { type: Boolean, default: true }
})

const statusMap = {
  activa: { class: 'badge-success', label: 'Activa' },
  vencida: { class: 'badge-warning', label: 'Vencida' },
  agotada: { class: 'badge-muted', label: 'Agotada' },
  bloqueada: { class: 'badge-danger', label: 'Bloqueada' },
  compra: { class: 'badge-danger', label: 'Compra' },
  recarga: { class: 'badge-success', label: 'Recarga' },
}

const badgeClass = computed(() => statusMap[props.status]?.class || 'badge-muted')
const label = computed(() => statusMap[props.status]?.label || props.status)
</script>

<style scoped>
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
</style>
