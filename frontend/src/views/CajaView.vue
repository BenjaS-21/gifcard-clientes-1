<template>
  <!-- PIN Gate -->
  <div v-if="!cajaAuthed" class="pin-page">
    <div class="pin-card fade-up">
      <div class="pin-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      </div>
      <h2 class="pin-title">Acceso Caja</h2>
      <p class="pin-subtitle">Ingresa el PIN de cajera para continuar</p>
      <form @submit.prevent="validatePin" class="pin-form">
        <input
          type="password"
          v-model="pinInput"
          class="form-input pin-input"
          placeholder="••••••••"
          autofocus
        />
        <p v-if="pinError" class="pin-error">{{ pinError }}</p>
        <button type="submit" class="btn btn-primary btn-lg pin-submit">Ingresar</button>
      </form>
    </div>
  </div>

  <!-- Caja Content -->
  <div v-else class="caja-page">

    <!-- Search Section -->
    <div class="caja-search-section fade-up">
      <div class="caja-search-header">
        <div class="caja-search-icon-wrapper">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
        </div>
        <div>
          <h1 class="caja-title">Consulta de Tarjeta</h1>
          <p class="caja-subtitle">Ingresa el número de la tarjeta para ver sus datos</p>
        </div>
      </div>

      <form @submit.prevent="buscarTarjeta" class="caja-search-form">
        <div class="caja-search-row">
          <button type="button" class="copy-btn copy-btn-search" v-if="numeroTarjeta.trim()" @click="copyInput" :title="copied ? '¡Copiado!' : 'Copiar código'">
            <svg v-if="!copied" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </button>
          <div class="caja-input-group">
            <span class="caja-input-prefix">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </span>
            <input
              type="text"
              v-model="numeroTarjeta"
              placeholder="Ej: DAM-2024-0001"
              class="caja-input"
              autofocus
            />
            <button type="submit" class="btn btn-primary caja-search-btn" :disabled="searching || !numeroTarjeta.trim()">
              <span v-if="searching" class="spinner spinner-sm"></span>
              <span v-else>Consultar</span>
            </button>
          </div>
        </div>
        <p v-if="error" class="caja-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ error }}
        </p>
      </form>
    </div>

    <!-- Loading -->
    <div v-if="searching" class="loading-spinner" style="margin-top:var(--space-10)">
      <div class="spinner"></div>
      <span class="text-muted text-sm" style="margin-top:16px">Buscando tarjeta...</span>
    </div>

    <!-- Results -->
    <div v-if="gc && !searching" class="caja-results fade-up" style="animation-delay:100ms">

      <!-- Hero -->
      <div class="detail-hero">
        <div class="hero-card-wrapper">
          <div class="gift-card gift-card-detail" :class="'gc-' + (gc.color || 'black')" :style="cardBgStyle" ref="cardEl">
            <div class="gc-type-label">GIFT CARD</div>
            <div class="gc-pattern"></div>
            <div class="gc-logo">
              <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="gc-logo-img" />
            </div>
            <div class="gc-number">
              {{ gc.numero_tarjeta }}
              <button class="copy-btn copy-btn-card" data-export-ignore @click.stop="copyCode" :title="copied ? 'Copiado!' : 'Copiar código'">
                <svg v-if="!copied" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </button>
            </div>
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

        <div class="hero-info">
          <div class="status-row">
            <span class="badge" :class="statusClass(gc.estado)">{{ gc.estado }}</span>
            <button
              v-if="canActivate"
              class="btn btn-activate"
              @click="showActivateModal = true"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Activar
            </button>
            <span class="card-id text-xs text-muted">
              {{ gc.numero_tarjeta }}
              <button class="copy-btn copy-btn-info" @click.stop="copyCode" :title="copied ? 'Copiado!' : 'Copiar código'">
                <svg v-if="!copied" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </button>
            </span>
          </div>

          <!-- Gratuita Warning -->
          <div v-if="gc.gratuita === 'Y'" class="gratuita-warning">
            <div class="gratuita-warning-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <div class="gratuita-warning-text">
              <strong>NO DISPONIBLE PARA USO CON CASHEA</strong>
              <span>Esta tarjeta es de tipo gratuita/cortesía y solo puede ser utilizada directamente en tienda.</span>
            </div>
          </div>

          <div class="balance-hero">
            <span class="balance-label">Saldo Actual</span>
            <span class="balance-amount">${{ formatMoney(gc.saldo) }}</span>
            <span class="balance-initial text-muted">de ${{ formatMoney(gc.saldo_inicial) }} inicial</span>
          </div>

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
              <span class="text-xs text-muted">Disponible: ${{ formatMoney(gc.saldo) }}</span>
            </div>
          </div>

          <div class="info-chips">
            <div class="info-chip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <div>
                <span class="chip-label">Cliente</span>
                <span class="chip-value">{{ gc.cliente_nombre || '-' }}</span>
              </div>
            </div>
            <div class="info-chip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              <div>
                <span class="chip-label">Emisión</span>
                <span class="chip-value">{{ formatDate(gc.fecha_emision) }}</span>
              </div>
            </div>
            <div class="info-chip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <div>
                <span class="chip-label">Vencimiento</span>
                <span class="chip-value">{{ formatDate(gc.fecha_vencimiento) }}</span>
              </div>
            </div>
            <div class="info-chip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <div>
                <span class="chip-label">Cédula</span>
                <span class="chip-value">{{ gc.cliente_cedula || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Transactions -->
      <div class="section fade-up" style="animation-delay:200ms">
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
                <div class="tx-icon-wrapper" :class="isDebit(tx) ? 'tx-icon-debit' : 'tx-icon-credit'">
                  <svg v-if="isDebit(tx)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
                </div>
                <div class="tx-info">
                  <div class="tx-title">{{ tx.descripcion }}</div>
                  <div class="tx-meta">
                    <span class="tx-meta-item text-muted">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                      {{ formatDate(tx.fecha) }}
                    </span>
                    <span class="tx-meta-item tx-ref" v-if="tx.referencia">Ref: {{ tx.referencia }}</span>
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
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              </div>
              <h3>Sin movimientos</h3>
              <p class="text-secondary" style="margin-top:8px">No hay transacciones registradas.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- New Search Button -->
      <div class="caja-new-search fade-up" style="animation-delay:300ms">
        <button class="btn btn-ghost btn-sm" @click="resetSearch">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          Nueva consulta
        </button>
      </div>
    </div>

    <!-- Modal Activar -->
    <Teleport to="body">
      <div v-if="showActivateModal" class="modal-overlay" @click.self="closeActivateModal">
        <div class="modal-card activate-modal fade-up">
          <div class="modal-header">
            <h3 class="modal-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Activar Tarjeta
            </h3>
            <button class="modal-close" @click="closeActivateModal">&times;</button>
          </div>
          <div class="modal-body">
            <p class="text-muted text-sm" style="margin-bottom:var(--space-4)">Ingresa los datos del beneficiario para activar <strong>{{ gc?.numero_tarjeta }}</strong></p>
            <div class="form-group">
              <label class="form-label">Nombre del Beneficiario</label>
              <input type="text" v-model="activateNombre" class="form-input" placeholder="Ej: María García López" autofocus />
            </div>
            <div class="form-group">
              <label class="form-label">Cédula</label>
              <div class="cedula-row">
                <select v-model="activateCedulaTipo" class="form-select cedula-tipo">
                  <option value="V">V</option>
                  <option value="J">J</option>
                  <option value="E">E</option>
                </select>
                <input type="text" v-model="activateCedula" class="form-input cedula-numero" placeholder="12345678" inputmode="numeric" @input="onCedulaInput" />
              </div>
            </div>
            <p v-if="activateError" class="caja-error" style="margin-top:var(--space-3)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              {{ activateError }}
            </p>
            <p v-if="activateSuccess" class="activate-success">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              {{ activateSuccess }}
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost btn-sm" @click="closeActivateModal" :disabled="activating">Cancelar</button>
            <button class="btn btn-primary btn-sm" @click="activateCard" :disabled="activating || !activateNombre.trim() || !activateCedula.trim()">
              <span v-if="activating" class="spinner spinner-sm"></span>
              <span v-else>Confirmar Activación</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { useCardDownload } from '../composables/useCardDownload'

// ── PIN Gate ──
const CAJA_PIN = 'Damasco2026*'
const cajaAuthed = ref(sessionStorage.getItem('cajaAuth') === 'true')
const pinInput = ref('')
const pinError = ref('')

const validatePin = () => {
  if (pinInput.value === CAJA_PIN) {
    sessionStorage.setItem('cajaAuth', 'true')
    cajaAuthed.value = true
    pinError.value = ''
  } else {
    pinError.value = 'PIN incorrecto'
    pinInput.value = ''
  }
}

// ── Caja state ──
const route = useRoute()
const numeroTarjeta = ref('')
const gc = ref(null)
const searching = ref(false)
const error = ref('')
const copied = ref(false)
let copiedTimeout = null

// Activation modal state
const showActivateModal = ref(false)
const activateNombre = ref('')
const activateCedulaTipo = ref('V')
const activateCedula = ref('')
const activating = ref(false)
const activateError = ref('')
const activateSuccess = ref('')
const canActivate = computed(() => {
  if (!gc.value) return false
  const estado = (gc.value.estado || '').toUpperCase()
  // Don't show if already ACTIVA
  if (estado === 'ACTIVA') return false
  // Don't show if already has a beneficiary assigned
  if (gc.value.cliente_nombre && gc.value.cliente_cedula) return false
  return true
})

// Descarga de la tarjeta como imagen (para enviar por correo)
const cardEl = ref(null)
const { downloading, downloadCard } = useCardDownload()

// Dynamic card background
const cardBgUrl = ref(null)
const cardBgStyle = computed(() => cardBgUrl.value ? { backgroundImage: `url(${cardBgUrl.value})` } : {})

onMounted(async () => {
  // Load active template
  try {
    const tpl = await api.getActiveTemplate()
    if (tpl.data.active) cardBgUrl.value = tpl.data.image_url
  } catch (e) { /* usa imagen por defecto */ }
  const num = route.query.numero
  if (num) {
    numeroTarjeta.value = num
    buscarTarjeta()
  }
})

const buscarTarjeta = async () => {
  if (!numeroTarjeta.value.trim()) return
  searching.value = true
  error.value = ''
  gc.value = null

  try {
    const res = await api.lookupGiftCard(numeroTarjeta.value.trim())
    gc.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al buscar la tarjeta'
  } finally {
    searching.value = false
  }
}

const resetSearch = () => {
  gc.value = null
  numeroTarjeta.value = ''
  error.value = ''
  copied.value = false
}

const consumed = computed(() => (gc.value?.saldo_inicial || 0) - (gc.value?.saldo || 0))
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
const formatDate = (d) => {
  if (!d) return '-'
  // SAP puede devolver dd/mm/yyyy o yyyy-mm-dd
  let parsed = new Date(d)
  if (isNaN(parsed.getTime()) && typeof d === 'string' && d.includes('/')) {
    const [day, month, year] = d.split('/')
    parsed = new Date(`${year}-${month}-${day}`)
  }
  return isNaN(parsed.getTime()) ? d : parsed.toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' })
}
const statusClass = (s) => {
  const key = (s || '').toUpperCase()
  return {
    VENDIDA: 'badge-info',
    GENERADA: 'badge-warning',
    ACTIVA: 'badge-success',
    VENCIDA: 'badge-muted',
    AGOTADA: 'badge-muted',
    BLOQUEADA: 'badge-destructive',
  }[key] || 'badge-muted'
}

/* Determina si una transacción es débito (gasto) basándose en el tipo */
const DEBIT_TYPES = ['USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO']
const isDebit = (tx) => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase())

const copyCode = async () => {
  if (!gc.value?.numero_tarjeta) return
  try {
    await navigator.clipboard.writeText(gc.value.numero_tarjeta)
    copied.value = true
    clearTimeout(copiedTimeout)
    copiedTimeout = setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback for older browsers
    const ta = document.createElement('textarea')
    ta.value = gc.value.numero_tarjeta
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    clearTimeout(copiedTimeout)
    copiedTimeout = setTimeout(() => { copied.value = false }, 2000)
  }
}

const copyInput = async () => {
  const text = numeroTarjeta.value.trim()
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    clearTimeout(copiedTimeout)
    copiedTimeout = setTimeout(() => { copied.value = false }, 2000)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    clearTimeout(copiedTimeout)
    copiedTimeout = setTimeout(() => { copied.value = false }, 2000)
  }
}

