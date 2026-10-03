<template>
  <div class="vendedor-page">
    <header class="vendedor-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Portal de Vendedores</h1>
          <span class="header-sub">Gift Cards generadas · descarga para clientes</span>
        </div>
      </div>
      <div class="header-right">
        <span class="vendedor-name">{{ nombre }}</span>
        <button class="btn-logout" @click="logout">Cerrar Sesión</button>
      </div>
    </header>

    <main class="vendedor-content">
      <!-- Filtros -->
      <section class="toolbar">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input v-model="search" type="search" placeholder="Buscar por código, beneficiario, cédula o lote" />
        </div>
        <select v-model="lote" class="toolbar-select" aria-label="Lote">
          <option value="">Todos los lotes</option>
          <option v-for="l in lotes" :key="l.lote" :value="l.lote">{{ l.lote }} ({{ l.total_giftcards }})</option>
        </select>
        <select v-model="estado" class="toolbar-select" aria-label="Estado">
          <option value="">Todos los estados</option>
          <option v-for="e in ESTADOS" :key="e" :value="e">{{ e.charAt(0) + e.slice(1).toLowerCase() }}</option>
        </select>
      </section>

      <div class="results-header">
        <span class="results-count">
          {{ loading ? 'Cargando...' : `${total} ${total === 1 ? 'tarjeta' : 'tarjetas'}` }}
        </span>
        <button
          class="btn-download-all"
          :disabled="!total || loading || preparing || !!bulkProgress || !!downloading"
          @click="downloadFiltered"
        >
          <span v-if="preparing || bulkProgress" class="spinner-sm"></span>
          <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          {{ bulkLabel }}
        </button>
      </div>

      <div v-if="error" class="state-msg state-error">{{ error }}</div>

      <div v-else-if="!loading && !cards.length" class="state-msg">
        No hay tarjetas con estos filtros.
      </div>

      <!-- Tarjetas -->
      <div v-else class="cards-grid" :class="{ 'is-loading': loading }">
        <div v-for="gc in cards" :key="gc.id" class="card-item">
          <GiftCardFace :gc="gc" :bg-url="bgUrl" :ref="el => cardEls[gc.id] = el?.$el" />
          <div class="card-meta">
            <div class="card-meta-info">
              <span class="badge" :class="statusClass(gc.estado)">{{ gc.estado || 'Sin estado' }}</span>
              <span v-if="gc.lote" class="card-lote">Lote {{ gc.lote }}</span>
            </div>
            <button
              class="btn-download"
              title="Descargar imagen"
              :disabled="!!downloading || !!bulkProgress"
              @click="downloadCard(cardEls[gc.id], gc.numero_tarjeta)"
            >
              <span v-if="downloading === gc.numero_tarjeta" class="spinner-sm spinner-dark"></span>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </button>
          </div>
          <div v-if="gc.cliente_nombre || gc.cliente_cedula" class="card-owner">
            {{ gc.cliente_nombre || '-' }} <span v-if="gc.cliente_cedula">· {{ gc.cliente_cedula }}</span>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <nav v-if="totalPages > 1" class="pagination">
        <button :disabled="page <= 1 || loading" @click="goTo(page - 1)">← Anterior</button>
        <span>Página {{ page }} de {{ totalPages }}</span>
        <button :disabled="page >= totalPages || loading" @click="goTo(page + 1)">Siguiente →</button>
      </nav>
    </main>

    <!-- Render fuera de pantalla para la descarga de todas las del filtro -->
    <div v-if="bulkCards.length" class="bulk-render" ref="bulkContainer" aria-hidden="true">
      <GiftCardFace
        v-for="gc in bulkCards"
        :key="gc.id"
        :gc="gc"
        :bg-url="bgUrl"
        :ref="el => bulkEls[gc.id] = el?.$el"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { session } from '../services/session'
import { useCardDownload } from '../composables/useCardDownload'
import GiftCardFace from '../components/ui/GiftCardFace.vue'

const PAGE_SIZE = 24
const BULK_MAX = 500
const ESTADOS = ['GENERADA', 'VENDIDA', 'ACTIVA', 'AGOTADA', 'VENCIDA', 'BLOQUEADA']

const router = useRouter()
const { downloading, bulkProgress, downloadCard, downloadAllCards } = useCardDownload()

