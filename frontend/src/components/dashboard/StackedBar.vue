<template>
  <div class="stacked">
    <div class="stacked-bar" role="img" :aria-label="ariaLabel">
      <div
        v-for="seg in visible"
        :key="seg.label"
        class="stacked-seg"
        :style="{ flexGrow: seg.value, background: seg.color }"
        :title="`${seg.label}: ${format(seg.value)} (${share(seg.value)}%)`"
      ></div>
    </div>
    <ul class="stacked-legend">
      <li v-for="seg in segments" :key="seg.label">
        <span class="swatch" :style="{ background: seg.color }"></span>
        <span class="legend-label">{{ seg.label }}</span>
        <strong>{{ format(seg.value) }}</strong>
        <span class="legend-pct">{{ share(seg.value) }}%</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/* Parte-del-todo en una barra (≤ 6 segmentos), con leyenda que lleva los valores. */
const props = defineProps({
  // [{ label, value, color }] en el orden de los slots categóricos
  segments: { type: Array, required: true },
  format: { type: Function, default: (v) => String(v) },
  ariaLabel: { type: String, default: '' }
})
const total = computed(() => props.segments.reduce((s, x) => s + x.value, 0))
const visible = computed(() => props.segments.filter(s => s.value > 0))
const share = (v) => (total.value ? Math.round((v / total.value) * 1000) / 10 : 0)
</script>

<style scoped>
.stacked-bar { display: flex; gap: 2px; height: 22px; border-radius: 4px; overflow: hidden; background: var(--viz-grid); }
.stacked-seg { min-width: 2px; }
.stacked-legend { list-style: none; margin: 14px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 10px 22px; }
.stacked-legend li { display: flex; align-items: center; gap: 7px; font-size: 0.8rem; color: var(--viz-ink-2); }
.stacked-legend strong { color: var(--viz-ink); font-weight: 600; }
.swatch { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.legend-pct { color: var(--viz-muted); }
</style>