const closeActivateModal = () => {
  showActivateModal.value = false
  activateNombre.value = ''
  activateCedulaTipo.value = 'V'
  activateCedula.value = ''
  activateError.value = ''
  activateSuccess.value = ''
}

const onCedulaInput = () => {
  activateCedula.value = activateCedula.value.replace(/\D/g, '')
}

const activateCard = async () => {
  if (!activateNombre.value.trim() || !activateCedula.value.trim()) return
  activating.value = true
  activateError.value = ''
  activateSuccess.value = ''

  try {
    const cedulaFull = `${activateCedulaTipo.value}-${activateCedula.value.trim()}`
    const res = await api.activateGiftCard({
      codigo: gc.value.numero_tarjeta,
      nombre: activateNombre.value.trim(),
      cedula: cedulaFull
    })
    activateSuccess.value = res.data.message || 'Tarjeta activada exitosamente'
    // Update local card state
    gc.value.estado = 'ACTIVA'
    gc.value.cliente_nombre = activateNombre.value.trim()
    gc.value.cliente_cedula = activateCedula.value.trim()
    // Auto-close after 2s
    setTimeout(() => closeActivateModal(), 2000)
  } catch (e) {
    activateError.value = e.response?.data?.error || 'Error al activar la tarjeta'
  } finally {
    activating.value = false
  }
}
</script>

