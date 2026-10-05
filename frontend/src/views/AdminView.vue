<template>
  <div class="admin-page">
    <!-- Header -->
    <header class="admin-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Panel Admin</h1>
          <span class="header-sub">Templates de Gift Card</span>
        </div>
      </div>
      <div class="header-right">
        <router-link to="/admin/designer" class="btn-designer">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>
          Diseñador IA
        </router-link>
        <router-link to="/admin/logos" class="btn-designer">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          Logos de Empresas
        </router-link>
        <router-link to="/admin/dashboard" class="btn-designer">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          Dashboard
        </router-link>
        <router-link to="/admin/vendedores" class="btn-designer">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Vendedores
        </router-link>
        <span class="admin-user">{{ adminUser }}</span>
        <button class="btn-logout" @click="logout">Cerrar Sesión</button>
      </div>
    </header>

    <!-- Unauthorized -->
    <div v-if="!token" class="admin-empty">
      <h2>Acceso no autorizado</h2>
      <p>Debes iniciar sesión para acceder al panel.</p>
      <router-link to="/admin-login" class="btn-primary">Iniciar Sesión</router-link>
    </div>

    <!-- Main Content -->
    <main v-else class="admin-content">
      <!-- Upload Form -->
      <section class="upload-section">
        <h2 class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Subir nuevo diseño
        </h2>
        <form @submit.prevent="handleUpload" class="upload-form">
          <div class="upload-row">
            <input
              v-model="newName"
              type="text"
              placeholder="Nombre del diseño (ej: Día de las Madres)"
              class="input-name"
              :disabled="uploading"
              required
            />
            <label class="file-input-label" :class="{ 'has-file': selectedFile }">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              {{ selectedFile ? selectedFile.name : 'Seleccionar imagen' }}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/svg+xml"
                @change="onFileSelect"
                :disabled="uploading"
                hidden
              />
            </label>
            <button type="submit" class="btn-upload" :disabled="uploading || !selectedFile">
              <span v-if="!uploading">Subir</span>
              <span v-else class="btn-loading"><span class="spinner-sm"></span></span>
            </button>
          </div>
          <div v-if="uploadError" class="upload-error">{{ uploadError }}</div>
          <div v-if="uploadSuccess" class="upload-success">{{ uploadSuccess }}</div>
        </form>
      </section>

      <!-- Template Grid -->
      <section class="templates-section">
        <h2 class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          Diseños disponibles
          <span class="count-badge">{{ templates.length }}</span>
        </h2>

        <div v-if="loadingTemplates" class="loading-state">
          <div class="spinner"></div>
          <span>Cargando templates...</span>
        </div>

        <div v-else-if="templates.length === 0" class="empty-state">
          <p>No hay diseños todavía. ¡Sube el primero! 🎨</p>
        </div>

        <div v-else class="template-grid">
          <div
            v-for="t in templates"
            :key="t.id"
            class="template-card"
            :class="{ 'is-active': t.is_active }"
          >
            <div class="template-preview">
              <img v-if="t.type === 'image' && t.image_url" :src="t.image_url" :alt="t.name" />
              <iframe
                v-else-if="t.type === 'html' && t.html_code"
                :srcdoc="getPreviewHtml(t.html_code)"
                class="template-preview-iframe"
                sandbox="allow-same-origin"
                frameborder="0"
              ></iframe>
              <div v-else class="template-no-preview">Sin preview</div>
              <div v-if="t.is_active" class="active-badge">ACTIVO</div>
              <div class="type-badge" :class="t.type === 'html' ? 'type-html' : 'type-img'">
                {{ t.type === 'html' ? '&lt;/&gt; HTML' : '🖼 Imagen' }}
              </div>
            </div>
            <div class="template-info">
              <h3>{{ t.name }}</h3>
              <span class="template-date">{{ formatDate(t.created_at) }}</span>
            </div>
            <div class="template-actions">
              <button
                v-if="!t.is_active"
                class="btn-activate"
                @click="activateTemplate(t)"
                :disabled="actionLoading === t.id"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                Activar
              </button>
              <span v-else class="active-text">✓ En uso</span>
              <button
                v-if="!t.is_active"
                class="btn-delete"
                @click="deleteTemplate(t)"
                :disabled="actionLoading === t.id"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Preview -->
      <section v-if="activeTemplate" class="preview-section">
        <h2 class="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          Vista previa de tarjeta activa
        </h2>
        <div class="preview-card">
          <div class="gift-card-preview" :style="{ backgroundImage: `url(${activeTemplate.image_url})` }">
            <div class="gc-type-label">GIFT CARD</div>
            <div class="gc-logo-preview">
              <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" />
            </div>
            <div class="gc-number-preview">DAM-2025-XXXX</div>
            <div class="gc-bottom-preview">
              <div>
                <div class="gc-label-preview">Saldo disponible</div>
                <div class="gc-balance-preview">$100.00</div>
              </div>
              <div style="text-align:right">
                <div class="gc-label-preview">Vence</div>
                <div class="gc-expiry-preview">12/2026</div>
              </div>
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
  name: 'AdminView',
  data() {
    return {
      token: null,
      adminUser: '',
      templates: [],
      loadingTemplates: false,
      newName: '',
      selectedFile: null,
      uploading: false,
      uploadError: null,
      uploadSuccess: null,
      actionLoading: null
    }
  },
  computed: {
    activeTemplate() {
      return this.templates.find(t => t.is_active)
    }
  },
  created() {
    this.token = takeAdminToken(this.$route, this.$router)
    if (this.token) {
      this.loadTemplates()
    }
  },
  methods: {
    async loadTemplates() {
      this.loadingTemplates = true
      try {
        const res = await api.getTemplates(this.token)
        this.templates = res.data
      } catch (err) {
        if (err.response?.status === 401) {
          this.token = null
        }
      } finally {
        this.loadingTemplates = false
      }
    },
    onFileSelect(e) {
      this.selectedFile = e.target.files[0] || null
      this.uploadError = null
    },
    async handleUpload() {
      this.uploadError = null
      this.uploadSuccess = null
      this.uploading = true
      try {
        const formData = new FormData()
        formData.append('name', this.newName)
        formData.append('image', this.selectedFile)
        await api.uploadTemplate(this.token, formData)
        this.uploadSuccess = `Diseño "${this.newName}" subido exitosamente`
        this.newName = ''
        this.selectedFile = null
        await this.loadTemplates()
        setTimeout(() => { this.uploadSuccess = null }, 3000)
      } catch (err) {
        this.uploadError = err.response?.data?.error || 'Error al subir el diseño'
      } finally {
        this.uploading = false
      }
    },
    async activateTemplate(t) {
      this.actionLoading = t.id
      try {
        await api.activateTemplate(this.token, t.id)
        await this.loadTemplates()
      } catch (err) {
        alert(err.response?.data?.error || 'Error al activar')
      } finally {
        this.actionLoading = null
      }
    },
    async deleteTemplate(t) {
      if (!confirm(`¿Eliminar el diseño "${t.name}"?`)) return
      this.actionLoading = t.id
      try {
        await api.deleteTemplate(this.token, t.id)
        await this.loadTemplates()
      } catch (err) {
        alert(err.response?.data?.error || 'Error al eliminar')
      } finally {
        this.actionLoading = null
      }
    },
    formatDate(iso) {
      return new Date(iso).toLocaleDateString('es-VE', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    },
    logout() {
      session.clearAdmin()
      this.$router.push('/admin-login')
    },
    getPreviewHtml(code) {
      return `<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#eee;font-family:'Poppins',sans-serif;overflow:hidden;transform:scale(0.7);transform-origin:center center}</style></head><body>${code}</body></html>`
    }
  }
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f5f5;
  font-family: 'Poppins', sans-serif;
}

