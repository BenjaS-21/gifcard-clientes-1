<template>
  <div class="mis-tarjetas">

    <!-- KPI de actividad -->
    <div v-if="!loading && giftcards.length" class="kpi-grid fade-up" style="animation-delay: 80ms">
      <div class="kpi-card kpi-card--wide">
        <span class="kpi-label">Saldo disponible</span>
        <span class="kpi-value kpi-value--balance">${{ formatMoney(kpis.saldo) }}</span>
        <div class="kpi-track">
          <div class="kpi-fill" :style="{ width: kpis.pctConsumido + '%' }"></div>
        </div>
        <span class="kpi-sub">${{ formatMoney(kpis.consumido) }} consumido de ${{ formatMoney(kpis.emitido) }} ({{ kpis.pctConsumido }}%)</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Tarjetas</span>
        <span class="kpi-value">{{ giftcards.length }}</span>
        <span class="kpi-sub" v-if="kpis.entregadas">{{ kpis.entregadas }} entregadas</span>
        <span class="kpi-sub" v-else>{{ kpis.conSaldo }} con saldo</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Con uso</span>
        <span class="kpi-value">{{ kpis.conUso }}</span>
        <span class="kpi-sub">{{ kpis.sinUso }} sin usar</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Agotadas</span>
        <span class="kpi-value">{{ kpis.agotadas }}</span>
        <span class="kpi-sub">sin saldo disponible</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Usos registrados</span>
        <span class="kpi-value">{{ kpis.usos }}</span>
        <span class="kpi-sub">{{ kpis.ultimoUso ? 'Último: ' + formatDate(kpis.ultimoUso) : 'Sin usos todavía' }}</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span class="text-muted text-sm" style="margin-top: 16px">Sincronizando tus tarjetas...</span>
    </div>

    <!-- Gift Cards -->
    <div v-else class="section">
      <div class="section-header">
        <h2 class="section-title">Mis Gift Cards</h2>
        <button
          v-if="filteredCards.length"
          class="btn btn-outline btn-sm"
          :disabled="!!bulkProgress || !!downloading"
          @click="downloadAll"
        >
          <span v-if="bulkProgress" class="spinner spinner-sm"></span>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          {{ bulkProgress ? `Generando ${bulkProgress.done}/${bulkProgress.total}` : `Descargar todas (${filteredCards.length})` }}
        </button>
      </div>

      <div v-if="giftcards.length" class="card-filters">
        <button
          v-for="f in filters"
          :key="f.value"
          class="card-filter"
          :class="{ active: activeFilter === f.value }"
          @click="activeFilter = f.value"
        >
          {{ f.label }} <span class="card-filter-count">{{ f.count }}</span>
        </button>
      </div>

      <div v-if="filteredCards.length" class="grid-cards">
        <div
          v-for="(gc, i) in filteredCards"
          :key="gc.id"
          class="gc-wrapper fade-up"
          :style="{ animationDelay: Math.min(160 + i * 60, 800) + 'ms' }"
          @click="$router.push('/tarjeta/' + gc.id)"
        >
          <!-- Card Visual -->
          <div class="gift-card" :class="'gc-' + (gc.color || 'black')" :style="cardBgStyle" :ref="el => cardEls[gc.id] = el">
            <div class="gc-type-label">GIFT CARD</div>
            <div class="gc-pattern"></div>
            <div class="gc-logo">
              <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="gc-logo-img" />
            </div>
            <CardCompanyLogo :logo="gc.empresa_logo" />
            <div class="gc-number">{{ gc.numero_tarjeta }}</div>
            <div class="gc-bottom">
              <div>
                <div class="gc-label">Saldo disponible</div>
                <div class="gc-balance">${{ formatMoney(gc.saldo) }}</div>
              </div>
              <div class="gc-expiry" v-if="gc.fecha_vencimiento">
                <div class="gc-label">Vence</div>
                <div>{{ gc.fecha_vencimiento }}</div>
              </div>
            </div>
          </div>

          <!-- Card Meta -->
          <div class="gc-meta">
            <div class="gc-meta-left">
              <span class="badge" :class="statusClass(gc.estado)">
                <span class="badge-dot" :class="statusDotClass(gc.estado)"></span>
                {{ gc.estado }}
              </span>
            </div>
            <div class="gc-meta-right">
              <span class="gc-meta-label">Emitida</span>
              <span class="gc-meta-date">{{ formatDate(gc.fecha_emision) }}</span>
              <button
                class="gc-download-btn"
                title="Descargar imagen"
                :disabled="!!downloading"
                @click.stop="downloadCard(cardEls[gc.id], gc.numero_tarjeta)"
              >
                <span v-if="downloading === gc.numero_tarjeta" class="spinner spinner-sm"></span>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>
            </div>
          </div>

          <div v-if="gc.entregada" class="gc-entregada">
            Entregada a <strong>{{ gc.cliente_nombre || gc.cliente_cedula || 'otro beneficiario' }}</strong>
          </div>

          <!-- Usage mini-bar -->
          <div class="gc-usage-mini">
            <div class="gc-usage-track">
              <div class="gc-usage-fill" :class="usageColorClass(gc)" :style="{ width: usagePct(gc) + '%' }"></div>
            </div>
            <span class="gc-usage-text">{{ usagePct(gc) }}% usado</span>
          </div>

        </div>
      </div>

      <div v-else-if="giftcards.length" class="empty-state fade-up">
        <h3>No hay tarjetas en este filtro</h3>
        <p class="text-secondary" style="margin-top:8px">Elige otro filtro para ver tus tarjetas.</p>
      </div>

      <div v-else class="empty-state fade-up">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2"></rect>
            <path d="M2 10h20"></path>
          </svg>
        </div>
        <h3>No tienes Gift Cards</h3>
        <p class="text-secondary" style="margin-top:8px">Cuando adquieras una Gift Card Damasco, aparecerá aquí.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useCardDownload } from '../composables/useCardDownload'