<style scoped>
/* ── PIN Gate ── */
.pin-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--color-bg); padding: var(--space-4); position: relative; overflow: hidden;
}
.pin-page::before {
  content: ''; position: absolute; top: -20vh; left: 50%; transform: translateX(-50%);
  width: 80vw; height: 80vw; max-width: 800px; max-height: 800px;
  background: radial-gradient(circle, rgba(200,16,46,0.04) 0%, transparent 60%); pointer-events: none;
}
.pin-card {
  width: 100%; max-width: 380px; background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0,0,0,0.08); border-radius: var(--radius-lg);
  padding: var(--space-10) var(--space-8); box-shadow: var(--shadow-hover);
  text-align: center; position: relative; z-index: 1;
}
.pin-icon {
  width: 64px; height: 64px; margin: 0 auto var(--space-5);
  background: rgba(200,16,46,0.06); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.pin-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 6px; }
.pin-subtitle { font-size: 0.875rem; color: var(--color-muted); margin: 0 0 var(--space-6); }
.pin-form { display: flex; flex-direction: column; gap: var(--space-4); }
.pin-input { text-align: center; font-size: 1.125rem; letter-spacing: 4px; }
.pin-submit { width: 100%; }
.pin-error {
  color: var(--color-destructive); font-size: 0.8125rem; text-align: center; margin: 0;
  padding: 8px; background: rgba(239,68,68,0.08); border-radius: var(--radius-sm);
}

