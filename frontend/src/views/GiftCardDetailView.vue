<template>
  <div class="gc-detail" v-if="giftcard">
    <div class="page-header">
      <div>
        <button class="btn btn-ghost btn-sm" @click="$router.back()" style="margin-bottom:8px">&#9664; Volver</button>
        <h1>Detalle Gift Card</h1>
        <p class="page-header-subtitle">{{ giftcard.numero_tarjeta }}</p>
      </div>
      <StatusBadge :status="giftcard.estado" />
    </div>

    <div class="gc-detail-grid">
      <!-- Card Visual -->
      <div class="gc-visual fade-in">
        <GiftCard
          :numero="giftcard.numero_tarjeta"
          :saldo="giftcard.saldo"
          :color="giftcard.color"
          :vencimiento="giftcard.fecha_vencimiento"
          style="width:100%;max-width:340px"
        />
      </div>

      <!-- Card Info -->
      <div class="card fade-in" style="animation-delay:100ms">
        <div class="card-header"><h3>Información de la Tarjeta</h3></div>
        <div class="card-body">
          <div class="detail-grid">
            <div class="detail-item"><span class="detail-label">Número</span><span class="detail-value">{{ giftcard.numero_tarjeta }}</span></div>
            <div class="detail-item"><span class="detail-label">Estado</span><StatusBadge :status="giftcard.estado" /></div>
            <div class="detail-item"><span class="detail-label">Saldo Actual</span><span class="detail-value" style="color:var(--color-success);font-weight:800;font-size:1.2rem">${{ formatMoney(giftcard.saldo) }}</span></div>
            <div class="detail-item"><span class="detail-label">Saldo Inicial</span><span class="detail-value">${{ formatMoney(giftcard.saldo_inicial) }}</span></div>
            <div class="detail-item"><span class="detail-label">Emisión</span><span class="detail-value">{{ giftcard.fecha_emision }}</span></div>
            <div class="detail-item"><span class="detail-label">Vencimiento</span><span class="detail-value">{{ giftcard.fecha_vencimiento }}</span></div>
            <div class="detail-item"><span class="detail-label">Cliente</span>
              <span class="detail-value" style="cursor:pointer;color:var(--color-primary)" @click="$router.push('/clientes/' + giftcard.cliente_id)">{{ giftcard.cliente_nombre }}</span>
            </div>
            <div class="detail-item"><span class="detail-label">Cédula</span><span class="detail-value">{{ giftcard.cliente_cedula }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Bar -->
    <div class="card fade-in" style="margin-top:24px;animation-delay:200ms">
      <div class="card-body">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px">
          <span class="text-sm" style="font-weight:600">Uso de saldo</span>
          <span class="text-sm text-muted">{{ usagePct }}% consumido</span>
        </div>
        <div class="usage-bar"><div class="usage-fill" :style="{ width: usagePct + '%' }"></div></div>
        <div style="display:flex;justify-content:space-between;margin-top:8px">
          <span class="text-xs text-muted">Consumido: ${{ formatMoney((giftcard.saldo_inicial || 0) - (giftcard.saldo || 0)) }}</span>
          <span class="text-xs text-muted">Disponible: ${{ formatMoney(giftcard.saldo) }}</span>
        </div>
      </div>
    </div>

    <!-- Transactions -->
    <div class="card fade-in" style="margin-top:24px;animation-delay:300ms">
      <div class="card-header"><h3>Movimientos</h3></div>
      <div class="card-body" style="padding:0">
        <table class="data-table" v-if="giftcard.transactions?.length">
          <thead>
            <tr><th>Fecha</th><th>Tipo</th><th>Descripción</th><th>Referencia</th><th style="text-align:right">Monto</th></tr>
          </thead>
          <tbody>
            <tr v-for="tx in giftcard.transactions" :key="tx.id">
              <td class="text-sm">{{ tx.fecha }}</td>
              <td><StatusBadge :status="tx.tipo" :showDot="false" /></td>
              <td class="text-sm">{{ tx.descripcion }}</td>
              <td class="text-xs text-muted">{{ tx.referencia }}</td>
              <td style="text-align:right;font-weight:700" :style="{ color: isDebit(tx) ? 'var(--color-danger)' : 'var(--color-success)' }">
                {{ isDebit(tx) ? '-' : '+' }}${{ formatMoney(tx.monto) }}
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state"><div class="empty-icon">&#128196;</div><h3>Sin movimientos</h3><p class="text-muted">No hay transacciones registradas</p></div>
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
import StatusBadge from '../components/ui/StatusBadge.vue'

const route = useRoute()
const giftcard = ref(null)

onMounted(async () => {
  try {
    const res = await api.getGiftCard(route.params.id)
    giftcard.value = res.data
  } catch (e) { console.error(e) }
})

const usagePct = computed(() => {
  if (!giftcard.value?.saldo_inicial) return 0
  return Math.round(((giftcard.value.saldo_inicial - giftcard.value.saldo) / giftcard.value.saldo_inicial) * 100)
})

const formatMoney = (v) => Math.abs(Number(v || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2 })

/* Determina si una transacción es débito basado en tipo */
const DEBIT_TYPES = ['USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO']
const isDebit = (tx) => DEBIT_TYPES.includes((tx.tipo || '').toUpperCase())
</script>

<style scoped>
.gc-detail-grid { display: grid; grid-template-columns: auto 1fr; gap: 24px; align-items: start; }
.gc-visual { display: flex; justify-content: center; }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; }
.detail-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: var(--color-text-secondary); letter-spacing: 0.05em; }
.detail-value { font-size: 0.95rem; font-weight: 500; }
.usage-bar { height: 10px; background: var(--color-bg); border-radius: 5px; overflow: hidden; }
.usage-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-dark)); border-radius: 5px; transition: width 1s cubic-bezier(0.4,0,0.2,1); }
@media (max-width: 768px) { .gc-detail-grid { grid-template-columns: 1fr; } }
</style>
