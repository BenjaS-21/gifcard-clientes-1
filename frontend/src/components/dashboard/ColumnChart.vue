<template>
  <div class="column-chart" ref="root">
    <svg v-if="width" :width="width" :height="height" role="img" :aria-label="ariaLabel">
      <!-- Grilla y eje: hairlines recesivas -->
      <g v-for="t in ticks" :key="t">
        <line :x1="padLeft" :x2="width - padRight" :y1="y(t)" :y2="y(t)" class="grid" />
        <text :x="padLeft - 8" :y="y(t) + 4" class="tick" text-anchor="end">{{ formatAxis(t) }}</text>
      </g>
      <line :x1="padLeft" :x2="width - padRight" :y1="y(0)" :y2="y(0)" class="baseline" />

      <!-- Columnas: ≤24px, punta redondeada de 4px, base recta -->
      <g v-for="(item, i) in items" :key="item.label">
        <path v-if="item.value > 0" :d="columnPath(i, item.value)" class="column" :class="{ dim: active !== null && active !== i }" />
        <text
          v-if="i === maxIndex && item.value > 0"
          :x="cx(i)" :y="y(item.value) - 8" class="value-label" text-anchor="middle"
        >{{ format(item.value) }}</text>
        <text :x="cx(i)" :y="height - 8" class="tick" text-anchor="middle">{{ item.short || item.label }}</text>
        <!-- Zona de hover/foco: toda la franja, más grande que la columna -->
        <rect
          :x="padLeft + band * i" :y="padTop" :width="band" :height="plotHeight"
          class="hit" tabindex="0" :aria-label="`${item.label}: ${format(item.value)}`"
          @mouseenter="active = i" @mouseleave="active = null" @focus="active = i" @blur="active = null"
        />
      </g>
    </svg>

    <div
      v-if="active !== null"
      class="viz-tooltip"
      :style="{ left: tooltipLeft + 'px', top: padTop + 'px' }"
    >
      <div class="viz-tooltip-title">{{ items[active].label }}</div>
      <div v-for="line in tooltipLines(items[active])" :key="line.label" class="viz-tooltip-row">
        <span>{{ line.label }}</span><strong>{{ line.value }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

/* Columnas de una sola serie (sin leyenda: el título dice qué se grafica). */
const props = defineProps({
  // [{ label, short, value, details: [{label, value}] }]
  items: { type: Array, required: true },
  format: { type: Function, default: (v) => String(v) },
  formatAxis: { type: Function, default: (v) => String(v) },
  ariaLabel: { type: String, default: '' },
  height: { type: Number, default: 240 }
})

const root = ref(null)
const width = ref(0)
const active = ref(null)
const padLeft = 56
const padRight = 8
const padTop = 22
const padBottom = 28
let observer = null

onMounted(() => {
  observer = new ResizeObserver(([entry]) => { width.value = Math.floor(entry.contentRect.width) })
  observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())

const plotHeight = computed(() => props.height - padTop - padBottom)
const band = computed(() => (width.value - padLeft - padRight) / Math.max(props.items.length, 1))
const barWidth = computed(() => Math.max(4, Math.min(24, band.value * 0.6)))

// Escala con números redondos: 0 / 1.000 / 2.000 ...
const niceMax = computed(() => {
  const max = Math.max(...props.items.map(i => i.value), 0)
  if (max <= 0) return 1
  const step = 10 ** Math.floor(Math.log10(max))
  return [1, 2, 2.5, 5, 10].map(m => m * step).find(v => v >= max) || max
})
const ticks = computed(() => [0, 0.25, 0.5, 0.75, 1].map(f => niceMax.value * f))
const maxIndex = computed(() => props.items.reduce((best, it, i, arr) => (it.value > arr[best].value ? i : best), 0))

const y = (v) => padTop + plotHeight.value * (1 - v / niceMax.value)
const cx = (i) => padLeft + band.value * i + band.value / 2

function columnPath(i, value) {
  const w = barWidth.value
  const x0 = cx(i) - w / 2
  const top = y(value)
  const base = y(0)
  const r = Math.min(4, w / 2, base - top)
  return `M${x0},${base} V${top + r} Q${x0},${top} ${x0 + r},${top} H${x0 + w - r} Q${x0 + w},${top} ${x0 + w},${top + r} V${base} Z`
}

const tooltipLeft = computed(() => {
  if (active.value === null) return 0
  const x = cx(active.value)
  return Math.min(Math.max(x - 90, 0), Math.max(width.value - 180, 0))
})
const tooltipLines = (item) => item.details || [{ label: 'Valor', value: props.format(item.value) }]
</script>

<style scoped>
.column-chart { position: relative; width: 100%; }
svg { display: block; overflow: visible; }
.grid { stroke: var(--viz-grid); stroke-width: 1; }
.baseline { stroke: var(--viz-axis); stroke-width: 1; }
.tick { fill: var(--viz-muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.value-label { fill: var(--viz-ink-2); font-size: 11px; font-weight: 600; }
.column { fill: var(--viz-series-1); transition: opacity 0.15s; }
.column.dim { opacity: 0.45; }
.hit { fill: transparent; cursor: default; outline: none; }
.hit:focus-visible { stroke: var(--viz-ink-2); stroke-width: 1; }
.viz-tooltip { position: absolute; width: 180px; padding: 8px 10px; background: var(--viz-surface); border: 1px solid var(--viz-border); border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); pointer-events: none; z-index: 2; }
.viz-tooltip-title { font-size: 0.75rem; font-weight: 600; color: var(--viz-ink); margin-bottom: 4px; }
.viz-tooltip-row { display: flex; justify-content: space-between; gap: 8px; font-size: 0.72rem; color: var(--viz-ink-2); }
.viz-tooltip-row strong { color: var(--viz-ink); font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
