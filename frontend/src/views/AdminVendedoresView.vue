<template>
  <div class="vend-admin-page">
    <header class="page-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Vendedores</h1>
          <span class="header-sub">Acceso al portal de descarga de Gift Cards</span>
        </div>
      </div>
      <div class="header-right">
        <router-link to="/admin" class="btn-back">← Panel Admin</router-link>
        <button class="btn-logout" @click="logout">Cerrar Sesión</button>
      </div>
    </header>

    <div v-if="!token" class="page-empty">
      <h2>Acceso no autorizado</h2>
      <router-link to="/admin-login" class="btn-primary">Iniciar Sesión</router-link>
    </div>

    <main v-else class="page-content">
      <!-- Nuevo vendedor -->
      <section class="panel">
        <h2 class="panel-title">Nuevo vendedor</h2>
        <form class="new-form" @submit.prevent="create">
          <input v-model.trim="nuevo.nombre" type="text" placeholder="Nombre completo" class="field" autocomplete="off" />
          <input v-model.trim="nuevo.username" type="text" placeholder="Usuario (ej: jperez)" class="field" autocomplete="off" />
          <input v-model="nuevo.password" type="password" placeholder="Contraseña (mín. 8 caracteres)" class="field" autocomplete="new-password" />
          <button type="submit" class="btn-main" :disabled="saving || !nuevo.nombre || !nuevo.username || !nuevo.password">
            {{ saving ? 'Creando...' : 'Crear vendedor' }}
          </button>
        </form>
        <p class="hint">El vendedor entra en <strong>{{ loginUrl }}</strong> con este usuario y contraseña.</p>
        <div v-if="msg" class="msg" :class="msgType">{{ msg }}</div>
      </section>

      <!-- Lista -->
      <section class="panel">
        <h2 class="panel-title">
          Vendedores <span class="count-badge">{{ vendedores.length }}</span>
        </h2>

        <div v-if="loading" class="list-state">Cargando vendedores...</div>
        <div v-else-if="!vendedores.length" class="list-state">Todavía no hay vendedores.</div>

        <div v-else class="vend-list">
          <div v-for="v in vendedores" :key="v.id" class="vend-row" :class="{ inactive: !v.is_active }">
            <div class="vend-info">
              <span class="vend-name">{{ v.nombre || v.username }}</span>
              <span class="vend-meta">
                {{ v.username }} · {{ v.last_login ? 'Último acceso ' + formatDate(v.last_login) : 'Nunca ha entrado' }}
              </span>
            </div>
            <span class="vend-status" :class="v.is_active ? 'on' : 'off'">{{ v.is_active ? 'Activo' : 'Desactivado' }}</span>
            <div class="vend-actions">
              <template v-if="editingId === v.id">
                <input v-model="newPassword" type="password" placeholder="Nueva contraseña" class="field field-sm" autocomplete="new-password" @keydown.enter.prevent="savePassword(v)" />
                <button class="btn-small" :disabled="!newPassword || rowLoading === v.id" @click="savePassword(v)">Guardar</button>
                <button class="btn-small btn-ghost" @click="editingId = null">Cancelar</button>
              </template>
              <template v-else>
                <button class="btn-small btn-ghost" @click="editingId = v.id; newPassword = ''">Cambiar contraseña</button>
                <button class="btn-small" :class="v.is_active ? 'btn-danger' : ''" :disabled="rowLoading === v.id" @click="toggleActive(v)">
                  {{ v.is_active ? 'Desactivar' : 'Activar' }}
                </button>
              </template>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import api from '@/services/api'
import { session, takeAdminToken } from '@/services/session'

export default {
  name: 'AdminVendedoresView',
  data() {
    return {
      token: null,
      vendedores: [],
      loading: false,
      saving: false,
      nuevo: { nombre: '', username: '', password: '' },
      editingId: null,
      newPassword: '',
      rowLoading: null,
      msg: null,
      msgType: ''
    }
  },
  computed: {
    loginUrl() {
      return `${window.location.origin}/vendedor-login`
    }
  },
  created() {
    this.token = takeAdminToken(this.$route, this.$router)
    if (this.token) this.load()
  },
  methods: {
    logout() {
      session.clearAdmin()
      this.$router.push('/admin-login')
    },
    handleError(err, fallback) {
      if (err.response?.status === 401) this.token = null
      this.showMsg(err.response?.data?.error || fallback, 'error')
    },
    showMsg(text, type) {
      this.msg = text
      this.msgType = type
    },
    async load() {
      this.loading = true
      try {
        const res = await api.getVendedores(this.token)
        this.vendedores = res.data
      } catch (err) {
        this.handleError(err, 'Error al cargar vendedores')
      } finally {
        this.loading = false
      }
    },
    async create() {
      this.saving = true
      this.msg = null
      try {
        const res = await api.createVendedor(this.token, this.nuevo)
        this.showMsg(`Vendedor "${res.data.nombre}" creado. Ya puede entrar con el usuario ${res.data.username}.`, 'success')
        this.nuevo = { nombre: '', username: '', password: '' }
        await this.load()
      } catch (err) {
        this.handleError(err, 'Error al crear el vendedor')
      } finally {
        this.saving = false
      }
    },
    async update(v, data, okMsg) {
      this.rowLoading = v.id
      this.msg = null
      try {
        const res = await api.updateVendedor(this.token, v.id, data)
        Object.assign(v, res.data)
        this.showMsg(okMsg, 'success')
        return true
      } catch (err) {
        this.handleError(err, 'Error al actualizar el vendedor')
        return false
      } finally {
        this.rowLoading = null
      }
    },
    async savePassword(v) {
      if (await this.update(v, { password: this.newPassword }, `Contraseña de ${v.nombre || v.username} actualizada.`)) {
        this.editingId = null
        this.newPassword = ''
      }
    },
    toggleActive(v) {
      const activar = !v.is_active
      if (!activar && !confirm(`¿Desactivar a ${v.nombre || v.username}? Perderá el acceso de inmediato.`)) return
      this.update(v, { is_active: activar }, `${v.nombre || v.username} ${activar ? 'activado' : 'desactivado'}.`)
    },
    formatDate(iso) {
      return new Date(iso).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' })
    }
  }
}
</script>

