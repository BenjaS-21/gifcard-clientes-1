<template>
  <div class="clients-page">
    <div class="page-header">
      <div>
        <h1>&#128101; Clientes</h1>
        <p class="page-header-subtitle">Gestión de clientes con gift cards</p>
      </div>
      <SearchBar v-model="search" placeholder="Buscar por nombre o cédula..." @search="fetchClients" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-spinner"><div class="spinner"></div><span class="text-muted">Cargando clientes...</span></div>

    <!-- Table -->
    <div v-else class="card">
      <div class="card-body" style="padding:0">
        <table class="data-table">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Cédula</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th style="text-align:center">Gift Cards</th>
              <th style="text-align:right">Saldo Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in clients" :key="client.id" @click="$router.push('/clientes/' + client.id)">
              <td>
                <div style="display:flex;align-items:center;gap:10px">
                  <div class="client-avatar">{{ client.nombre?.charAt(0) }}</div>
                  <span style="font-weight:600">{{ client.nombre }}</span>
                </div>
              </td>
              <td class="text-sm">{{ client.cedula }}</td>
              <td class="text-sm text-muted">{{ client.email }}</td>
              <td class="text-sm">{{ client.telefono }}</td>
              <td style="text-align:center"><span class="badge badge-info">{{ client.total_giftcards || 0 }}</span></td>
              <td style="text-align:right;font-weight:700;color:var(--color-success)">${{ formatMoney(client.saldo_total) }}</td>
            </tr>
            <tr v-if="!clients.length">
              <td colspan="6" class="text-muted" style="text-align:center;padding:48px">No se encontraron clientes</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1">
      <button @click="goPage(page - 1)" :disabled="page <= 1">&#9664;</button>
      <button v-for="p in visiblePages" :key="p" @click="goPage(p)" :class="{ active: p === page }">{{ p }}</button>
      <button @click="goPage(page + 1)" :disabled="page >= totalPages">&#9654;</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../services/api'
import SearchBar from '../components/ui/SearchBar.vue'

const clients = ref([])
const loading = ref(true)
const search = ref('')
const page = ref(1)
const total = ref(0)
const pageSize = 20
const totalPages = computed(() => Math.ceil(total.value / pageSize))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const fetchClients = async () => {
  loading.value = true
  try {
    const res = await api.getClients({ search: search.value || undefined, page: page.value, page_size: pageSize })
    clients.value = res.data.results || []
    total.value = res.data.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const goPage = (p) => { page.value = p; fetchClients() }

let searchTimeout = null
watch(search, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => { page.value = 1; fetchClients() }, 400) })

onMounted(fetchClients)

const formatMoney = (v) => Number(v || 0).toLocaleString('es-VE', { minimumFractionDigits: 2 })
</script>

<style scoped>
.client-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
}
</style>