const nombre = ref(session.vendedorNombre() || 'Vendedor')
const cards = ref([])
const total = ref(0)
const totalPages = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref(null)
const search = ref('')
const lote = ref('')
const estado = ref('')
const lotes = ref([])
const bgUrl = ref(null)
const cardEls = {}

// Descarga de todas las del filtro
const preparing = ref(false)
const bulkCards = ref([])
const bulkContainer = ref(null)
const bulkEls = {}

const filters = () => ({
  search: search.value.trim() || undefined,
  lote: lote.value || undefined,
  status: estado.value || undefined
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await api.getVendedorGiftCards({ ...filters(), page: page.value, page_size: PAGE_SIZE })
    cards.value = res.data.results || []
    total.value = res.data.total || 0
    totalPages.value = res.data.total_pages || 0
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudieron cargar las tarjetas'
  } finally {
    loading.value = false
  }
}

function goTo(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// La búsqueda espera a que el vendedor deje de escribir
let searchTimer = null
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 400)
})
watch([lote, estado], () => { page.value = 1; load() })

const bulkLabel = computed(() => {
  if (preparing.value && !bulkProgress.value) return 'Preparando...'
  if (bulkProgress.value) return `Generando ${bulkProgress.value.done}/${bulkProgress.value.total}`
  return `Descargar todas (${Math.min(total.value, BULK_MAX)})`
})

function waitForImages(container) {
  const imgs = [...container.querySelectorAll('img')].filter(img => !img.complete)
  return Promise.all(imgs.map(img => new Promise(resolve => { img.onload = img.onerror = resolve })))
}

async function downloadFiltered() {
  if (total.value > BULK_MAX && !confirm(
    `Hay ${total.value} tarjetas con estos filtros. Se descargarán las primeras ${BULK_MAX}. ` +
    'Para descargar el resto, filtra por lote. ¿Continuar?'
  )) return

  preparing.value = true
  try {
    const all = []
    for (let p = 1; all.length < Math.min(total.value, BULK_MAX); p++) {
      const res = await api.getVendedorGiftCards({ ...filters(), page: p, page_size: 100 })
      all.push(...(res.data.results || []))
      if (p >= (res.data.total_pages || 1)) break
    }
    bulkCards.value = all.slice(0, BULK_MAX)
    await nextTick()
    await waitForImages(bulkContainer.value)

    const fecha = new Date().toISOString().slice(0, 10)
    const nombreZip = `giftcards-damasco-${lote.value || 'tarjetas'}-${fecha}.zip`.replace(/[^\w.-]+/g, '-')
    await downloadAllCards(
      bulkCards.value.map(gc => ({ el: bulkEls[gc.id], numero: gc.numero_tarjeta })),
      nombreZip
    )
  } catch (e) {
    alert(e.response?.data?.error || 'No se pudieron preparar las tarjetas para descargar.')
  } finally {
    bulkCards.value = []
    preparing.value = false
  }
}

const statusClass = (s) => ({
  ACTIVA: 'badge-success', VENDIDA: 'badge-success', GENERADA: 'badge-warning',
  VENCIDA: 'badge-muted', AGOTADA: 'badge-muted', BLOQUEADA: 'badge-destructive'
}[(s || '').toUpperCase()] || 'badge-muted')

function logout() {
  session.clearVendedor()
  router.push('/vendedor-login')
}

onMounted(async () => {
  if (!session.vendedorToken()) {
    router.replace('/vendedor-login')
    return
  }
  try {
    const tpl = await api.getActiveTemplate()
    if (tpl.data.active) bgUrl.value = tpl.data.image_url
  } catch (e) { /* usa imagen por defecto del CSS */ }
  load()
  try {
    const res = await api.getVendedorLotes()
    lotes.value = res.data
  } catch (e) { /* sin filtro de lotes */ }
})
</script>

