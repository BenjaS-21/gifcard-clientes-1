<template>
  <div class="giftcards-page">
    <div class="page-header">
      <div>
        <h1>&#127873; Gift Cards</h1>
        <p class="page-header-subtitle">Todas las tarjetas de regalo</p>
      </div>
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <SearchBar v-model="search" placeholder="Buscar tarjeta o cliente..." @search="fetchCards" />
        <div class="filter-tabs">
          <button class="filter-tab" :class="{ active: !statusFilter }" @click="statusFilter = ''; fetchCards()">Todas</button>
          <button class="filter-tab" :class="{ active: statusFilter === 'activa' }" @click="statusFilter = 'activa'; fetchCards()">Activas</button>
          <button class="filter-tab" :class="{ active: statusFilter === 'vencida' }" @click="statusFilter = 'vencida'; fetchCards()">Vencidas</button>
          <button class="filter-tab" :class="{ active: statusFilter === 'agotada' }" @click="statusFilter = 'agotada'; fetchCards()">Agotadas</button>
          <button class="filter-tab" :class="{ active: statusFilter === 'bloqueada' }" @click="statusFilter = 'bloqueada'; fetchCards()">Bloqueadas</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div><span class="text-muted">Cargando...</span></div>

    <!-- Cards Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid-cards">
      <div v-for="gc in giftcards" :key="gc.id" class="gc-wrapper fade-in" @click="$router.push('/giftcards/' + gc.id)">
        <GiftCard :numero="gc.numero_tarjeta" :saldo="gc.saldo" :color="gc.color" :vencimiento="gc.fecha_vencimiento" />
        <div class="gc-meta">
          <span class="text-sm" style="font-weight:600">{{ gc.cliente_nombre }}</span>
          <StatusBadge :status="gc.estado" />
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-else class="card">
      <div class="card-body" style="padding:0">
        <table class="data-table">
          <thead>
            <tr>
              <th>Tarjeta</th>
              <th>Cliente</th>
              <th>Estado</th>
              <th style="text-align:right">Saldo</th>
              <th style="text-align:right">Saldo Inicial</th>
              <th>Emisión</th>
              <th>Vencimiento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="gc in giftcards" :key="gc.id" @click="$router.push('/giftcards/' + gc.id)">
              <td style="font-weight:700">{{ gc.numero_tarjeta }}</td>
              <td>{{ gc.cliente_nombre }}</td>
              <td><StatusBadge :status="gc.estado" /></td>
              <td style="text-align:right;font-weight:700;color:var(--color-success)">${{ formatMoney(gc.saldo) }}</td>
              <td style="text-align:right" class="text-muted">${{ formatMoney(gc.saldo_inicial) }}</td>
              <td class="text-sm">{{ gc.fecha_emision }}</td>
              <td class="text-sm">{{ gc.fecha_vencimiento }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- View Toggle + Pagination -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:20px;flex-wrap:wrap;gap:12px">
      <div style="display:flex;gap:4px">
        <button class="btn btn-sm" :class="viewMode === 'grid' ? 'btn-primary' : 'btn-ghost'" @click="viewMode = 'grid'">&#9638; Tarjetas</button>
        <button class="btn btn-sm" :class="viewMode === 'table' ? 'btn-primary' : 'btn-ghost'" @click="viewMode = 'table'">&#9776; Tabla</button>
      </div>
      <div class="pagination" v-if="totalPages > 1">
        <button @click="goPage(page - 1)" :disabled="page <= 1">&#9664;</button>
        <button v-for="p in visiblePages" :key="p" @click="goPage(p)" :class="{ active: p === page }">{{ p }}</button>
        <button @click="goPage(page + 1)" :disabled="page >= totalPages">&#9654;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../services/api'
import GiftCard from '../components/ui/GiftCard.vue'
import SearchBar from '../components/ui/SearchBar.vue'
import StatusBadge from '../components/ui/StatusBadge.vue'

const giftcards = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')
const viewMode = ref('grid')
const page = ref(1)
const total = ref(0)
const pageSize = 20
const totalPages = computed(() => Math.ceil(total.value / pageSize))
const visiblePages = computed(() => {
  const pages = []; const s = Math.max(1, page.value - 2); const e = Math.min(totalPages.value, s + 4)
  for (let i = s; i <= e; i++) pages.push(i); return pages
})

const fetchCards = async () => {
  loading.value = true
  try {
    const res = await api.getGiftCards({ search: search.value || undefined, status: statusFilter.value || undefined, page: page.value, page_size: pageSize })
    giftcards.value = res.data.results || []
    total.value = res.data.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const goPage = (p) => { page.value = p; fetchCards() }
let t = null
watch(search, () => { clearTimeout(t); t = setTimeout(() => { page.value = 1; fetchCards() }, 400) })
onMounted(fetchCards)

const formatMoney = (v) => Number(v || 0).toLocaleString('es-VE', { minimumFractionDigits: 2 })
</script>

<style scoped>
.gc-wrapper { cursor: pointer; }
.gc-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding: 0 4px; }
</style>