/* ── Search Section ── */
.caja-search-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin-bottom: var(--space-8);
  box-shadow: var(--shadow-subtle);
}
.caja-search-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}
.caja-search-icon-wrapper {
  width: 52px; height: 52px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(200,16,46,0.1) 0%, rgba(200,16,46,0.05) 100%);
  color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.caja-title {
  font-size: 1.375rem; font-weight: 700; letter-spacing: -0.02em;
  margin: 0; line-height: 1.2;
}
.caja-subtitle {
  font-size: 0.875rem; color: var(--color-muted); margin: 4px 0 0;
}

/* Input Group */
.caja-input-group {
  display: flex; align-items: center; gap: 0;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
  background: var(--color-bg-body);
}
.caja-input-group:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(200,16,46,0.1);
}
.caja-input-prefix {
  display: flex; align-items: center; justify-content: center;
  padding: 0 var(--space-4); color: var(--color-muted);
}
.caja-input {
  flex: 1; border: none; outline: none; background: transparent;
  font-size: 1rem; padding: 14px 0;
  font-family: 'SF Mono', SFMono-Regular, monospace;
  letter-spacing: 0.05em; font-weight: 500;
}
.caja-input::placeholder { color: var(--color-muted); opacity: 0.6; font-family: inherit; }
.caja-search-btn {
  border-radius: 0; padding: 14px 24px; font-weight: 600;
  white-space: nowrap; flex-shrink: 0;
}

/* Error */
.caja-error {
  display: flex; align-items: center; gap: 8px;
  margin-top: var(--space-3); padding: 10px 14px;
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
  border-radius: var(--radius-sm); color: var(--color-destructive);
  font-size: 0.875rem; font-weight: 500;
}

