<template>
  <div class="movimientos-page">

    <!-- Filter -->
    <div class="filters fade-up" style="animation-delay: 80ms">
      <div class="search-bar" style="max-width:320px">
        <span class="search-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </span>
        <input
          type="text"
          v-model="search"
          placeholder="Buscar por descripción..."
        />
      </div>
      <div class="filter-pills">
        <button
          v-for="f in filters" :key="f.value"
          class="filter-pill"
          :class="{ active: activeFilter === f.value }"
          @click="activeFilter = f.value"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span class="text-muted text-sm" style="margin-top:16px">Cargando movimientos...</span>
    </div>

    <!-- Transactions -->
    <div v-else class="card fade-up" style="animation-delay: 160ms">
      <div class="card-body" style="padding:0;" v-if="filteredTx.length">
        <div class="tx-list">
          <div v-for="tx in filteredTx" :key="tx.id" class="tx-item">
            <div class="tx-icon-wrapper" :class="tx.tipo === 'compra' ? 'tx-icon-compra' : 'tx-icon-recarga'">
              <svg v-if="tx.tipo === 'compra'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
            </div>
            
            <div class="tx-info">
              <div class="tx-title" :title="tx.descripcion">{{ tx.descripcion }}</div>
              <div class="tx-meta">
                <span class="tx-meta-item text-muted">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  {{ formatDate(tx.fecha) }}
                </span>
                <span class="tx-meta-item tx-card-number">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>
                  {{ tx.numero_tarjeta }}
                </span>
              </div>
            </div>
            
            <div class="tx-amount-wrapper">
              <div class="tx-amount" :class="tx.tipo === 'compra' ? 'tx-debit' : 'tx-credit'">
                {{ tx.tipo === 'compra' ? '-' : '+' }}${{ formatMoney(tx.monto) }}
              </div>
              <span class="badge" :class="tx.tipo === 'compra' ? 'badge-destructive' : 'badge-success'" style="font-size:0.65rem; padding: 2px 6px;">
                {{ tx.tipo }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="card-body">
        <div class="empty-state">
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
          <p class="text-secondary" style="margin-top:8px">No se encontraron transacciones con los filtros actuales.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const allTransactions = ref([])
const loading = ref(true)
const search = ref('')
const activeFilter = ref('all')

const filters = [
  { label: 'Todos', value: 'all' },
  { label: 'Compras', value: 'compra' },
  { label: 'Recargas', value: 'recarga' },
]

/**
 * Normaliza el tipo de transacción que viene de SAP.
 * SAP devuelve: VENTA, CONSUMO, RECARGA, GENERACION, etc.
 * El frontend usa: compra, recarga.
 */
const normalizeTipo = (tipo) => {
  if (!tipo) return 'compra'
  const t = tipo.toUpperCase()
  if (['RECARGA', 'GENERACION', 'ACTIVACION'].includes(t)) return 'recarga'
  return 'compra' // VENTA, CONSUMO, etc.
}

onMounted(async () => {
  const clienteStr = localStorage.getItem('cliente')
  if (!clienteStr) {
    router.push('/login')
    return
  }
  try {
    const cliente = JSON.parse(clienteStr)
    const res = await api.getGiftCards({ cedula: cliente.cedula })
    const cards = res.data.results || []
    const txPromises = cards.map(gc =>
      api.getGiftCard(gc.id).then(r => (r.data.transactions || []).map(tx => ({
        ...tx,
        tipo: normalizeTipo(tx.tipo),
        numero_tarjeta: gc.numero_tarjeta || tx.numero_tarjeta
      })))
    )
    const txArrays = await Promise.all(txPromises)
    allTransactions.value = txArrays.flat().sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
  } catch (e) { console.error('Error cargando movimientos:', e) }
  finally { loading.value = false }
})

const filteredTx = computed(() => {
  let txs = allTransactions.value
  if (activeFilter.value !== 'all') {
    txs = txs.filter(t => t.tipo === activeFilter.value)
  }
  if (search.value) {
    const s = search.value.toLowerCase()
    txs = txs.filter(t => (t.descripcion || '').toLowerCase().includes(s))
  }
  return txs
})

const formatMoney = (v) => Math.abs(Number(v || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'
</script>

<style scoped>
.filters {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}
.filter-pills {
  display: flex;
  gap: var(--space-2);
}
.filter-pill {
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-full);
  color: var(--color-muted);
  transition: all var(--transition-fast);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
}
.filter-pill:hover {
  color: var(--color-foreground);
  background: var(--color-surface-hover);
}
.filter-pill.active {
  color: var(--color-primary-inverse);
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.tx-debit { color: var(--color-destructive); }
.tx-credit { color: var(--color-success); }

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
.tx-icon-compra { background: rgba(239, 68, 68, 0.1); color: var(--color-destructive); }
.tx-icon-recarga { background: rgba(34, 197, 94, 0.1); color: var(--color-success); }

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
.tx-card-number {
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

/* ── Responsive ── */
@media (max-width: 640px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  .search-bar {
    max-width: 100% !important;
  }
  .filter-pills {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 4px;
  }
  .filter-pill {
    white-space: nowrap;
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