import CardCompanyLogo from '../components/ui/CardCompanyLogo.vue'

const router = useRouter()
const cardEls = {}
const { downloading, bulkProgress, downloadCard, downloadAllCards } = useCardDownload()
const giftcards = ref([])
const loading = ref(true)
const cliente = ref(null)
const activeFilter = ref('all')
const cardBgUrl = ref(null)
const cardBgStyle = computed(() => cardBgUrl.value ? { backgroundImage: `url(${cardBgUrl.value})` } : {})

onMounted(async () => {
  // Cargar template activo
  try {
    const tpl = await api.getActiveTemplate()
    if (tpl.data.active) cardBgUrl.value = tpl.data.image_url
  } catch (e) { /* usa imagen por defecto del CSS */ }
  const clienteStr = localStorage.getItem('cliente')
  if (!clienteStr) {
    router.push('/login')
    return
  }
  try {
    cliente.value = JSON.parse(clienteStr)
    giftcards.value = await api.getAllGiftCards({ cedula: cliente.value.cedula })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

/* Clasificación de cada tarjeta según su actividad */
const isAgotada = (gc) => Number(gc.saldo_inicial || 0) > 0 && Number(gc.saldo || 0) <= 0
const isUsada = (gc) => (gc.num_usos || 0) > 0 || Number(gc.saldo || 0) < Number(gc.saldo_inicial || 0)

const kpis = computed(() => {
  const cards = giftcards.value
  const emitido = cards.reduce((s, gc) => s + Number(gc.saldo_inicial || 0), 0)
  const saldo = cards.reduce((s, gc) => s + Number(gc.saldo || 0), 0)
  const consumido = Math.max(emitido - saldo, 0)
  const fechas = cards.map(gc => gc.ultimo_uso).filter(Boolean).sort()
  return {
    emitido,
    saldo,
    consumido,
    pctConsumido: emitido ? Math.round((consumido / emitido) * 100) : 0,
    entregadas: cards.filter(gc => gc.entregada).length,
    conSaldo: cards.filter(gc => Number(gc.saldo || 0) > 0).length,
    sinUso: cards.filter(gc => !isUsada(gc)).length,
    conUso: cards.filter(gc => isUsada(gc) && !isAgotada(gc)).length,
    agotadas: cards.filter(isAgotada).length,
    usos: cards.reduce((s, gc) => s + (gc.num_usos || 0), 0),
    ultimoUso: fechas[fechas.length - 1] || null
  }
})

const FILTERS = [
  { label: 'Todas', value: 'all', test: () => true },
  { label: 'Sin usar', value: 'sin-uso', test: (gc) => !isUsada(gc) },
  { label: 'Con uso', value: 'con-uso', test: (gc) => isUsada(gc) && !isAgotada(gc) },
  { label: 'Agotadas', value: 'agotadas', test: isAgotada },
  { label: 'Entregadas', value: 'entregadas', test: (gc) => gc.entregada, onlyIfAny: true }
]

const filters = computed(() => FILTERS
  .map(f => ({ ...f, count: giftcards.value.filter(f.test).length }))
  .filter(f => !f.onlyIfAny || f.count > 0))

const filteredCards = computed(() => {
  const f = FILTERS.find(f => f.value === activeFilter.value) || FILTERS[0]
  return giftcards.value.filter(f.test)
})

const downloadAll = () => {
  const nombre = (cliente.value?.nombre || 'cliente').toLowerCase().normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  downloadAllCards(
    filteredCards.value.map(gc => ({ el: cardEls[gc.id], numero: gc.numero_tarjeta })),
    `giftcards-damasco-${nombre}.zip`
  )
}

const formatMoney = (v) => Number(v || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'

const statusClass = (status) => {
  const map = { activa: 'badge-success', vendida: 'badge-success', vencida: 'badge-warning', agotada: 'badge-muted', bloqueada: 'badge-destructive', generada: 'badge-muted' }
  return map[(status || '').toLowerCase()] || 'badge-muted'
}

const statusDotClass = (status) => {
  const map = { activa: 'dot-success', vendida: 'dot-success', vencida: 'dot-warning', agotada: 'dot-muted', bloqueada: 'dot-destructive', generada: 'dot-muted' }
  return map[(status || '').toLowerCase()] || 'dot-muted'
}

const usagePct = (gc) => {
  if (!gc.saldo_inicial) return 0
  return Math.round(((gc.saldo_inicial - gc.saldo) / gc.saldo_inicial) * 100)
}

const usageColorClass = (gc) => {
  const pct = usagePct(gc)
  if (pct >= 80) return 'usage-high'
  if (pct >= 50) return 'usage-mid'
  return 'usage-low'
}
</script>

<style scoped>
/* ── Logo inside card ── */
.gc-logo-img {
  height: 20px;
  width: auto;
  opacity: 0.95;
}

/* ── KPI ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-10);
}
.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--space-5) var(--space-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-subtle);
  min-width: 0;
}
.kpi-card--wide { grid-column: span 2; }
.kpi-label {
  font-size: 0.8125rem;
  color: var(--color-muted);
}
.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.kpi-value--balance { color: var(--color-success); font-size: 1.875rem; }
.kpi-sub {
  font-size: 0.75rem;
  color: var(--color-muted);
}
.kpi-track {
  height: 6px;
  margin: 6px 0 2px;
  background: var(--color-surface-hover);
  border-radius: 3px;
  overflow: hidden;
}
.kpi-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ── Filtros ── */
.card-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}
.card-filter {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  color: var(--color-foreground);
  transition: all var(--transition-base);
}
.card-filter:hover { border-color: var(--color-muted); }
.card-filter.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}
.card-filter-count { font-size: 0.75rem; opacity: 0.7; }

.gc-entregada {
  font-size: 0.75rem;
  color: var(--color-muted);
  padding: var(--space-2) var(--space-2) 0;
  text-align: center;
}
.gc-entregada strong { color: var(--color-foreground); font-weight: 600; }

/* ── Gift Card Wrapper ── */
.gc-wrapper {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  align-items: center;
  cursor: pointer;
  transition: all var(--transition-base);
}
.gc-wrapper:hover {
  border-color: rgba(0,0,0,0.15);
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px);
}
.gc-wrapper:hover .gift-card {
  box-shadow: 0 16px 40px rgba(0,0,0,0.3);
}

/* Card inside wrapper */
.gc-wrapper .gift-card {
  border-radius: 16px;
  transition: box-shadow var(--transition-base);
  width: 100%;
  max-width: 420px;
}

/* Chip decoration on card */
.gc-chip-deco {
  position: absolute;
  top: 50%;
  right: 28px;
  transform: translateY(-50%);
  width: 40px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, #d4af37 0%, #f5d779 40%, #c9a227 60%, #e8c84a 100%);
  opacity: 0.8;
  z-index: 2;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.15);
}
.gc-chip-deco::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 3px;
  right: 3px;
  height: 1px;
  background: rgba(0,0,0,0.15);
}