/* ── Results ── */
.gc-logo-img { height: 22px; width: auto; opacity: 0.95; }

.detail-hero {
  display: grid; grid-template-columns: 420px 1fr;
  gap: var(--space-10); margin-bottom: var(--space-12); align-items: start;
}
.hero-card-wrapper { display: flex; flex-direction: column; align-items: center; gap: var(--space-4); }
.gift-card-detail {
  max-width: 420px !important; min-height: 240px;
  padding: var(--space-8) !important; border-radius: 16px !important;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05) inset;
}
.gc-chip {
  position: absolute; top: 50%; right: 28px; transform: translateY(-50%);
  width: 40px; height: 28px; border-radius: 6px;
  background: linear-gradient(135deg, #d4af37 0%, #f5d779 40%, #c9a227 60%, #e8c84a 100%);
  opacity: 0.8; z-index: 2;
}
.gc-pattern {
  position: absolute; top: 0; right: 0; width: 100%; height: 100%; opacity: 0.06;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,1) 20px, rgba(255,255,255,1) 21px);
  pointer-events: none; z-index: 1;
}

.hero-info { display: flex; flex-direction: column; gap: var(--space-6); padding-top: var(--space-2); }
.status-row { display: flex; align-items: center; justify-content: space-between; }
.card-id { font-family: monospace; letter-spacing: 0.1em; display: inline-flex; align-items: center; gap: 4px; }

