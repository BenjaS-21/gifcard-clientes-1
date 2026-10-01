<template>
  <div class="tarjeta-detalle" v-if="gc">
    <!-- Back -->
    <button class="btn btn-ghost btn-sm back-btn" @click="$router.push('/')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
      Mis Tarjetas
    </button>

    <!-- ═══════════════════════════════════════ -->
    <!-- HERO: Card + Info                      -->
    <!-- ═══════════════════════════════════════ -->
    <div class="detail-hero fade-up">
      <!-- Large Gift Card -->
      <div class="hero-card-wrapper">
        <div
          class="gift-card gift-card-detail"
          :class="'gc-' + (gc.color || 'black')"
          :style="cardBgStyle"
          @mousemove="handleTilt"
          @mouseleave="resetTilt"
          ref="cardEl"
        >
          <!-- Decorative elements -->
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
              <div class="gc-balance">${{ formatMoney(saldoReal) }}</div>
            </div>
            <div class="gc-expiry" v-if="gc.fecha_vencimiento">
              <div class="gc-label">Vence</div>
              <div>{{ gc.fecha_vencimiento }}</div>
            </div>
          </div>
        </div>

        <button
          class="btn btn-outline btn-sm"
          :disabled="!!downloading"
          @click="downloadCard(cardEl, gc.numero_tarjeta)"
        >
          <span v-if="downloading" class="spinner spinner-sm"></span>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Descargar imagen
        </button>
      </div>

      <!-- Info Panel -->
      <div class="hero-info">
        <!-- Status row -->
        <div class="status-row">
          <span class="badge" :class="statusClass(gc.estado)">{{ gc.estado }}</span>
          <span class="card-id text-xs text-muted">{{ gc.numero_tarjeta }}</span>
        </div>

        <!-- Main balance -->
        <div class="balance-hero">
          <span class="balance-label">Saldo Actual</span>
          <span class="balance-amount">${{ formatMoney(saldoReal) }}</span>
          <span class="balance-initial text-muted">de ${{ formatMoney(gc.saldo_inicial) }} inicial</span>
        </div>

        <!-- Usage bar -->
        <div class="usage-section">
          <div class="usage-header">
            <span class="text-xs text-muted">Consumido</span>
            <span class="text-xs" style="font-weight:600">{{ usagePct }}%</span>
          </div>
          <div class="usage-track">
            <div class="usage-fill" :class="usageColor" :style="{ width: usagePct + '%' }"></div>
          </div>
          <div class="usage-labels">
            <span class="text-xs text-muted">Usado: ${{ formatMoney(consumed) }}</span>
            <span class="text-xs text-muted">Disponible: ${{ formatMoney(saldoReal) }}</span>
          </div>
        </div>

        <!-- Info chips -->
        <div class="info-chips">
          <div class="info-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <div>
              <span class="chip-label">Emisión</span>
              <span class="chip-value">{{ formatDate(gc.fecha_emision) }}</span>
            </div>
          </div>
          <div class="info-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <div>
              <span class="chip-label">Vencimiento</span>
              <span class="chip-value">{{ formatDate(gc.fecha_vencimiento) }}</span>
            </div>
          </div>
          <div class="info-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <div>
              <span class="chip-label">Saldo Inicial</span>
              <span class="chip-value">${{ formatMoney(gc.saldo_inicial) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════ -->
    <!-- TRANSACTIONS                           -->
    <!-- ═══════════════════════════════════════ -->
    <div class="section fade-up" style="animation-delay: 150ms">
      <div class="section-header">
        <h2 class="section-title">Movimientos</h2>
        <span class="text-xs text-muted" v-if="gc.transactions?.length">
          {{ gc.transactions.length }} {{ gc.transactions.length === 1 ? 'transacción' : 'transacciones' }}
        </span>
      </div>

      <div class="card">
        <div class="card-body" style="padding:0" v-if="gc.transactions?.length">
          <div class="tx-list">
            <div v-for="tx in gc.transactions" :key="tx.id" class="tx-item">
              <div class="tx-icon-wrapper" :class="isDebit(tx) ? 'tx-icon-default-debit' : 'tx-icon-default-credit'">
                <svg v-if="isDebit(tx)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
              </div>
              
              <div class="tx-info">
                <div class="tx-title" :title="tx.descripcion">{{ tx.descripcion }}</div>
                <div class="tx-meta">
                  <span class="tx-meta-item text-muted">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                    {{ formatDate(tx.fecha) }}
                  </span>
                  <span class="tx-meta-item tx-ref" v-if="tx.referencia">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    Ref: {{ tx.referencia }}
                  </span>
                </div>
              </div>
              
              <div class="tx-amount-wrapper">
                <div class="tx-amount" :class="isDebit(tx) ? 'tx-debit' : 'tx-credit'">
                  {{ isDebit(tx) ? '-' : '+' }}${{ formatMoney(tx.monto) }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="card-body">
          <div class="empty-state" style="padding:var(--space-16)">
            <div class="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <h3>Sin movimientos</h3>
            <p class="text-secondary" style="margin-top:8px">Aún no se han registrado transacciones en esta tarjeta.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading-spinner">
    <div class="spinner"></div>
    <span class="text-muted text-sm" style="margin-top: 16px">Cargando detalles...</span>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { useCardDownload } from '../composables/useCardDownload'
import CardCompanyLogo from '../components/ui/CardCompanyLogo.vue'

const route = useRoute()
const { downloading, downloadCard } = useCardDownload()
const gc = ref(null)
const cardEl = ref(null)
const cardBgUrl = ref(null)
const cardBgStyle = computed(() => cardBgUrl.value ? { backgroundImage: `url(${cardBgUrl.value})` } : {})

onMounted(async () => {
  try {
    const tpl = await api.getActiveTemplate()
    if (tpl.data.active) cardBgUrl.value = tpl.data.image_url
  } catch (e) { /* usa imagen por defecto */ }
  try {
    const res = await api.getGiftCard(route.params.id)
    gc.value = res.data
  } catch (e) { console.error(e) }
})

/* Tipos de transacción que cuentan como débito */
const DEBIT_TYPES = ['USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO']
const isDebit = (tx) => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase())

/* Saldo real = saldo_inicial - suma de débitos (SAP confirmados + KLK pendientes).
   Evita inconsistencias cuando SAP marca U_Saldo = 0 sin tener TRX que lo justifique. */
const saldoReal = computed(() => {
  const inicial = Number(gc.value?.saldo_inicial || 0)
  const debitos = (gc.value?.transactions || [])
    .filter(tx => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase()))
    .reduce((sum, tx) => sum + Math.abs(Number(tx.monto || 0)), 0)
  return Math.max(inicial - debitos, 0)
})
const consumed = computed(() => (gc.value?.saldo_inicial || 0) - saldoReal.value)
const usagePct = computed(() => {
  if (!gc.value?.saldo_inicial) return 0
  return Math.round((consumed.value / gc.value.saldo_inicial) * 100)
})
const usageColor = computed(() => {
  if (usagePct.value >= 80) return 'usage-high'
  if (usagePct.value >= 50) return 'usage-mid'
  return 'usage-low'
})

const formatMoney = (v) => Math.abs(Number(v || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'
const statusClass = (s) => ({ activa: 'badge-success', vendida: 'badge-success', vencida: 'badge-warning', agotada: 'badge-muted', bloqueada: 'badge-destructive', generada: 'badge-muted' }[(s || '').toLowerCase()] || 'badge-muted')

/* 3D tilt effect */
function handleTilt(e) {
  if (!cardEl.value) return
  const rect = cardEl.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const midX = rect.width / 2
  const midY = rect.height / 2
  const rotateY = ((x - midX) / midX) * 8
  const rotateX = ((midY - y) / midY) * 8
  cardEl.value.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`
}
function resetTilt() {
  if (!cardEl.value) return
  cardEl.value.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale(1)'
}
</script>

<style scoped>
/* ── Back button ── */
.back-btn {
  margin-bottom: var(--space-6);
  gap: 6px;
}

/* ── Logo image ── */
.gc-logo-img {
  height: 22px;
  width: auto;
  opacity: 0.95;
}

/* ── Hero Layout ── */
.detail-hero {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: var(--space-10);
  margin-bottom: var(--space-12);
  align-items: start;
}

.hero-card-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  perspective: 800px;
}

/* ── Large Gift Card ── */
.gift-card-detail {
  max-width: 420px !important;
  min-height: 240px;
  padding: var(--space-8) var(--space-8) var(--space-8) var(--space-8) !important;
  border-radius: 16px !important;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  transition: transform 0.4s cubic-bezier(0.03, 0.98, 0.52, 0.99),
              box-shadow 0.4s ease;
  will-change: transform;
}
.gift-card-detail:hover {
  transform: none !important; /* Handled by JS tilt */
  box-shadow:
    0 30px 60px -15px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
}

/* Chip decoration */
.gc-chip {
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
.gc-chip::after {
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
}

/* ── Info Panel ── */
.hero-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding-top: var(--space-2);
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-id {
  font-family: monospace;
  letter-spacing: 0.1em;
}

/* Balance hero */
.balance-hero {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.balance-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
}
.balance-amount {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
  background: linear-gradient(135deg, #000 0%, #333 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.balance-initial {
  font-size: 0.8125rem;
  font-weight: 400;
  margin-top: 4px;
}

/* ── Usage bar ── */
.usage-section {
  padding: var(--space-5) var(--space-6);
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
}
.usage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}
.usage-track {
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}
.usage-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.usage-low { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.usage-mid { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.usage-high { background: linear-gradient(90deg, #EF4444, #F87171); }

.usage-labels {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
}

/* ── Info chips ── */
.info-chips {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}
.info-chip {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}
.info-chip:hover {
  border-color: var(--color-muted);
  box-shadow: var(--shadow-subtle);
}
.info-chip svg {
  color: var(--color-muted);
  flex-shrink: 0;
}
.info-chip div {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}
.chip-label {
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  font-weight: 500;
}
.chip-value {
  font-size: 0.8125rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Transactions List ── */
.tx-list {
  display: flex;
  flex-direction: column;
}
.tx-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  transition: background var(--transition-fast);
}
.tx-item:last-child {
  border-bottom: none;
}
.tx-item:hover {
  background: var(--color-surface-hover);
}
.tx-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 16px;
}
.tx-icon-default-debit { background: rgba(239, 68, 68, 0.1); color: var(--color-destructive); }
.tx-icon-default-credit { background: rgba(34, 197, 94, 0.1); color: var(--color-success); }

.tx-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.tx-title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--color-foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tx-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.tx-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.tx-ref {
  font-family: monospace;
  letter-spacing: 0.05em;
  background: var(--color-bg-body);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  color: var(--color-foreground);
}

.tx-amount-wrapper {
  text-align: right;
  margin-left: 16px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}
.tx-amount {
  font-weight: 700;
  font-size: 1rem;
}

.tx-debit { color: var(--color-destructive); }
.tx-credit { color: var(--color-success); }

/* ── Gratuita Warning Banner ── */
.gratuita-warning {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border: 2px solid #F59E0B;
  border-radius: var(--radius-md);
  animation: warningPulse 2s ease-in-out infinite;
}
.gratuita-warning-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F59E0B;
  border-radius: 50%;
  color: #fff;
}
.gratuita-warning-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.gratuita-warning-text strong {
  font-size: 0.9375rem;
  font-weight: 800;
  color: #92400E;
  letter-spacing: 0.02em;
}
.gratuita-warning-text span {
  font-size: 0.8125rem;
  color: #78350F;
  line-height: 1.4;
}
@keyframes warningPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.3); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .detail-hero {
    grid-template-columns: 1fr;
    gap: var(--space-8);
  }
  .hero-card-wrapper {
    justify-content: center;
  }
  .gift-card-detail {
    max-width: 380px !important;
  }
  .info-chips {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .gift-card-detail {
    max-width: 100% !important;
    min-height: 200px;
    padding: var(--space-6) !important;
  }
  .balance-amount {
    font-size: 2rem;
  }
  .info-chips {
    grid-template-columns: 1fr;
  }
  
  .tx-item {
    padding: 16px;
  }
  .tx-icon-wrapper {
    width: 32px;
    height: 32px;
    margin-right: 12px;
  }
  .tx-icon-wrapper svg {
    width: 16px;
    height: 16px;
  }
  .tx-title {
    font-size: 0.875rem;
  }
  .tx-amount {
    font-size: 0.9375rem;
  }
}
</style>
