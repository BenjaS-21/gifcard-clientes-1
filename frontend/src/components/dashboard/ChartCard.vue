<template>
  <section class="chart-card">
    <header class="chart-card-head">
      <div>
        <h3 class="chart-card-title">{{ title }}</h3>
        <p v-if="subtitle" class="chart-card-sub">{{ subtitle }}</p>
      </div>
      <button v-if="$slots.table" type="button" class="chart-card-toggle" @click="showTable = !showTable">
        {{ showTable ? 'Ver gráfico' : 'Ver tabla' }}
      </button>
    </header>
    <div v-if="showTable && $slots.table" class="chart-card-table">
      <slot name="table" />
    </div>
    <slot v-else />
  </section>
</template>

<script setup>
import { ref } from 'vue'

/* Tarjeta de un gráfico del dashboard, con su vista de tabla (accesible y exacta). */
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
const showTable = ref(false)
</script>

<style scoped>
.chart-card { background: var(--viz-surface); border: 1px solid var(--viz-border); border-radius: 12px; padding: 18px 20px; min-width: 0; }
.chart-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.chart-card-title { font-size: 0.95rem; font-weight: 600; color: var(--viz-ink); margin: 0; }
.chart-card-sub { font-size: 0.75rem; color: var(--viz-ink-2); margin: 2px 0 0; }
.chart-card-toggle { flex-shrink: 0; font-family: inherit; font-size: 0.75rem; font-weight: 500; padding: 5px 10px; border: 1px solid var(--viz-border); border-radius: 8px; background: var(--viz-surface); color: var(--viz-ink-2); cursor: pointer; }
.chart-card-toggle:hover { color: var(--viz-ink); border-color: var(--viz-axis); }
.chart-card-table { overflow-x: auto; }
</style>