<style scoped>
.vend-admin-page { min-height: 100vh; background: #f5f5f5; font-family: 'Poppins', sans-serif; }

.page-header { background: linear-gradient(135deg, #E1052D, #b8042a); color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 16px 32px; box-shadow: 0 2px 16px rgba(225,5,45,0.3); }
.header-left { display: flex; align-items: center; gap: 16px; }
.header-logo { height: 36px; }
.header-left h1 { font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-sub { font-size: 0.75rem; opacity: 0.8; }
.header-right { display: flex; gap: 12px; }
.btn-back, .btn-logout { font-family: 'Poppins', sans-serif; font-size: 0.8rem; font-weight: 600; padding: 8px 16px; border: 2px solid rgba(255,255,255,0.4); border-radius: 8px; background: transparent; color: #fff; cursor: pointer; text-decoration: none; transition: all 0.2s; }
.btn-back:hover, .btn-logout:hover { background: rgba(255,255,255,0.15); border-color: #fff; }

.page-content { max-width: 960px; margin: 0 auto; padding: 32px 24px; display: flex; flex-direction: column; gap: 20px; }
.panel { background: #fff; border-radius: 12px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.panel-title { font-size: 1rem; font-weight: 700; color: #222; margin: 0 0 14px; display: flex; align-items: center; gap: 8px; }
.count-badge { background: #E1052D; color: #fff; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; }

.new-form { display: grid; grid-template-columns: 1.2fr 1fr 1fr auto; gap: 10px; }
.field { font-family: inherit; font-size: 0.85rem; padding: 11px 14px; border: 2px solid #e5e5e5; border-radius: 8px; outline: none; min-width: 0; }
.field:focus { border-color: #E1052D; }
.field-sm { padding: 7px 10px; font-size: 0.8rem; width: 170px; }
.btn-main { font-family: inherit; font-size: 0.85rem; font-weight: 600; padding: 11px 18px; border: none; border-radius: 8px; background: #E1052D; color: #fff; cursor: pointer; white-space: nowrap; }
.btn-main:hover:not(:disabled) { background: #c5042a; }
.btn-main:disabled { opacity: 0.5; cursor: not-allowed; }
.hint { font-size: 0.75rem; color: #888; margin: 10px 0 0; }
.msg { margin-top: 12px; padding: 10px 14px; border-radius: 8px; font-size: 0.8rem; }
.msg.success { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.msg.error { background: #fef2f2; color: #E1052D; border: 1px solid #fecaca; }

.list-state { text-align: center; padding: 24px; color: #999; font-size: 0.85rem; }
.vend-list { display: flex; flex-direction: column; }
.vend-row { display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: 16px; padding: 14px 4px; border-bottom: 1px solid #f0f0f0; }
.vend-row:last-child { border-bottom: none; }
.vend-row.inactive .vend-name { color: #999; }
.vend-info { display: flex; flex-direction: column; min-width: 0; }
.vend-name { font-size: 0.9rem; font-weight: 600; color: #222; }
.vend-meta { font-size: 0.75rem; color: #999; }
.vend-status { font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.04em; }
.vend-status.on { background: #f0fdf4; color: #16a34a; }
.vend-status.off { background: #f5f5f5; color: #999; }
.vend-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.btn-small { font-family: inherit; font-size: 0.78rem; font-weight: 600; padding: 7px 12px; border: 1px solid #222; border-radius: 8px; background: #222; color: #fff; cursor: pointer; white-space: nowrap; }
.btn-small:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-small.btn-ghost { background: #fff; color: #444; border-color: #ddd; }
.btn-small.btn-ghost:hover { border-color: #999; }
.btn-small.btn-danger { background: #fff; color: #E1052D; border-color: #fecaca; }
.btn-small.btn-danger:hover { background: #fef2f2; }

.page-empty { text-align: center; padding: 120px 20px; color: #888; }
.page-empty h2 { color: #333; margin-bottom: 8px; }
.btn-primary { display: inline-block; margin-top: 16px; padding: 12px 24px; background: #E1052D; color: #fff; border-radius: 10px; text-decoration: none; font-weight: 600; }

@media (max-width: 760px) {
  .page-header { flex-direction: column; gap: 12px; padding: 16px; text-align: center; }
  .new-form { grid-template-columns: 1fr; }
  .vend-row { grid-template-columns: 1fr auto; }
  .vend-actions { grid-column: 1 / -1; justify-content: flex-start; }
}
</style>
