<template>
  <div class="dashboard">
    <!-- Stats Grid -->
    <div class="grid-stats">
      <StatCard
        v-for="(stat, i) in stats" :key="stat.label"
        :value="stat.value" :label="stat.label" :icon="stat.icon"
        :iconBg="stat.bg" :isMoney="stat.isMoney" :prefix="stat.prefix"
        :delay="i * 80"
      />
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      <!-- Recent Transactions -->
      <div class="card fade-in" style="animation-delay: 300ms">
        <div class="card-header">
          <h3>Últimas Transacciones</h3>
          <router-link to="/giftcards" class="btn btn-ghost btn-sm">Ver todas →</router-link>
        </div>
        <div class="card-body" style="padding:0">
          <table class="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tarjeta</th>
                <th>Tipo</th>
                <th style="text-align:right">Monto</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in data.recent_transactions" :key="tx.id">
                <td class="text-sm text-muted">{{ formatDate(tx.fecha) }}</td>
                <td class="text-sm" style="font-weight:600">{{ tx.numero_tarjeta }}</td>
                <td><StatusBadge :status="tx.tipo" :showDot="false" /></td>
                <td style="text-align:right;font-weight:700" :style="{ color: isDebit(tx) ? 'var(--color-danger)' : 'var(--color-success)' }">
                  {{ isDebit(tx) ? '-' : '+' }}${{ formatMoney(tx.monto) }}
                </td>
              </tr>
              <tr v-if="!data.recent_transactions?.length">
                <td colspan="4" class="text-muted" style="text-align:center;padding:32px">Sin transacciones recientes</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Clients -->
      <div class="card fade-in" style="animation-delay: 400ms">
        <div class="card-header">
          <h3>Top Clientes</h3>
          <router-link to="/clientes" class="btn btn-ghost btn-sm">Ver todos →</router-link>
        </div>
        <div class="card-body top-clients-list">
          <div v-for="(client, i) in data.top_clients" :key="client.id" class="top-client-item"
            @click="$router.push('/clientes/' + client.id)">
            <div class="top-client-rank">{{ i + 1 }}</div>
            <div class="top-client-avatar">{{ client.nombre?.charAt(0) || '?' }}</div>
            <div class="top-client-info">
              <div class="top-client-name">{{ client.nombre }}</div>
              <div class="top-client-sub text-sm text-muted">{{ client.total_giftcards || 0 }} tarjetas</div>
            </div>
            <div class="top-client-amount">${{ formatMoney(client.saldo_total) }}</div>
          </div>
          <div v-if="!data.top_clients?.length" class="empty-state" style="padding:24px">
            <p class="text-muted">Sin datos de clientes</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Gift Cards Overview -->
    <div class="card fade-in" style="animation-delay: 500ms; margin-top: 24px">
      <div class="card-header">
        <h3>Distribución de Estados</h3>
      </div>
      <div class="card-body">
        <div class="status-bars">
          <div v-for="bar in statusBars" :key="bar.label" class="status-bar-item">
            <div class="status-bar-header">
              <StatusBadge :status="bar.key" />
              <span class="text-sm" style="font-weight:700">{{ bar.value }}</span>
            </div>
            <div class="status-bar-track">
              <div class="status-bar-fill" :style="{ width: bar.pct + '%', background: bar.color }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import StatCard from '../components/ui/StatCard.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'

const data = ref({})
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.getDashboardStats()
    data.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

const stats = computed(() => [
  { value: data.value.total_giftcards || 0, label: 'Total Gift Cards', icon: '&#127873;', bg: 'rgba(227,24,55,0.1)' },
  { value: data.value.saldo_total || 0, label: 'Saldo Total', icon: '&#128176;', bg: 'rgba(46,125,50,0.1)', isMoney: true, prefix: '$' },
  { value: data.value.activas || 0, label: 'Tarjetas Activas', icon: '&#9989;', bg: 'rgba(46,125,50,0.1)' },
  { value: data.value.total_clientes || 0, label: 'Total Clientes', icon: '&#128101;', bg: 'rgba(21,101,192,0.1)' },
])

const statusBars = computed(() => {
  const total = data.value.total_giftcards || 1
  return [
    { key: 'activa', label: 'Activas', value: data.value.activas || 0, pct: ((data.value.activas || 0) / total * 100), color: 'var(--color-success)' },
    { key: 'vencida', label: 'Vencidas', value: data.value.vencidas || 0, pct: ((data.value.vencidas || 0) / total * 100), color: 'var(--color-warning)' },
    { key: 'agotada', label: 'Agotadas', value: data.value.agotadas || 0, pct: ((data.value.agotadas || 0) / total * 100), color: 'var(--color-text-muted)' },
    { key: 'bloqueada', label: 'Bloqueadas', value: data.value.bloqueadas || 0, pct: ((data.value.bloqueadas || 0) / total * 100), color: 'var(--color-danger)' },
  ]
})

const formatMoney = (v) => Math.abs(Number(v || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2 })
const formatDate = (d) => d ? new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short' }) : '-'

/* Determina si una transacción es débito basado en tipo */
const DEBIT_TYPES = ['USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO']
const isDebit = (tx) => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase())
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
}
@media (max-width: 1024px) { .dashboard-grid { grid-template-columns: 1fr; } }

.top-clients-list { display: flex; flex-direction: column; gap: 4px; }
.top-client-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.top-client-item:hover { background: var(--color-primary-bg); }
.top-client-rank {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.top-client-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.top-client-info { flex: 1; min-width: 0; }
.top-client-name { font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.top-client-amount { font-weight: 800; font-size: 0.95rem; color: var(--color-success); white-space: nowrap; }

.status-bars { display: flex; flex-direction: column; gap: 20px; }
.status-bar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.status-bar-track { height: 8px; background: var(--color-bg); border-radius: 4px; overflow: hidden; }
.status-bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }
</style>