/* Pattern decoration */
.gc-pattern {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  opacity: 0.06;
  background-image:
    repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,1) 20px, rgba(255,255,255,1) 21px);
  pointer-events: none;
  z-index: 1;
  border-radius: inherit;
}

/* ── Card Meta ── */
.gc-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-2) 0;
}
.gc-meta-right {
  display: flex;
  align-items: center;
  gap: 6px;
}
.gc-download-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  margin-left: 4px;
  border-radius: var(--radius-sm);
  color: var(--color-muted);
  transition: all var(--transition-base);
}
.gc-download-btn:hover:not(:disabled) {
  color: var(--color-foreground);
  background: var(--color-surface-hover);
}
.gc-download-btn:disabled { opacity: 0.5; cursor: default; }
.gc-meta-label {
  font-size: 0.6875rem;
  color: var(--color-muted);
  font-weight: 400;
}
.gc-meta-date {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-foreground);
}

/* Badge dot */
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.dot-success { background: var(--color-success); }
.dot-warning { background: var(--color-warning); }
.dot-destructive { background: var(--color-destructive); }
.dot-muted { background: var(--color-muted); }

/* ── Mini Usage Bar ── */
.gc-usage-mini {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-2) var(--space-1);
}
.gc-usage-track {
  flex: 1;
  height: 4px;
  background: var(--color-surface-hover);
  border-radius: 2px;
  overflow: hidden;
}
.gc-usage-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.usage-low { background: var(--color-success); }
.usage-mid { background: var(--color-warning); }
.usage-high { background: var(--color-destructive); }

