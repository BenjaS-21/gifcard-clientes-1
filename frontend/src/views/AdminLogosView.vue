<template>
  <div class="logos-page">
    <header class="logos-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Logos de Empresas</h1>
          <span class="header-sub">Logo de la empresa compradora en sus Gift Cards</span>
        </div>
      </div>
      <div class="header-right">
        <router-link to="/admin" class="btn-back">← Panel Admin</router-link>
        <button class="btn-logout" @click="logout">Cerrar Sesión</button>
      </div>
    </header>

    <div v-if="!token" class="logos-empty">
      <h2>Acceso no autorizado</h2>
      <router-link to="/admin-login" class="btn-primary">Iniciar Sesión</router-link>
    </div>

    <main v-else class="logos-content">
      <div class="logos-grid">
        <!-- LEFT: Empresas -->
        <aside class="companies-panel">
          <button class="btn-new" @click="newCompany">+ Nueva empresa</button>

          <div v-if="loading" class="list-state">Cargando empresas...</div>
          <div v-else-if="!companies.length" class="list-state">Aún no hay empresas con logo.</div>

          <button
            v-for="c in companies"
            :key="c.id"
            class="company-item"
            :class="{ 'is-selected': form.id === c.id }"
            @click="selectCompany(c)"
          >
            <span class="company-thumb"><img :src="c.logo_url" :alt="c.name" /></span>
            <span class="company-text">
              <span class="company-name">{{ c.name }}</span>
              <span class="company-lotes">{{ c.lotes.length }} {{ c.lotes.length === 1 ? 'lote' : 'lotes' }}</span>
            </span>
          </button>
        </aside>

        <!-- RIGHT: Editor -->
        <div class="editor-panel">
          <section class="ctrl-section">
            <h3 class="ctrl-title">{{ form.id ? 'Editar empresa' : 'Nueva empresa' }}</h3>

            <label class="ctrl-label">Nombre de la empresa</label>
            <input v-model="form.name" type="text" placeholder="Ej: Empresas Polar" class="ctrl-input" />

            <label class="ctrl-label">RIF de la empresa (opcional)</label>
            <input v-model="form.rif" type="text" placeholder="Ej: J-00000000-0" class="ctrl-input" />
            <p class="ctrl-hint">Al entrar al portal con este RIF, la empresa ve todas las tarjetas de sus lotes, también las que ya entregó.</p>

            <label class="ctrl-label">Logo</label>
            <label class="file-input-label" :class="{ 'has-file': form.file }">
              {{ form.file ? form.file.name : (form.id ? 'Cambiar logo' : 'Seleccionar logo') }}
              <input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" @change="onFileSelect" hidden />
            </label>
            <p class="ctrl-hint">PNG, JPG, WebP o SVG (máx. 5 MB). Recomendado: PNG o SVG con fondo transparente.</p>

            <label class="ctrl-label">
              Lotes de la empresa
              <span v-if="form.lotes.length" class="lote-count">{{ form.lotes.length }} seleccionados</span>
            </label>
            <div class="lote-chips" v-if="form.lotes.length">
              <span v-for="l in form.lotes" :key="l" class="lote-chip">
                {{ l }}
                <button type="button" @click="removeLote(l)" :title="`Quitar lote ${l}`">&times;</button>
              </span>
              <button type="button" class="lote-clear" @click="form.lotes = []">Quitar todos</button>
            </div>
            <div class="lote-add-row">
              <input
                v-model="loteInput"
                type="text"
                placeholder="Buscar lote, o escribir/pegar varios y Enter"
                class="ctrl-input"
                @keydown.enter.prevent="addLote(loteInput)"
                @paste="onLotePaste"
              />
              <button type="button" class="btn-add" @click="addLote(loteInput)" :disabled="!loteInput.trim()">Agregar</button>
            </div>

            <div v-if="lotePicker.items.length" class="lote-picker">
              <div class="lote-picker-head">
                <span>{{ loteInput.trim() ? `${lotePicker.total} coinciden` : `${lotePicker.total} lotes en SAP` }}</span>
                <button
                  v-if="lotePicker.selectable"
                  type="button"
                  class="lote-select-all"
                  @click="selectAllMatching"
                >
                  Seleccionar {{ lotePicker.selectable === 1 ? 'el que coincide' : `los ${lotePicker.selectable} que coinciden` }}
                </button>
              </div>
              <div class="lote-picker-list">
                <label
                  v-for="s in lotePicker.items"
                  :key="s.lote"
                  class="lote-option"
                  :class="{ 'is-taken': s.owner, 'is-checked': s.checked }"
                  :title="s.owner ? `Asignado a ${s.owner}` : ''"
                >
                  <input type="checkbox" :checked="s.checked" :disabled="!!s.owner" @change="toggleLote(s.lote)" />
                  <span class="lote-option-code">{{ s.lote }}</span>
                  <small>{{ s.owner ? s.owner : s.total_giftcards + ' tarj.' }}</small>
                </label>
              </div>
              <p v-if="lotePicker.total > lotePicker.items.length" class="ctrl-hint">
                Mostrando {{ lotePicker.items.length }} de {{ lotePicker.total }}. Escribe para filtrar.
              </p>
            </div>
            <p class="ctrl-hint">Todas las tarjetas de estos lotes saldrán con el logo. Puedes pegar una lista de lotes copiada de Excel.</p>
          </section>

          <section class="ctrl-section">
            <h3 class="ctrl-title">Posición y tamaño</h3>
            <div class="preview-wrapper">
              <div class="gift-card logo-preview-card" :style="cardBgStyle" ref="card">
                <div class="gc-type-label">GIFT CARD</div>
                <div class="gc-pattern"></div>
                <div class="gc-logo">
                  <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="gc-logo-img" />
                </div>
                <img
                  v-if="form.previewUrl"
                  class="gc-company-logo is-editable"
                  :class="{ 'is-dragging': dragging }"
                  :src="form.previewUrl"
                  alt="Logo de la empresa"
                  :style="logoStyle"
                  draggable="false"
                  @pointerdown="startDrag"
                  @pointermove="onDrag"
                  @pointerup="endDrag"
                  @pointercancel="endDrag"
                />
                <div class="gc-number">DAM-2025-XXXX</div>
                <div class="gc-bottom">
                  <div>
                    <div class="gc-label">Saldo disponible</div>
                    <div class="gc-balance">$100,00</div>
                  </div>
                  <div class="gc-expiry">
                    <div class="gc-label">Vence</div>
                    <div>12/2026</div>
                  </div>
                </div>
              </div>
            </div>
            <p class="preview-note">
              {{ form.previewUrl ? 'Arrastra el logo sobre la tarjeta para ubicarlo.' : 'Selecciona un logo para ubicarlo en la tarjeta.' }}
            </p>

            <label class="ctrl-label">Tamaño: {{ form.width }}%</label>
            <input type="range" v-model.number="form.width" min="5" max="80" step="0.5" class="ctrl-range" :disabled="!form.previewUrl" />
            <div class="range-row">
              <div>
                <label class="ctrl-label">Horizontal: {{ form.pos_x }}%</label>
                <input type="range" v-model.number="form.pos_x" min="0" max="100" step="0.5" class="ctrl-range" :disabled="!form.previewUrl" />
              </div>
              <div>
                <label class="ctrl-label">Vertical: {{ form.pos_y }}%</label>
                <input type="range" v-model.number="form.pos_y" min="0" max="100" step="0.5" class="ctrl-range" :disabled="!form.previewUrl" />
              </div>
            </div>
          </section>

          <section class="ctrl-section save-section">
            <div class="save-row">
              <button class="btn-save" @click="save" :disabled="saving || !canSave">
                <span v-if="!saving">Guardar</span>
                <span v-else>Guardando...</span>
              </button>
              <button v-if="form.id" class="btn-delete" @click="remove" :disabled="saving">Eliminar empresa</button>
            </div>
            <div v-if="msg" class="save-msg" :class="msgType">{{ msg }}</div>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/services/api'
