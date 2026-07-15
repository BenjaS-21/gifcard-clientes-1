<template>
  <div class="client-detail" v-if="client">
    <div class="page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="$router.push('/clientes')" style="margin-bottom:8px">&#9664; Volver a Clientes</button>
        <h1>
          <div class="client-avatar-lg">{{ client.nombre?.charAt(0) }}</div>
          {{ client.nombre }}
        </h1>
        <p class="page-header-subtitle">{{ client.cedula }} &bull; {{ client.email }}</p>
      </div>
    </div>

    <!-- Client Info -->
    <div class="grid-stats" style="margin-bottom:24px">
      <StatCard :value="client.giftcards?.length || 0" label="Gift Cards" icon="&#127873;" iconBg="rgba(227,24,55,0.1)" />
      <StatCard :value="totalBalance" label="Saldo Total" icon="&#128176;" iconBg="rgba(46,125,50,0.1)" :isMoney="true" prefix="$" :delay="80" />
      <StatCard :value="activeCards" label="Activas" icon="&#9989;" iconBg="rgba(46,125,50,0.1)" :delay="160" />
    </div>

    <!-- Gift Cards con Movimientos -->
    <div v-for="gc in client.giftcards" :key="gc.id" class="card" style="margin-bottom:24px">
      <div class="card-header" style="display:flex;justify-content:space-between;align-items:center;cursor:pointer" @click="$router.push('/giftcards/' + gc.id)">
        <h3 style="display:flex;align-items:center;gap:8px">
          &#127873; {{ gc.numero_tarjeta }}
          <span class="badge" :class="gc.estado?.toLowerCase() === 'activa' ? 'badge-success' : 'badge-muted'" style="font-size:0.7rem">
            {{ gc.estado }}
          </span>
        </h3>
        <span style="font-weight:700;font-size:1.1rem" :style="{ color: gc.saldo <= 0 ? 'var(--color-danger)' : '' }">
          ${{ formatMoney(gc.saldo) }}
        </span>
      </div>

      <!-- Barra de consumo -->
      <div class="gc-usage" style="padding:12px 16px;border-bottom:1px solid var(--color-border-light, rgba(0,0,0,0.06))">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span class="text-xs text-muted">Consumido</span>
          <span class="text-xs" style="font-weight:600" :style="{ color: getUsagePct(gc) >= 100 ? 'var(--color-danger)' : '' }">{{ getUsagePct(gc) }}%</span>
        </div>
        <div class="usage-track">
          <div class="usage-fill" :class="getUsageColor(gc)" :style="{ width: getUsagePct(gc) + '%' }"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:4px">
          <span class="text-xs text-muted">Usado: ${{ formatMoney(getConsumed(gc)) }}</span>
          <span class="text-xs text-muted">Disponible: ${{ formatMoney(gc.saldo) }}</span>
        </div>
        <div v-if="gc.saldo <= 0" style="margin-top:8px;padding:6px 12px;background:rgba(227,24,55,0.08);border-radius:6px;text-align:center">
          <span style="color:var(--color-danger);font-weight:600;font-size:0.8rem">⚠ Saldo agotado — 0% disponible</span>
        </div>
      </div>

      <!-- Transacciones de esta GC -->
      <div class="card-body" style="padding:0" v-if="gc.transactions?.length">
        <table class="table-minimal">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Descripción</th>
              <th style="text-align:right">Monto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tx in gc.transactions" :key="tx.id + '-' + tx.referencia">
              <td class="text-sm text-muted">{{ formatDate(tx.fecha) }}</td>
              <td>
                <span class="badge" :class="isDebit(tx) ? 'badge-destructive' : 'badge-success'" style="font-size:0.65rem;padding:2px 6px">
                  {{ tx.tipo }}
                </span>
              </td>
              <td class="text-sm">{{ tx.descripcion }}</td>
              <td style="text-align:right;font-weight:700" :style="{ color: isDebit(tx) ? 'var(--color-danger)' : 'var(--color-success)' }">
                {{ isDebit(tx) ? '-' : '+' }}${{ formatMoney(tx.monto) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card-body" v-else>
        <p class="text-muted text-sm" style="text-align:center;padding:12px 0">Sin movimientos registrados</p>
      </div>
    </div>

    <div v-if="!client.giftcards?.length" class="card">
      <div class="card-body">
        <div class="empty-state">
          <div class="empty-icon">&#127873;</div>
          <h3>Sin gift cards</h3>
          <p class="text-muted">Este cliente no tiene gift cards asociadas</p>
        </div>
      </div>
    </div>

    <!-- Client Details -->
    <div class="card">
      <div class="card-header"><h3>Información del Cliente</h3></div>
      <div class="card-body">
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Nombre completo</span>
            <span class="detail-value">{{ client.nombre }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Cédula</span>
            <span class="detail-value">{{ client.cedula }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ client.email }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Teléfono</span>
            <span class="detail-value">{{ client.telefono }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Dirección</span>
            <span class="detail-value">{{ client.direccion }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fecha Registro</span>
            <span class="detail-value">{{ client.fecha_registro }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading-spinner"><div class="spinner"></div><span class="text-muted">Cargando...</span></div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import GiftCard from '../components/ui/GiftCard.vue'
import StatCard from '../components/ui/StatCard.vue'

const route = useRoute()
const client = ref(null)

onMounted(async () => {
  try {
    const res = await api.getClient(route.params.id)
    client.value = res.data
  } catch (e) { console.error(e) }
})

const totalBalance = computed(() => (client.value?.giftcards || []).reduce((sum, gc) => sum + (gc.saldo || 0), 0))
const activeCards = computed(() => (client.value?.giftcards || []).filter(gc => (gc.estado || '').toLowerCase() === 'activa').length)

const formatMoney = (v) => Math.abs(Number(v || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2 })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'

/* Determina si una transacción es débito basado en tipo */
const DEBIT_TYPES = ['USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO']
const isDebit = (tx) => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase())

/* Cálculos de consumo por gift card */
const getConsumed = (gc) => Math.max((gc.saldo_inicial || 0) - (gc.saldo || 0), 0)
const getUsagePct = (gc) => {
  const ini = gc.saldo_inicial || 0
  if (ini <= 0) return 0
  return Math.min(Math.round((getConsumed(gc) / ini) * 100), 100)
}
const getUsageColor = (gc) => {
  const pct = getUsagePct(gc)
  if (pct >= 100) return 'usage-danger'
  if (pct >= 75) return 'usage-warning'
  return 'usage-ok'
}
</script>

<style scoped>
.client-avatar-lg {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 800; font-size: 1.2rem; flex-shrink: 0;
}
.detail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 24px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; }
.detail-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: var(--color-text-secondary); letter-spacing: 0.05em; }
.detail-value { font-size: 0.95rem; font-weight: 500; }
.table-minimal { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.table-minimal th { text-align: left; padding: 10px 16px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-secondary); border-bottom: 1px solid var(--color-border); }
.table-minimal td { padding: 10px 16px; border-bottom: 1px solid var(--color-border-light, rgba(0,0,0,0.05)); }
.table-minimal tr:last-child td { border-bottom: none; }
.usage-track { height: 6px; background: var(--color-border-light, rgba(0,0,0,0.08)); border-radius: 3px; overflow: hidden; }
.usage-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }
.usage-ok { background: var(--color-success, #2e7d32); }
.usage-warning { background: #f59e0b; }
.usage-danger { background: var(--color-danger, #e31837); }
</style>
