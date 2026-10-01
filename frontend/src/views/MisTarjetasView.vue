<template>
  <div class="mis-tarjetas">

    <!-- Summary Stats -->
    <div class="summary-row fade-up" style="animation-delay: 80ms">
      <div class="summary-card">
        <div class="summary-icon summary-icon--balance">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="summary-info">
          <span class="summary-label">Saldo total disponible</span>
          <span class="summary-value summary-value--balance">${{ formatMoney(totalBalance) }}</span>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon summary-icon--primary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="summary-info">
          <span class="summary-label">Tarjetas activas</span>
          <span class="summary-value">{{ activeCount }}</span>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon summary-icon--primary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 10h20"/></svg>
        </div>
        <div class="summary-info">
          <span class="summary-label">Total de tarjetas</span>
          <span class="summary-value">{{ giftcards.length }}</span>
        </div>
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
        <span class="text-xs text-muted">{{ giftcards.length }} {{ giftcards.length === 1 ? 'tarjeta' : 'tarjetas' }}</span>
      </div>

      <div v-if="giftcards.length" class="grid-cards">
        <div
          v-for="(gc, i) in giftcards"
          :key="gc.id"
          class="gc-wrapper fade-up"
          :style="{ animationDelay: (160 + i * 60) + 'ms' }"
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

          <!-- Usage mini-bar -->
          <div class="gc-usage-mini">
            <div class="gc-usage-track">
              <div class="gc-usage-fill" :class="usageColorClass(gc)" :style="{ width: usagePct(gc) + '%' }"></div>
            </div>
            <span class="gc-usage-text">{{ usagePct(gc) }}% usado</span>
          </div>

        </div>
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
const { downloading, downloadCard } = useCardDownload()
const giftcards = ref([])
const loading = ref(true)
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
    const cliente = JSON.parse(clienteStr)
    const res = await api.getGiftCards({ cedula: cliente.cedula })
    giftcards.value = res.data.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const totalBalance = computed(() => giftcards.value.reduce((s, gc) => s + (gc.saldo || 0), 0))
const activeCount = computed(() => giftcards.value.filter(gc => (gc.estado || '').toLowerCase() === 'activa').length)

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

/* ── Summary Row ── */
.summary-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-10);
}
.summary-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5) var(--space-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-subtle);
  transition: all var(--transition-base);
}
.summary-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(0,0,0,0.12);
}
.summary-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
  flex-shrink: 0;
}
.summary-icon--balance {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}
.summary-icon--primary {
  background: rgba(200, 16, 46, 0.1);
  color: var(--color-primary);
}
.summary-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.summary-label {
  font-size: 0.8125rem;
  color: var(--color-muted);
  font-weight: 400;
}
.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.summary-value--balance {
  color: var(--color-success);
}

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
  .summary-row { grid-template-columns: 1fr; gap: var(--space-3); margin-bottom: var(--space-8); }
  .grid-cards { grid-template-columns: 1fr; max-width: 480px; margin: 0 auto; }
  .gc-wrapper .gift-card { max-width: 100%; }
}
@media (max-width: 480px) {
  .summary-card { padding: var(--space-4); }
  .summary-value { font-size: 1.25rem; }
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