import { session, takeAdminToken } from '@/services/session'
import { secureUrl } from '@/services/secureUrl'

const LOGO_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
const LOGO_MAX_BYTES = 5 * 1024 * 1024
const MAX_PICKER_ITEMS = 200

const emptyForm = () => ({
  id: null,
  name: '',
  rif: '',
  lotes: [],
  pos_x: 50,
  pos_y: 50,
  width: 25,
  file: null,
  previewUrl: null
})

const clamp = (v, min, max) => Math.min(max, Math.max(min, v))
const round1 = (v) => Math.round(v * 10) / 10

export default {
  name: 'AdminLogosView',
  data() {
    return {
      token: null,
      companies: [],
      loading: false,
      availableLotes: [],
      form: emptyForm(),
      loteInput: '',
      cardBgUrl: null,
      dragging: false,
      dragOffset: null,
      blobUrl: null,
      saving: false,
      msg: null,
      msgType: ''
    }
  },
  computed: {
    cardBgStyle() {
      return this.cardBgUrl ? { backgroundImage: `url(${this.cardBgUrl})` } : {}
    },
    logoStyle() {
      return {
        left: this.form.pos_x + '%',
        top: this.form.pos_y + '%',
        width: this.form.width + '%'
      }
    },
    canSave() {
      return !!this.form.name.trim() && !!this.form.previewUrl
    },
    // Lotes ya asignados a OTRAS empresas: { LOTE: nombre empresa }
    lotesTaken() {
      const taken = {}
      for (const c of this.companies) {
        if (c.id === this.form.id) continue
        for (const l of c.lotes) taken[l.toUpperCase()] = c.name
      }
      return taken
    },
    // Lotes de SAP que coinciden con la búsqueda, marcados si ya están elegidos
    lotePicker() {
      const selected = new Set(this.form.lotes.map(l => l.toUpperCase()))
      const text = this.loteInput.trim().toUpperCase()
      const matching = this.availableLotes
        .map(l => {
          const lote = String(l.lote)
          const key = lote.toUpperCase()
          return { ...l, lote, checked: selected.has(key), owner: this.lotesTaken[key] || null }
        })
        .filter(l => !text || l.lote.toUpperCase().includes(text))
      return {
        total: matching.length,
        selectable: matching.filter(l => !l.checked && !l.owner).length,
        items: matching.slice(0, MAX_PICKER_ITEMS)
      }
    }
  },
  created() {
    this.token = takeAdminToken(this.$route, this.$router)
    if (this.token) {
      this.loadCompanies()
      this.loadLotes()
      this.loadTemplate()
    }
  },
  beforeUnmount() {
    this.releaseBlob()
  },
  methods: {
    logout() {
      session.clearAdmin()
      this.$router.push('/admin-login')
    },
    async loadCompanies() {
      this.loading = true
      try {
        const res = await api.getCompanies(this.token)
        this.companies = res.data
      } catch (err) {
        if (err.response?.status === 401) this.token = null
      } finally {
        this.loading = false
      }
    },
    async loadLotes() {
      try {
        const res = await api.getLotes(this.token)
        this.availableLotes = res.data
      } catch (e) { /* sin sugerencias: los lotes se escriben a mano */ }
    },
    async loadTemplate() {
      try {
        const tpl = await api.getActiveTemplate()
        if (tpl.data.active) this.cardBgUrl = secureUrl(tpl.data.image_url)
      } catch (e) { /* usa imagen por defecto del CSS */ }
    },
    releaseBlob() {
      if (this.blobUrl) URL.revokeObjectURL(this.blobUrl)
      this.blobUrl = null
    },
    newCompany() {
      this.releaseBlob()
      this.form = emptyForm()
      this.loteInput = ''
      this.msg = null
    },
    selectCompany(c) {
      this.releaseBlob()
      this.form = {
        id: c.id,
        name: c.name,
        rif: c.rif || '',
        lotes: [...c.lotes],
        pos_x: c.pos_x,
        pos_y: c.pos_y,
        width: c.width,
        file: null,
        previewUrl: c.logo_url
      }
      this.loteInput = ''
      this.msg = null
    },
    onFileSelect(e) {
      const file = e.target.files[0]
      e.target.value = ''
      if (!file) return
      if (!LOGO_TYPES.includes(file.type)) {
        this.showMsg('Tipo de archivo no permitido. Usa PNG, JPG, WebP o SVG.', 'error')
        return
      }
      if (file.size > LOGO_MAX_BYTES) {
        this.showMsg('El logo no puede pesar más de 5 MB.', 'error')
        return
      }
      this.releaseBlob()
      this.blobUrl = URL.createObjectURL(file)
      this.form.file = file
      this.form.previewUrl = this.blobUrl
      this.msg = null
    },
    // Marcar/desmarcar en la lista no borra la búsqueda, para elegir varios seguidos
    toggleLote(lote) {
      if (this.form.lotes.some(l => l.toUpperCase() === lote.toUpperCase())) {
        this.form.lotes = this.form.lotes.filter(l => l.toUpperCase() !== lote.toUpperCase())
      } else {
        this.form.lotes.push(lote)
      }
    },
    selectAllMatching() {
      const text = this.loteInput.trim().toUpperCase()
      const selected = new Set(this.form.lotes.map(l => l.toUpperCase()))
      for (const l of this.availableLotes) {
        const lote = String(l.lote)
        const key = lote.toUpperCase()
        if ((!text || key.includes(text)) && !selected.has(key) && !this.lotesTaken[key]) {
          selected.add(key)
          this.form.lotes.push(lote)
        }
      }
    },
    // Pegar una lista (de Excel, separada por saltos de línea, comas o tabs) agrega todos
    onLotePaste(e) {
      const text = e.clipboardData?.getData('text') || ''
      if (/[,;\n\r\t]/.test(text.trim())) {
        e.preventDefault()
        this.addLote(text)
      }
    },
    addLote(value) {
      const selected = new Set(this.form.lotes.map(l => l.toUpperCase()))
      for (const raw of String(value).split(/[,;\n\r\t]+/)) {
        const lote = raw.trim()
        const key = lote.toUpperCase()
        if (!lote || selected.has(key)) continue
        if (this.lotesTaken[key]) {
          this.showMsg(`El lote "${lote}" ya está asignado a ${this.lotesTaken[key]}.`, 'error')
          continue
        }
        selected.add(key)
        this.form.lotes.push(lote)
      }
      this.loteInput = ''
    },
    removeLote(lote) {
      this.form.lotes = this.form.lotes.filter(l => l !== lote)
    },
    /* Arrastre del logo: la posición es el centro del logo en % de la tarjeta */
    startDrag(e) {
      const card = this.$refs.card.getBoundingClientRect()
      this.dragOffset = {
        x: e.clientX - (card.left + card.width * this.form.pos_x / 100),
        y: e.clientY - (card.top + card.height * this.form.pos_y / 100)
      }
      this.dragging = true
      e.currentTarget.setPointerCapture(e.pointerId)
      e.preventDefault()
    },
    onDrag(e) {
      if (!this.dragging) return
      const card = this.$refs.card.getBoundingClientRect()
      this.form.pos_x = round1(clamp((e.clientX - this.dragOffset.x - card.left) / card.width * 100, 0, 100))
      this.form.pos_y = round1(clamp((e.clientY - this.dragOffset.y - card.top) / card.height * 100, 0, 100))
    },
    endDrag() {
      this.dragging = false
    },
    showMsg(text, type) {
      this.msg = text
      this.msgType = type
    },
    async save() {
      // Un lote escrito pero no agregado también cuenta
      if (this.loteInput.trim()) this.addLote(this.loteInput)
      this.saving = true
      this.msg = null
      try {
        const fd = new FormData()
        fd.append('name', this.form.name.trim())
        fd.append('rif', this.form.rif.trim())
        fd.append('lotes', JSON.stringify(this.form.lotes))
        fd.append('pos_x', this.form.pos_x)
        fd.append('pos_y', this.form.pos_y)
        fd.append('width', this.form.width)
        if (this.form.file) fd.append('logo', this.form.file)

        const res = this.form.id
          ? await api.updateCompany(this.token, this.form.id, fd)
          : await api.createCompany(this.token, fd)
        await this.loadCompanies()
        this.selectCompany(res.data)
        this.showMsg(`"${res.data.name}" guardada. Sus tarjetas ya salen con el logo.`, 'success')
      } catch (err) {
        if (err.response?.status === 401) this.token = null
        this.showMsg(err.response?.data?.error || 'Error al guardar', 'error')
      } finally {
        this.saving = false
      }
    },
    async remove() {
      if (!confirm(`¿Eliminar "${this.form.name}" y su logo? Sus tarjetas dejarán de mostrarlo.`)) return
      this.saving = true
      try {
        await api.deleteCompany(this.token, this.form.id)
        await this.loadCompanies()
        this.newCompany()
      } catch (err) {
        this.showMsg(err.response?.data?.error || 'Error al eliminar', 'error')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.logos-page { min-height:100vh; background:#f5f5f5; font-family:'Poppins',sans-serif; }

.logos-header { background:linear-gradient(135deg,#E1052D,#b8042a); color:#fff; display:flex; align-items:center; justify-content:space-between; padding:16px 32px; box-shadow:0 2px 16px rgba(225,5,45,0.3); }
.header-left { display:flex; align-items:center; gap:16px; }
.header-logo { height:36px; }
.header-left h1 { font-size:1.25rem; font-weight:700; margin:0; }
.header-sub { font-size:0.75rem; opacity:0.8; }
.header-right { display:flex; gap:12px; }
.btn-back,.btn-logout { font-family:'Poppins',sans-serif; font-size:0.8rem; font-weight:600; padding:8px 16px; border:2px solid rgba(255,255,255,0.4); border-radius:8px; background:transparent; color:#fff; cursor:pointer; text-decoration:none; transition:all 0.2s; }
.btn-back:hover,.btn-logout:hover { background:rgba(255,255,255,0.15); border-color:#fff; }

.logos-content { max-width:1100px; margin:0 auto; padding:32px 24px; }
.logos-grid { display:grid; grid-template-columns:280px 1fr; gap:28px; align-items:start; }

/* Empresas */
.companies-panel { display:flex; flex-direction:column; gap:10px; }
.btn-new { font-family:'Poppins',sans-serif; font-size:0.85rem; font-weight:600; padding:12px; border:2px dashed #ccc; border-radius:10px; background:#fff; color:#666; cursor:pointer; transition:all 0.2s; }
.btn-new:hover { border-color:#E1052D; color:#E1052D; }
.list-state { font-size:0.8rem; color:#999; text-align:center; padding:16px 8px; }
.company-item { display:flex; align-items:center; gap:12px; width:100%; padding:10px 12px; background:#fff; border:2px solid transparent; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.06); cursor:pointer; text-align:left; font-family:'Poppins',sans-serif; transition:all 0.2s; }
.company-item:hover { box-shadow:0 6px 16px rgba(0,0,0,0.1); }
.company-item.is-selected { border-color:#E1052D; }
.company-thumb { width:56px; height:40px; flex-shrink:0; border-radius:8px; background:#888; display:flex; align-items:center; justify-content:center; padding:4px; }
.company-thumb img { max-width:100%; max-height:100%; object-fit:contain; }
.company-text { display:flex; flex-direction:column; min-width:0; }
.company-name { font-size:0.875rem; font-weight:600; color:#222; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.company-lotes { font-size:0.7rem; color:#999; }

/* Editor */
.editor-panel { display:flex; flex-direction:column; gap:16px; min-width:0; }
.ctrl-section { background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.ctrl-title { font-size:0.95rem; font-weight:700; color:#222; margin:0 0 14px; }
.ctrl-label { display:block; font-size:0.75rem; font-weight:600; color:#666; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px; margin-top:14px; }
.ctrl-input { width:100%; font-family:'Poppins',sans-serif; font-size:0.85rem; padding:12px 14px; border:2px solid #e5e5e5; border-radius:8px; outline:none; }
.ctrl-input:focus { border-color:#E1052D; }
.ctrl-hint { font-size:0.72rem; color:#999; margin:6px 0 0; }
.ctrl-range { width:100%; accent-color:#E1052D; margin-top:4px; }
.range-row { display:grid; grid-template-columns:1fr 1fr; gap:20px; }

.file-input-label { display:inline-flex; align-items:center; font-size:0.85rem; padding:10px 16px; border:2px dashed #ccc; border-radius:10px; cursor:pointer; color:#888; max-width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; transition:all 0.2s; }
.file-input-label:hover { border-color:#E1052D; color:#E1052D; }
.file-input-label.has-file { border-color:#22c55e; color:#16a34a; border-style:solid; }

/* Lotes */
.lote-chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }
.lote-chip { display:inline-flex; align-items:center; gap:4px; font-size:0.78rem; font-weight:600; padding:4px 6px 4px 10px; border-radius:20px; background:#fef2f2; color:#E1052D; border:1px solid #fecaca; }
.lote-chip button { border:none; background:none; color:inherit; font-size:1rem; line-height:1; cursor:pointer; padding:0 4px; }
.lote-add-row { display:flex; gap:8px; }
.btn-add { font-family:'Poppins',sans-serif; font-size:0.8rem; font-weight:600; padding:0 16px; border:none; border-radius:8px; background:#222; color:#fff; cursor:pointer; white-space:nowrap; }
.btn-add:disabled { opacity:0.4; cursor:not-allowed; }
.lote-count { margin-left:6px; font-size:0.7rem; font-weight:600; color:#E1052D; text-transform:none; letter-spacing:0; }
.lote-clear { font-family:'Poppins',sans-serif; font-size:0.72rem; padding:4px 8px; border:none; background:none; color:#999; cursor:pointer; text-decoration:underline; }
.lote-clear:hover { color:#E1052D; }
.lote-picker { margin-top:10px; border:2px solid #f0f0f0; border-radius:10px; overflow:hidden; }
.lote-picker-head { display:flex; align-items:center; justify-content:space-between; gap:8px; padding:8px 12px; background:#fafafa; border-bottom:1px solid #f0f0f0; font-size:0.75rem; color:#777; }
.lote-select-all { font-family:'Poppins',sans-serif; font-size:0.75rem; font-weight:600; padding:5px 10px; border:none; border-radius:6px; background:#E1052D; color:#fff; cursor:pointer; white-space:nowrap; }
.lote-select-all:hover { background:#c5042a; }
.lote-picker-list { max-height:240px; overflow-y:auto; display:grid; grid-template-columns:repeat(auto-fill, minmax(190px, 1fr)); }
.lote-option { display:flex; align-items:center; gap:8px; padding:8px 12px; font-size:0.8rem; cursor:pointer; border-bottom:1px solid #f6f6f6; }
.lote-option:hover { background:#fff7f8; }
.lote-option.is-checked { background:#fef2f2; }
.lote-option.is-taken { opacity:0.5; cursor:not-allowed; }
.lote-option input { accent-color:#E1052D; width:16px; height:16px; flex-shrink:0; }
.lote-option-code { font-weight:600; color:#333; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.lote-option small { margin-left:auto; color:#999; white-space:nowrap; }

/* Preview */
.preview-wrapper { display:flex; justify-content:center; background:#e8e8e8; border-radius:14px; padding:28px; border:2px dashed #d0d0d0; }
.logo-preview-card { max-width:420px; border-radius:16px; padding:var(--space-8); cursor:default; }
.logo-preview-card:hover { transform:none; box-shadow:0 4px 20px rgba(0,0,0,0.15); }
.gc-logo-img { height:22px; width:auto; opacity:0.95; }
.gc-pattern { position:absolute; top:0; right:0; width:100%; height:100%; opacity:0.06; background-image:repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,1) 20px, rgba(255,255,255,1) 21px); pointer-events:none; z-index:1; }
.logo-preview-card .gc-company-logo.is-editable { pointer-events:auto; cursor:grab; touch-action:none; z-index:3; outline:1px dashed rgba(255,255,255,0.7); outline-offset:3px; }
.logo-preview-card .gc-company-logo.is-dragging { cursor:grabbing; }
.preview-note { text-align:center; font-size:0.75rem; color:#999; margin:12px 0 0; font-style:italic; }

/* Save */
.save-row { display:flex; gap:12px; }
.btn-save { flex:1; font-family:'Poppins',sans-serif; font-size:0.9rem; font-weight:600; padding:14px; border:none; border-radius:10px; background:#E1052D; color:#fff; cursor:pointer; transition:background 0.2s; }
.btn-save:hover:not(:disabled) { background:#c5042a; }
.btn-save:disabled { opacity:0.5; cursor:not-allowed; }
.btn-delete { font-family:'Poppins',sans-serif; font-size:0.85rem; font-weight:600; padding:14px 18px; border:none; border-radius:10px; background:#f5f5f5; color:#999; cursor:pointer; transition:all 0.2s; }
.btn-delete:hover:not(:disabled) { background:#fef2f2; color:#E1052D; }
.save-msg { margin-top:12px; padding:10px 14px; border-radius:8px; font-size:0.8rem; }
.save-msg.success { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.save-msg.error { background:#fef2f2; color:#E1052D; border:1px solid #fecaca; }

.logos-empty { text-align:center; padding:120px 20px; color:#888; }
.logos-empty h2 { color:#333; margin-bottom:8px; }
.btn-primary { display:inline-block; margin-top:16px; padding:12px 24px; background:#E1052D; color:#fff; border-radius:10px; text-decoration:none; font-weight:600; }

@media (max-width: 900px) {
  .logos-header { flex-direction:column; gap:12px; padding:16px; text-align:center; }
  .header-right { justify-content:center; }
  .logos-grid { grid-template-columns:1fr; }
  .preview-wrapper { padding:16px; }
  .range-row { grid-template-columns:1fr; gap:0; }
}
</style>