.gc-usage-text {
  font-size: 0.625rem;
  color: var(--color-muted);
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.03em;
}

/* ── Wave Animation ── */
@keyframes wave {
  0% { transform: rotate(0.0deg) }
  10% { transform: rotate(14.0deg) }
  20% { transform: rotate(-8.0deg) }
  30% { transform: rotate(14.0deg) }
  40% { transform: rotate(-4.0deg) }
  50% { transform: rotate(10.0deg) }
  60% { transform: rotate(0.0deg) }
  100% { transform: rotate(0.0deg) }
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .grid-cards { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-bottom: var(--space-8); }
  .grid-cards { grid-template-columns: 1fr; max-width: 480px; margin: 0 auto; }
  .gc-wrapper .gift-card { max-width: 100%; }
}
@media (max-width: 480px) {
  .kpi-card { padding: var(--space-4); }
  .kpi-value { font-size: 1.25rem; }
  .kpi-value--balance { font-size: 1.5rem; }
  .gc-meta { flex-direction: column; align-items: flex-start; gap: var(--space-2); }
}

/* ── Gratuita Badge ── */
.gratuita-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #FEF3C7, #FDE68A);
  border: 1.5px solid #F59E0B;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  color: #92400E;
  letter-spacing: 0.01em;
}
.gratuita-badge svg {
  color: #D97706;
  flex-shrink: 0;
}
</style>