<style scoped>
.vendedor-page { min-height: 100vh; background: #f5f5f5; font-family: 'Poppins', sans-serif; }

.vendedor-header { background: linear-gradient(135deg, #E1052D, #b8042a); color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 16px 32px; box-shadow: 0 2px 16px rgba(225,5,45,0.3); gap: 16px; }
.header-left { display: flex; align-items: center; gap: 16px; min-width: 0; }
.header-logo { height: 32px; }
.header-left h1 { font-size: 1.2rem; font-weight: 700; margin: 0; }
.header-sub { font-size: 0.75rem; opacity: 0.85; }
.header-right { display: flex; align-items: center; gap: 14px; }
.vendedor-name { font-size: 0.85rem; opacity: 0.95; }
.btn-logout { font-family: 'Poppins', sans-serif; font-size: 0.8rem; font-weight: 600; padding: 8px 16px; border: 2px solid rgba(255,255,255,0.45); border-radius: 8px; background: transparent; color: #fff; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-logout:hover { background: rgba(255,255,255,0.15); border-color: #fff; }

.vendedor-content { max-width: 1240px; margin: 0 auto; padding: 28px 24px 48px; }

/* Filtros */
.toolbar { display: grid; grid-template-columns: 1fr 220px 200px; gap: 12px; margin-bottom: 18px; }
.search-box { display: flex; align-items: center; gap: 10px; padding: 0 14px; background: #fff; border: 2px solid #e5e5e5; border-radius: 10px; color: #999; transition: border-color 0.2s; }
.search-box:focus-within { border-color: #E1052D; }
.search-box input { flex: 1; min-width: 0; border: none; outline: none; padding: 12px 0; font-family: inherit; font-size: 0.875rem; background: transparent; color: #222; }
.toolbar-select { font-family: inherit; font-size: 0.85rem; padding: 12px; border: 2px solid #e5e5e5; border-radius: 10px; background: #fff; outline: none; cursor: pointer; min-width: 0; }
.toolbar-select:focus { border-color: #E1052D; }

.results-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.results-count { font-size: 0.875rem; color: #666; font-weight: 500; }
.btn-download-all { display: inline-flex; align-items: center; gap: 8px; font-family: inherit; font-size: 0.85rem; font-weight: 600; padding: 10px 18px; border: none; border-radius: 10px; background: #E1052D; color: #fff; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.btn-download-all:hover:not(:disabled) { background: #c5042a; }
.btn-download-all:disabled { opacity: 0.5; cursor: not-allowed; }

/* Tarjetas */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; transition: opacity 0.2s; }
.cards-grid.is-loading { opacity: 0.5; }
.card-item { background: #fff; border-radius: 14px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.card-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.card-meta-info { display: flex; align-items: center; gap: 8px; min-width: 0; flex-wrap: wrap; }
.card-lote { font-size: 0.75rem; color: #777; }
.card-owner { font-size: 0.75rem; color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn-download { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; flex-shrink: 0; border: 1px solid #e5e5e5; border-radius: 8px; background: #fff; color: #555; cursor: pointer; transition: all 0.2s; }
.btn-download:hover:not(:disabled) { color: #E1052D; border-color: #E1052D; }
.btn-download:disabled { opacity: 0.5; cursor: default; }

.state-msg { text-align: center; padding: 56px 16px; color: #888; font-size: 0.9rem; }
.state-error { color: #E1052D; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 28px; font-size: 0.85rem; color: #555; }
.pagination button { font-family: inherit; font-size: 0.85rem; font-weight: 600; padding: 8px 14px; border: 1px solid #ddd; border-radius: 8px; background: #fff; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: default; }

.spinner-sm { width: 15px; height: 15px; border: 2px solid rgba(255,255,255,0.35); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; }
.spinner-dark { border-color: #e5e5e5; border-top-color: #E1052D; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Fuera de pantalla: solo para generar las imágenes del ZIP */
.bulk-render { position: fixed; left: -10000px; top: 0; width: 420px; pointer-events: none; }
.bulk-render > * { margin-bottom: 8px; }

@media (max-width: 860px) {
  .vendedor-header { flex-direction: column; text-align: center; padding: 16px; }
  .header-left { flex-direction: column; gap: 8px; }
  .toolbar { grid-template-columns: 1fr 1fr; }
  .search-box { grid-column: 1 / -1; }
}
@media (max-width: 480px) {
  .vendedor-content { padding: 20px 16px 40px; }
  .toolbar { grid-template-columns: 1fr; }
  .results-header { flex-direction: column; align-items: stretch; }
  .btn-download-all { justify-content: center; }
  .cards-grid { grid-template-columns: 1fr; }
}
</style>
