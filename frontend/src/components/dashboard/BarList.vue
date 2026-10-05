<template>
  <ol class="bar-list">
    <li
      v-for="(item, i) in items"
      :key="item.key || item.label"
      class="bar-row"
      tabindex="0"
      @mouseenter="active = i" @mouseleave="active = null" @focus="active = i" @blur="active = null"
    >
      <div class="bar-head">
        <span class="bar-rank">{{ i + 1 }}</span>
        <span class="bar-label" :title="item.label">{{ item.label }}</span>
        <span class="bar-value">{{ format(item.value) }}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" :class="{ dim: active !== null && active !== i }" :style="{ width: pct(item.value) + '%' }"></div>
      </div>
      <div v-if="item.sub" class="bar-sub">{{ item.sub }}</div>
    </li>
    <li v-if="!items.length" class="bar-empty">Sin datos para este filtro.</li>
  </ol>
</template>

<script setup>
import { ref, computed } from 'vue'

/* Ranking en barras horizontales de una sola serie, con el valor en la punta. */
const props = defineProps({
  // [{ key, label, value, sub }]
  items: { type: Array, required: true },
  format: { type: Function, default: (v) => String(v) },
  max: { type: Number, default: null } // fijo (ej. 100 para porcentajes); si no, el mayor valor
})
const active = ref(null)
const scaleMax = computed(() => props.max ?? Math.max(...props.items.map(i => i.value), 0))
const pct = (v) => (scaleMax.value > 0 ? Math.max((v / scaleMax.value) * 100, v > 0 ? 1 : 0) : 0)
</script>

<style scoped>
.bar-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.bar-row { outline: none; border-radius: 6px; }
.bar-row:focus-visible { box-shadow: 0 0 0 2px var(--viz-grid); }
.bar-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 5px; }
.bar-rank { width: 18px; flex-shrink: 0; font-size: 0.72rem; color: var(--viz-muted); font-variant-numeric: tabular-nums; }
.bar-label { flex: 1; min-width: 0; font-size: 0.82rem; color: var(--viz-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-value { font-size: 0.82rem; font-weight: 600; color: var(--viz-ink); font-variant-numeric: tabular-nums; white-space: nowrap; }
.bar-track { margin-left: 26px; height: 10px; }
.bar-fill { height: 100%; background: var(--viz-series-1); border-radius: 0 4px 4px 0; transition: opacity 0.15s, width 0.4s ease; }
.bar-fill.dim { opacity: 0.45; }
.bar-sub { margin: 4px 0 0 26px; font-size: 0.72rem; color: var(--viz-ink-2); }
.bar-empty { font-size: 0.8rem; color: var(--viz-muted); padding: 12px 0; }
</style>
