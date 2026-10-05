<template>
  <div class="viz-root">
    <!-- Filtros: una sola fila arriba de todo lo que afectan -->
    <div class="dash-filters">
      <select v-model="empresa" class="dash-select" aria-label="Empresa">
        <option value="">Todas las empresas</option>
        <option v-for="e in data?.empresas || []" :key="e.id" :value="String(e.id)">{{ e.nombre }}</option>
      </select>
      <input v-model="lote" type="search" class="dash-input" placeholder="Lote (o parte del código)" aria-label="Lote" />
      <div class="dash-periods" role="group" aria-label="Período de venta">
        <button
          v-for="p in PERIODOS" :key="p.value" type="button"
          :class="{ active: periodo === p.value }" @click="periodo = p.value"
        >{{ p.label }}</button>
      </div>
      <button type="button" class="dash-refresh" :disabled="loading" @click="load(true)" title="Volver a leer los datos de SAP">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
        Actualizar
      </button>
    </div>
    <p class="dash-note">
      El período filtra por fecha de venta: muestra cómo se han usado las tarjetas vendidas en ese período.
      <span v-if="data">Última lectura de SAP: {{ formatTime(data.actualizado) }}</span>
    </p>

    <div v-if="error" class="dash-error">{{ error }}</div>
    <div v-else-if="!data" class="dash-loading"><span class="spinner"></span> Cargando indicadores...</div>

    <div v-else-if="!k.generadas" class="dash-empty" :class="{ refreshing: loading }">
      No hay tarjetas con estos filtros. Prueba con otro lote, empresa o período.
    </div>

    <div v-else class="dash-body" :class="{ refreshing: loading }">
      <!-- Cifra principal + indicadores -->
      <div class="dash-tiles">
        <div class="tile tile-hero">
          <span class="tile-label">Tarjetas vendidas que ya se usaron</span>
          <span class="hero-value">{{ fmtPct(k.pct_uso) }}</span>
          <span class="tile-sub">{{ fmtInt(k.con_uso) }} de {{ fmtInt(k.vendidas) }} tarjetas vendidas</span>
        </div>
        <div class="tile">
          <span class="tile-label">Monto vendido</span>
          <span class="tile-value">{{ fmtMoneyCompact(k.monto_vendido) }}</span>
          <span class="tile-sub">{{ fmtInt(k.vendidas) }} tarjetas</span>
        </div>
        <div class="tile">
          <span class="tile-label">Consumido en tienda</span>
          <span class="tile-value">{{ fmtMoneyCompact(k.consumido) }}</span>
          <div class="meter" :aria-label="`${fmtPct(k.pct_consumido)} del monto vendido`">
            <div class="meter-fill" :style="{ width: Math.min(k.pct_consumido, 100) + '%' }"></div>
          </div>
          <span class="tile-sub">{{ fmtPct(k.pct_consumido) }} del monto vendido</span>
        </div>
        <div class="tile">
          <span class="tile-label">Saldo pendiente por usar</span>
          <span class="tile-value">{{ fmtMoneyCompact(k.saldo_pendiente) }}</span>
          <span class="tile-sub">en {{ fmtInt(k.vendidas - k.agotadas) }} tarjetas con saldo</span>
        </div>
        <div class="tile">
          <span class="tile-label">Usos en tienda</span>
          <span class="tile-value">{{ fmtInt(k.usos) }}</span>
          <span class="tile-sub">ticket promedio {{ fmtMoney(k.ticket_promedio) }}</span>
        </div>
        <div class="tile">
          <span class="tile-label">Días hasta el primer uso</span>
          <span class="tile-value">{{ k.dias_primer_uso ?? '—' }}</span>
          <span class="tile-sub">mediana desde la venta</span>
        </div>
      </div>

      <!-- Alertas para dar seguimiento (estado: ícono + texto, nunca solo color) -->
      <div class="dash-alerts">
        <button type="button" class="alert alert-warning" @click="seguimiento = 'sin_uso'; scrollTo('seguimiento')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <span><strong>{{ fmtInt(k.sin_uso_viejas) }}</strong> vendidas hace más de 60 días y sin usar</span>
        </button>
        <button type="button" class="alert alert-serious" @click="seguimiento = 'por_vencer'; scrollTo('seguimiento')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span><strong>{{ fmtInt(k.por_vencer) }}</strong> vencen en 30 días con {{ fmtMoney(k.por_vencer_saldo) }} de saldo</span>
        </button>
        <div class="alert alert-critical">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          <span><strong>{{ fmtInt(k.vencidas_con_saldo) }}</strong> vencidas con {{ fmtMoney(k.vencidas_saldo) }} sin usar</span>
        </div>
      </div>

      <!-- Uso de las tarjetas vendidas -->
      <ChartCard title="Uso de las tarjetas vendidas" :subtitle="`${fmtInt(k.vendidas)} tarjetas vendidas · ${fmtInt(k.sin_vender)} generadas sin vender`">
        <StackedBar :segments="usoSegments" :format="fmtInt" aria-label="Tarjetas vendidas según su uso" />
        <template #table>
          <table class="viz-table">
            <thead><tr><th>Estado de uso</th><th class="num">Tarjetas</th></tr></thead>
            <tbody>
              <tr v-for="s in usoSegments" :key="s.label"><td>{{ s.label }}</td><td class="num">{{ fmtInt(s.value) }}</td></tr>
              <tr><td>Generadas sin vender</td><td class="num">{{ fmtInt(k.sin_vender) }}</td></tr>
            </tbody>
          </table>
        </template>
      </ChartCard>

      <div class="dash-grid-2">
        <ChartCard title="Consumo en tienda por mes" subtitle="Monto usado con gift cards, últimos 12 meses">
          <ColumnChart :items="consumoItems" :format="fmtMoney" :format-axis="fmtMoneyAxis" aria-label="Consumo por mes" />
          <template #table>
            <table class="viz-table">
              <thead><tr><th>Mes</th><th class="num">Usos</th><th class="num">Monto</th></tr></thead>
              <tbody><tr v-for="m in data.consumo_mensual" :key="m.mes"><td>{{ monthLabel(m.mes) }}</td><td class="num">{{ fmtInt(m.usos) }}</td><td class="num">{{ fmtMoney(m.monto) }}</td></tr></tbody>
            </table>
          </template>
        </ChartCard>
        <ChartCard title="Tarjetas vendidas por mes" subtitle="Cantidad de tarjetas vendidas, últimos 12 meses">
          <ColumnChart :items="ventasItems" :format="fmtInt" :format-axis="fmtCompact" aria-label="Tarjetas vendidas por mes" />
          <template #table>
            <table class="viz-table">
              <thead><tr><th>Mes</th><th class="num">Tarjetas</th><th class="num">Monto</th></tr></thead>
              <tbody><tr v-for="m in data.ventas_mensuales" :key="m.mes"><td>{{ monthLabel(m.mes) }}</td><td class="num">{{ fmtInt(m.tarjetas) }}</td><td class="num">{{ fmtMoney(m.monto) }}</td></tr></tbody>
            </table>
          </template>
        </ChartCard>
      </div>

      <div class="dash-grid-2">
        <ChartCard
          title="Clientes y empresas que más usan sus gift cards"
          :subtitle="`Por monto consumido · ${fmtInt(data.clientes_total)} clientes en total`"
        >
          <BarList :items="clientesItems" :format="fmtMoney" />
          <template #table>
            <table class="viz-table">
              <thead><tr><th>Cliente</th><th class="num">Tarjetas</th><th class="num">Usadas</th><th class="num">Vendido</th><th class="num">Consumido</th><th>Último uso</th></tr></thead>
              <tbody>
                <tr v-for="c in data.clientes" :key="c.nombre + c.identificador">
                  <td>{{ c.nombre }}<div class="cell-sub">{{ c.identificador }}</div></td>
                  <td class="num">{{ fmtInt(c.tarjetas) }}</td>
                  <td class="num">{{ fmtPct(c.pct_uso) }}</td>
                  <td class="num">{{ fmtMoney(c.monto) }}</td>
                  <td class="num">{{ fmtMoney(c.consumido) }}</td>
                  <td>{{ formatDate(c.ultimo_uso) }}</td>
                </tr>
              </tbody>
            </table>
          </template>
        </ChartCard>
        <ChartCard title="Dónde se usan" subtitle="Monto consumido por sucursal">
          <BarList :items="sucursalItems" :format="fmtMoney" />
          <template #table>
            <table class="viz-table">
              <thead><tr><th>Sucursal</th><th class="num">Usos</th><th class="num">Monto</th></tr></thead>
              <tbody><tr v-for="s in data.sucursales" :key="s.sucursal"><td>{{ s.sucursal }}</td><td class="num">{{ fmtInt(s.usos) }}</td><td class="num">{{ fmtMoney(s.monto) }}</td></tr></tbody>
            </table>
          </template>
        </ChartCard>
      </div>

      <div class="dash-grid-2">
        <ChartCard title="Lotes con más consumo" :subtitle="`${fmtInt(data.lotes_total)} lotes en total`">
          <div class="chart-card-table">
            <table class="viz-table">
              <thead><tr><th>Lote</th><th class="num">Vendidas</th><th class="num">Usadas</th><th class="num">Consumido</th></tr></thead>
              <tbody>
                <tr v-for="l in data.lotes" :key="l.lote">
                  <td>{{ l.lote }}<div v-if="l.empresa" class="cell-sub">{{ l.empresa }}</div></td>
                  <td class="num">{{ fmtInt(l.vendidas) }}</td>
                  <td class="num">{{ fmtPct(l.pct_uso) }}</td>
                  <td class="num">{{ fmtMoney(l.consumido) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </ChartCard>
        <ChartCard title="Uso según el monto de la tarjeta" subtitle="% de tarjetas vendidas que ya se usaron, por denominación">
          <BarList :items="denomItems" :format="fmtPct" :max="100" />
          <template #table>
            <table class="viz-table">
              <thead><tr><th>Monto</th><th class="num">Vendidas</th><th class="num">Usadas</th><th class="num">% uso</th></tr></thead>
              <tbody><tr v-for="d in data.denominaciones" :key="d.monto"><td>{{ fmtMoney(d.monto) }}</td><td class="num">{{ fmtInt(d.vendidas) }}</td><td class="num">{{ fmtInt(d.con_uso) }}</td><td class="num">{{ fmtPct(d.pct_uso) }}</td></tr></tbody>
            </table>
          </template>
        </ChartCard>
      </div>

      <!-- Listas de seguimiento -->
      <ChartCard id="seguimiento" title="Seguimiento" subtitle="Tarjetas a las que conviene darles seguimiento con el cliente">
        <div class="seg-tabs" role="tablist">
          <button type="button" role="tab" :aria-selected="seguimiento === 'sin_uso'" :class="{ active: seguimiento === 'sin_uso' }" @click="seguimiento = 'sin_uso'">
            Sin usar hace más de 60 días ({{ fmtInt(k.sin_uso_viejas) }})
          </button>
          <button type="button" role="tab" :aria-selected="seguimiento === 'por_vencer'" :class="{ active: seguimiento === 'por_vencer' }" @click="seguimiento = 'por_vencer'">
            Por vencer en 30 días ({{ fmtInt(k.por_vencer) }})
          </button>
        </div>
        <div class="chart-card-table seg-scroll">
          <table class="viz-table">
            <thead>
              <tr>
                <th>Tarjeta</th><th>Cliente</th><th>Lote</th><th class="num">Saldo</th>
                <th>{{ seguimiento === 'sin_uso' ? 'Vendida' : 'Vence' }}</th>
                <th v-if="seguimiento === 'sin_uso'" class="num">Días sin uso</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in seguimientoRows" :key="c.codigo">
                <td class="mono">{{ c.codigo }}</td>
                <td>{{ c.cliente || '—' }}<div v-if="c.identificador" class="cell-sub">{{ c.identificador }}</div></td>
                <td>{{ c.lote || '—' }}</td>
                <td class="num">{{ fmtMoney(c.saldo) }}</td>
                <td>{{ formatDate(seguimiento === 'sin_uso' ? c.fecha_venta : c.vence) }}</td>
                <td v-if="seguimiento === 'sin_uso'" class="num">{{ fmtInt(c.dias_sin_uso) }}</td>
              </tr>
              <tr v-if="!seguimientoRows.length"><td colspan="6" class="cell-empty">No hay tarjetas en esta lista.</td></tr>
            </tbody>
          </table>
        </div>
        <p v-if="seguimientoTotal > seguimientoRows.length" class="dash-note">
          Mostrando {{ seguimientoRows.length }} de {{ fmtInt(seguimientoTotal) }}. Filtra por empresa o lote para ver el resto.
        </p>
      </ChartCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../../services/api'
import ChartCard from './ChartCard.vue'
import ColumnChart from './ColumnChart.vue'
import BarList from './BarList.vue'
import StackedBar from './StackedBar.vue'

/* Dashboard de venta y uso de las gift cards (panel admin y portal de vendedores). */
const props = defineProps({
  adminToken: { type: String, default: null } // el admin usa su token; el vendedor va por su sesión
})

const PERIODOS = [
  { value: 'todo', label: 'Todo' },
  { value: 'anio', label: 'Este año' },
  { value: '90d', label: '90 días' },
  { value: '30d', label: '30 días' }
]
// Slots categóricos validados (azul, naranja, aqua): ver el skill de dataviz
const SERIES = ['var(--viz-series-1)', 'var(--viz-series-2)', 'var(--viz-series-3)']

const data = ref(null)
const loading = ref(false)
const error = ref(null)
const empresa = ref('')
const lote = ref('')
const periodo = ref('todo')
const seguimiento = ref('sin_uso')

const k = computed(() => data.value?.kpis || {})

async function load(refresh = false) {
  loading.value = true
  error.value = null
  try {
    const params = {
      empresa: empresa.value || undefined,
      lote: lote.value.trim() || undefined,
      periodo: periodo.value,
      refresh: refresh ? 1 : undefined
    }
    const res = await api.getDashboard(params, props.adminToken)
    data.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudieron cargar los indicadores.'
  } finally {
    loading.value = false
  }
}

let loteTimer = null
watch(lote, () => {
  clearTimeout(loteTimer)
  loteTimer = setTimeout(() => load(), 450)
})
watch([empresa, periodo], () => load())
onMounted(() => load())

// ── Datos de cada gráfico ──
const usoSegments = computed(() => [
  { label: 'Usadas, con saldo', value: Math.max((k.value.con_uso || 0) - (k.value.agotadas || 0), 0), color: SERIES[0] },
  { label: 'Agotadas', value: k.value.agotadas || 0, color: SERIES[2] },
  { label: 'Sin usar', value: k.value.sin_uso || 0, color: SERIES[1] }
])

const consumoItems = computed(() => (data.value?.consumo_mensual || []).map(m => ({
  label: monthLabel(m.mes), short: monthShort(m.mes), value: m.monto,
  details: [{ label: 'Monto', value: fmtMoney(m.monto) }, { label: 'Usos', value: fmtInt(m.usos) }]
})))
const ventasItems = computed(() => (data.value?.ventas_mensuales || []).map(m => ({
  label: monthLabel(m.mes), short: monthShort(m.mes), value: m.tarjetas,
  details: [{ label: 'Tarjetas', value: fmtInt(m.tarjetas) }, { label: 'Monto', value: fmtMoney(m.monto) }]
})))
const clientesItems = computed(() => (data.value?.clientes || []).map(c => ({
  key: c.nombre + c.identificador, label: c.nombre, value: c.consumido,
  sub: `${fmtInt(c.tarjetas)} tarjetas · ${fmtPct(c.pct_uso)} usadas · ${fmtPct(c.pct_consumido)} del monto consumido`
})))
const sucursalItems = computed(() => (data.value?.sucursales || []).map(s => ({
  key: s.sucursal, label: `Sucursal ${s.sucursal}`, value: s.monto, sub: `${fmtInt(s.usos)} usos`
})))
const denomItems = computed(() => (data.value?.denominaciones || []).map(d => ({
  key: d.monto, label: `Tarjetas de ${fmtMoney(d.monto)}`, value: d.pct_uso,
  sub: `${fmtInt(d.con_uso)} de ${fmtInt(d.vendidas)} vendidas`
})))
const seguimientoRows = computed(() => (seguimiento.value === 'sin_uso' ? data.value?.sin_uso_viejas : data.value?.por_vencer) || [])
const seguimientoTotal = computed(() => (seguimiento.value === 'sin_uso' ? k.value.sin_uso_viejas : k.value.por_vencer) || 0)

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// ── Formatos ──
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
const intFmt = new Intl.NumberFormat('es-VE')
const moneyFmt = new Intl.NumberFormat('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const compactFmt = new Intl.NumberFormat('es-VE', { notation: 'compact', maximumFractionDigits: 1 })
const fmtInt = (v) => intFmt.format(Math.round(v || 0))
const fmtMoney = (v) => '$' + moneyFmt.format(v || 0)
const fmtCompact = (v) => compactFmt.format(v || 0)
const fmtMoneyAxis = (v) => (Math.abs(v || 0) >= 10000 ? '$' + compactFmt.format(v) : '$' + intFmt.format(Math.round(v || 0)))
const fmtMoneyCompact = (v) => (Math.abs(v || 0) >= 10000 ? '$' + compactFmt.format(v) : fmtMoney(v))
const fmtPct = (v) => `${(v || 0).toLocaleString('es-VE', { maximumFractionDigits: 1 })}%`
const monthShort = (m) => MESES[Number(m.slice(5, 7)) - 1]
const monthLabel = (m) => `${monthShort(m)} ${m.slice(0, 4)}`
const formatDate = (d) => (d ? new Date(d.length === 10 ? d + 'T12:00:00' : d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' }) : '—')
const formatTime = (d) => (d ? new Date(d).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' }) : '')
</script>

<style scoped>
/* Tokens del dashboard (paleta validada; el portal es solo modo claro) */
.viz-root {
  --viz-surface: #ffffff;
  --viz-ink: #0b0b0b;
  --viz-ink-2: #52514e;
  --viz-muted: #898781;
  --viz-grid: #e1e0d9;
  --viz-axis: #c3c2b7;
  --viz-border: rgba(11, 11, 11, 0.10);
  --viz-series-1: #2a78d6;
  --viz-series-2: #eb6834;
  --viz-series-3: #1baf7a;
  --viz-warning: #fab219;
  --viz-serious: #ec835a;
  --viz-critical: #d03b3b;
  font-family: 'Poppins', system-ui, -apple-system, 'Segoe UI', sans-serif;
  color: var(--viz-ink);
}

.dash-filters { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.dash-select, .dash-input { font-family: inherit; font-size: 0.85rem; padding: 10px 12px; border: 1px solid var(--viz-border); border-radius: 10px; background: var(--viz-surface); color: var(--viz-ink); outline: none; }
.dash-select:focus, .dash-input:focus { border-color: var(--viz-series-1); }
.dash-select { min-width: 210px; }
.dash-input { flex: 1; min-width: 200px; }
.dash-periods { display: inline-flex; background: var(--viz-surface); border: 1px solid var(--viz-border); border-radius: 10px; padding: 3px; }
.dash-periods button { font-family: inherit; font-size: 0.8rem; font-weight: 500; padding: 7px 12px; border: none; border-radius: 8px; background: transparent; color: var(--viz-ink-2); cursor: pointer; }
.dash-periods button.active { background: var(--viz-ink); color: #fff; }
.dash-refresh { display: inline-flex; align-items: center; gap: 6px; font-family: inherit; font-size: 0.8rem; font-weight: 500; padding: 9px 12px; border: 1px solid var(--viz-border); border-radius: 10px; background: var(--viz-surface); color: var(--viz-ink-2); cursor: pointer; }
.dash-refresh:disabled { opacity: 0.5; cursor: default; }
.dash-note { font-size: 0.74rem; color: var(--viz-muted); margin: 8px 0 0; }
.dash-error { margin-top: 18px; padding: 14px; border-radius: 10px; background: #fef2f2; color: #b42318; font-size: 0.85rem; }
.dash-loading { display: flex; align-items: center; gap: 10px; padding: 48px 0; justify-content: center; color: var(--viz-ink-2); font-size: 0.85rem; }
.spinner { width: 18px; height: 18px; border: 2px solid var(--viz-grid); border-top-color: var(--viz-series-1); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.dash-empty { margin-top: 18px; padding: 48px 16px; text-align: center; border: 1px dashed var(--viz-axis); border-radius: 12px; color: var(--viz-ink-2); font-size: 0.85rem; transition: opacity 0.2s; }
.dash-empty.refreshing { opacity: 0.55; }
.dash-body { display: flex; flex-direction: column; gap: 16px; margin-top: 18px; transition: opacity 0.2s; }
.dash-body.refreshing { opacity: 0.55; }

/* Indicadores */
.dash-tiles { display: grid; grid-template-columns: 1.3fr repeat(5, 1fr); gap: 12px; }
.tile { background: var(--viz-surface); border: 1px solid var(--viz-border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.tile-label { font-size: 0.75rem; color: var(--viz-ink-2); }
.tile-value { font-size: 1.45rem; font-weight: 600; letter-spacing: -0.01em; }
.tile-sub { font-size: 0.72rem; color: var(--viz-muted); }
.tile-hero { justify-content: center; }
.hero-value { font-size: 3rem; font-weight: 600; line-height: 1.05; letter-spacing: -0.02em; }
.meter { height: 6px; border-radius: 3px; background: #cde2fb; overflow: hidden; margin: 2px 0; }
.meter-fill { height: 100%; background: var(--viz-series-1); border-radius: 3px; }

/* Alertas de seguimiento */
.dash-alerts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.alert { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border: 1px solid var(--viz-border); border-radius: 12px; background: var(--viz-surface); font-family: inherit; font-size: 0.8rem; color: var(--viz-ink-2); text-align: left; }
button.alert { cursor: pointer; }
button.alert:hover { border-color: var(--viz-axis); }
.alert strong { color: var(--viz-ink); font-size: 0.95rem; }
.alert svg { flex-shrink: 0; }
.alert-warning svg { color: var(--viz-warning); }
.alert-serious svg { color: var(--viz-serious); }
.alert-critical svg { color: var(--viz-critical); }

.dash-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* Tablas */
.chart-card-table { overflow-x: auto; }
.viz-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.viz-table th { text-align: left; font-weight: 500; color: var(--viz-muted); padding: 6px 8px; border-bottom: 1px solid var(--viz-grid); white-space: nowrap; }
.viz-table td { padding: 8px; border-bottom: 1px solid var(--viz-grid); color: var(--viz-ink); vertical-align: top; }
.viz-table .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.viz-table .mono { font-family: monospace; letter-spacing: 0.05em; }
.cell-sub { font-size: 0.7rem; color: var(--viz-muted); }
.cell-empty { text-align: center; color: var(--viz-muted); padding: 18px; }

.seg-scroll { max-height: 440px; overflow-y: auto; }
.seg-scroll thead th { position: sticky; top: 0; background: var(--viz-surface); }
.seg-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.seg-tabs button { font-family: inherit; font-size: 0.78rem; font-weight: 500; padding: 6px 12px; border: 1px solid var(--viz-border); border-radius: 999px; background: var(--viz-surface); color: var(--viz-ink-2); cursor: pointer; }
.seg-tabs button.active { background: var(--viz-ink); border-color: var(--viz-ink); color: #fff; }

@media (max-width: 1100px) {
  .dash-tiles { grid-template-columns: repeat(3, 1fr); }
  .tile-hero { grid-column: span 3; }
}
@media (max-width: 760px) {
  .dash-grid-2, .dash-alerts { grid-template-columns: 1fr; }
  .dash-tiles { grid-template-columns: repeat(2, 1fr); }
  .tile-hero { grid-column: span 2; }
  .hero-value { font-size: 2.5rem; }
  .dash-select, .dash-input { min-width: 0; width: 100%; }
  .dash-periods { width: 100%; justify-content: space-between; }
}
</style>