/* Copy button */
.copy-btn {
  display: inline-flex; align-items: center; justify-content: center;
  background: none; border: none; cursor: pointer; padding: 4px;
  border-radius: 4px; transition: all 0.2s ease;
  line-height: 1; vertical-align: middle; flex-shrink: 0;
}
.copy-btn:active { transform: scale(0.9); }
.copy-btn-card {
  color: rgba(255,255,255,0.5); margin-left: 6px;
}
.copy-btn-card:hover { color: rgba(255,255,255,0.9); background: rgba(255,255,255,0.1); }
.copy-btn-info {
  color: var(--color-muted);
}
.copy-btn-info:hover { color: var(--color-foreground); background: var(--color-surface-hover); }
.copy-btn-search {
  width: 42px; height: 42px; border-radius: var(--radius-md);
  color: var(--color-muted); background: var(--color-bg-card);
  border: 1px solid var(--color-border); flex-shrink: 0;
  padding: 0;
}
.copy-btn-search:hover { color: var(--color-primary); border-color: var(--color-primary); background: rgba(200,16,46,0.04); }
.caja-search-row { display: flex; align-items: center; gap: var(--space-3); }
.caja-search-row .caja-input-group { flex: 1; }
.balance-hero { display: flex; flex-direction: column; gap: 2px; }
.balance-label { font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-muted); }
.balance-amount { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; background: linear-gradient(135deg, #000 0%, #333 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.balance-initial { font-size: 0.8125rem; margin-top: 4px; }

.usage-section { padding: var(--space-5) var(--space-6); background: var(--color-surface-hover); border-radius: var(--radius-md); }
.usage-header { display: flex; justify-content: space-between; margin-bottom: var(--space-2); }
.usage-track { height: 8px; background: var(--color-border); border-radius: 4px; overflow: hidden; }
.usage-fill { height: 100%; border-radius: 4px; transition: width 1.2s cubic-bezier(0.16,1,0.3,1); }
.usage-low { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.usage-mid { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.usage-high { background: linear-gradient(90deg, #EF4444, #F87171); }
.usage-labels { display: flex; justify-content: space-between; margin-top: var(--space-2); }

.info-chips { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.info-chip { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-4); background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-sm); transition: all var(--transition-base); }
.info-chip:hover { border-color: var(--color-muted); box-shadow: var(--shadow-subtle); }
.info-chip svg { color: var(--color-muted); flex-shrink: 0; }
.info-chip div { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.chip-label { font-size: 0.625rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-muted); font-weight: 500; }
.chip-value { font-size: 0.8125rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Transactions */
.tx-list { display: flex; flex-direction: column; }
.tx-item { display: flex; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--color-border); transition: background var(--transition-fast); }
.tx-item:last-child { border-bottom: none; }
.tx-item:hover { background: var(--color-surface-hover); }
.tx-icon-wrapper { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 16px; }
.tx-icon-debit { background: rgba(239,68,68,0.1); color: var(--color-destructive); }
.tx-icon-credit { background: rgba(34,197,94,0.1); color: var(--color-success); }
.tx-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.tx-title { font-weight: 600; font-size: 0.9375rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tx-meta { display: flex; align-items: center; gap: 12px; font-size: 0.75rem; color: var(--color-muted); }
.tx-meta-item { display: flex; align-items: center; gap: 4px; }
.tx-ref { font-family: monospace; letter-spacing: 0.05em; background: var(--color-bg-body); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--color-border); color: var(--color-foreground); }
.tx-amount-wrapper { text-align: right; margin-left: 16px; flex-shrink: 0; }
.tx-amount { font-weight: 700; font-size: 1rem; }
.tx-debit { color: var(--color-destructive); }
.tx-credit { color: var(--color-success); }

/* New Search */
.caja-new-search { text-align: center; margin-top: var(--space-6); }
.caja-new-search .btn { gap: 8px; }

/* Spinner small */
.spinner-sm { width: 18px; height: 18px; border-width: 2px; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .detail-hero { grid-template-columns: 1fr; gap: var(--space-8); }
  .gift-card-detail { max-width: 380px !important; }
  .info-chips { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .caja-search-section { padding: var(--space-5); }
  .caja-search-header { flex-direction: column; align-items: flex-start; gap: var(--space-3); }
  .caja-input-group { flex-direction: column; }
  .caja-search-btn { width: 100%; border-radius: 0; }
  .gift-card-detail { max-width: 100% !important; min-height: 200px; padding: var(--space-6) !important; }
  .balance-amount { font-size: 2rem; }
  .info-chips { grid-template-columns: 1fr; }
  .tx-item { padding: 16px; }
  .tx-icon-wrapper { width: 32px; height: 32px; margin-right: 12px; }
}

/* ── Activate Button ── */
.btn-activate {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; font-size: 0.8125rem; font-weight: 600;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff; border: none; cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: 0 2px 8px rgba(34,197,94,0.2);
}
.btn-activate:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(34,197,94,0.3); }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.45); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-4);
}
.modal-card {
  background: var(--color-bg); border-radius: var(--radius-xl);
  box-shadow: var(--shadow-elevated); width: 100%; max-width: 440px;
  overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-5) var(--space-6); border-bottom: 1px solid var(--color-border);
}
.modal-title { font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.modal-close {
  width: 32px; height: 32px; border: none; background: none; cursor: pointer;
  font-size: 1.4rem; color: var(--color-muted); border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition-fast);
}
.modal-close:hover { background: var(--color-surface-hover); color: var(--color-foreground); }
.modal-body { padding: var(--space-6); }
.modal-footer {
  display: flex; justify-content: flex-end; gap: var(--space-3);
  padding: var(--space-4) var(--space-6); border-top: 1px solid var(--color-border);
  background: var(--color-surface-hover);
}

/* ── Form Fields ── */
.form-group { margin-bottom: var(--space-4); }
.form-label { display: block; font-size: 0.8125rem; font-weight: 600; margin-bottom: 6px; color: var(--color-foreground); }
.form-input {
  width: 100%; padding: 10px 14px; font-size: 0.9375rem;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  background: var(--color-bg); color: var(--color-foreground);
  transition: all var(--transition-fast); outline: none;
}
.form-input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(200,16,46,0.08); }
.form-input::placeholder { color: var(--color-muted); }

.cedula-row { display: flex; gap: 8px; }
.cedula-tipo {
  width: 70px; padding: 10px 8px; font-size: 0.9375rem; font-weight: 600;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  background: var(--color-bg); color: var(--color-foreground);
  cursor: pointer; outline: none; text-align: center;
  transition: all var(--transition-fast);
  appearance: none; -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 8px center;
  padding-right: 24px;
}
.cedula-tipo:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(200,16,46,0.08); }
.cedula-numero { flex: 1; }

.activate-success {
  display: flex; align-items: center; gap: 8px;
  color: #16a34a; font-weight: 600; font-size: 0.875rem;
  margin-top: var(--space-3); padding: var(--space-3) var(--space-4);
  background: rgba(34,197,94,0.06); border-radius: var(--radius-sm);
}

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
</style>