/* Header */
.admin-header {
  background: #E1052D;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  box-shadow: 0 2px 12px rgba(225,5,45,0.3);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-logo {
  height: 36px;
  width: auto;
}
.header-left h1 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}
.header-sub {
  font-size: 0.75rem;
  opacity: 0.8;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.admin-user {
  font-size: 0.85rem;
  opacity: 0.9;
}
.btn-logout {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 8px 16px;
  border: 2px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  background: transparent;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover {
  background: rgba(255,255,255,0.15);
  border-color: #fff;
}
.btn-designer {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 8px 16px;
  border: 2px solid rgba(255,255,255,0.5);
  border-radius: 8px;
  background: rgba(255,255,255,0.12);
  color: #fff;
  cursor: pointer;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.btn-designer:hover {
  background: rgba(255,255,255,0.25);
  border-color: #fff;
}

/* Content */
.admin-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #222;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.count-badge {
  background: #E1052D;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
}

/* Upload */
.upload-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.upload-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.input-name {
  flex: 1;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  padding: 12px 16px;
  border: 2px solid #e5e5e5;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s;
}
.input-name:focus {
  border-color: #E1052D;
}
.file-input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  padding: 12px 16px;
  border: 2px dashed #ccc;
  border-radius: 10px;
  cursor: pointer;
  color: #888;
  white-space: nowrap;
  transition: all 0.2s;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-input-label:hover {
  border-color: #E1052D;
  color: #E1052D;
}
.file-input-label.has-file {
  border-color: #22c55e;
  color: #16a34a;
  border-style: solid;
}
.btn-upload {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  background: #E1052D;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.btn-upload:hover:not(:disabled) {
  background: #c5042a;
}
.btn-upload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.upload-error {
  margin-top: 12px;
  padding: 10px 14px;
  background: #fef2f2;
  color: #E1052D;
  border-radius: 8px;
  font-size: 0.85rem;
  border: 1px solid #fecaca;
}
.upload-success {
  margin-top: 12px;
  padding: 10px 14px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 8px;
  font-size: 0.85rem;
  border: 1px solid #bbf7d0;
}

/* Template Grid */
.templates-section {
  margin-bottom: 32px;
}
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.template-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.template-card.is-active {
  border-color: #E1052D;
  box-shadow: 0 4px 16px rgba(225,5,45,0.2);
}
.template-preview {
  position: relative;
  aspect-ratio: 1.586 / 1;
  overflow: hidden;
  background: #eee;
}
.template-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.active-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #E1052D;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.1em;
}
.type-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  font-size: 0.6rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  letter-spacing: 0.03em;
}
.type-html {
  background: rgba(59, 130, 246, 0.9);
  color: #fff;
}
.type-img {
  background: rgba(0,0,0,0.5);
  color: #fff;
}
.template-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  pointer-events: none;
}
.template-no-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddd;
  color: #888;
  font-size: 0.85rem;
}
.template-info {
  padding: 14px 16px 8px;
}
.template-info h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #222;
  margin: 0;
}
.template-date {
  font-size: 0.75rem;
  color: #999;
}
.template-actions {
  padding: 8px 16px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-activate {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #E1052D;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}
.btn-activate:hover:not(:disabled) {
  background: #c5042a;
}
.btn-delete {
  font-family: 'Poppins', sans-serif;
  padding: 8px;
  border: none;
  border-radius: 8px;
  background: #f5f5f5;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
  margin-left: auto;
}
.btn-delete:hover:not(:disabled) {
  background: #fef2f2;
  color: #E1052D;
}
.active-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #16a34a;
}

/* Preview */
.preview-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.preview-card {
  display: flex;
  justify-content: center;
  padding: 20px;
}
.gift-card-preview {
  width: 380px;
  aspect-ratio: 1.586 / 1;
  border-radius: 14px;
  padding: 24px;
  color: #fff;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background-size: cover;
  background-position: center;
  background-color: #E1052D;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}
.gift-card-preview::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(225,5,45,0.78) 0%, rgba(200,0,40,0.68) 50%, rgba(160,0,30,0.82) 100%);
  pointer-events: none;
}
.gift-card-preview .gc-type-label {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: rgba(255,255,255,0.75);
  z-index: 2;
}
.gc-logo-preview {
  z-index: 2;
}
.gc-logo-preview img {
  height: 28px;
  width: auto;
}
.gc-number-preview {
  font-family: monospace;
  font-size: 1rem;
  letter-spacing: 0.25em;
  opacity: 0.7;
  z-index: 2;
  margin-top: auto;
  margin-bottom: 12px;
}
.gc-bottom-preview {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  z-index: 2;
}
.gc-label-preview {
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.5);
  margin-bottom: 2px;
}
.gc-balance-preview {
  font-size: 1.5rem;
  font-weight: 600;
}
.gc-expiry-preview {
  font-size: 0.875rem;
  font-weight: 500;
}

/* States */
.loading-state, .empty-state, .admin-empty {
  text-align: center;
  padding: 48px 20px;
  color: #888;
}
.admin-empty {
  padding-top: 120px;
}
.admin-empty h2 {
  color: #333;
  margin-bottom: 8px;
}
.btn-primary {
  display: inline-block;
  margin-top: 16px;
  padding: 12px 24px;
  background: #E1052D;
  color: #fff;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e5e5;
  border-top-color: #E1052D;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 12px;
}
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
    padding: 16px;
  }
  .header-right {
    width: 100%;
    justify-content: center;
  }
  .upload-row {
    flex-direction: column;
  }
  .file-input-label {
    max-width: 100%;
    width: 100%;
    justify-content: center;
  }
  .template-grid {
    grid-template-columns: 1fr;
  }
  .gift-card-preview {
    width: 100%;
    max-width: 340px;
  }
}
</style>
