<template>
  <div class="designer-page">
    <header class="designer-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Diseñador de Tarjetas</h1>
          <span class="header-sub">Constructor Visual</span>
        </div>
      </div>
      <div class="header-right">
        <router-link :to="`/admin?token=${token}`" class="btn-back">← Panel Admin</router-link>
        <button class="btn-logout" @click="$router.push('/admin-login')">Cerrar Sesión</button>
      </div>
    </header>

    <div v-if="!token" class="designer-empty">
      <h2>Acceso no autorizado</h2>
      <router-link to="/admin-login" class="btn-primary">Iniciar Sesión</router-link>
    </div>

    <main v-else class="designer-content">
      <div class="designer-grid">
        <!-- LEFT: Controls -->
        <div class="controls-panel">

          <!-- Background -->
          <section class="ctrl-section">
            <h3 class="ctrl-title">🎨 Fondo</h3>
            <label class="ctrl-label">Tipo</label>
            <select v-model="cfg.bgType" class="ctrl-select">
              <option value="solid">Color Sólido</option>
              <option value="linear">Gradiente Lineal</option>
              <option value="radial">Gradiente Radial</option>
            </select>
            <div class="color-row">
              <div>
                <label class="ctrl-label">Color 1</label>
                <input type="color" v-model="cfg.bgColor1" class="ctrl-color" />
              </div>
              <div v-if="cfg.bgType !== 'solid'">
                <label class="ctrl-label">Color 2</label>
                <input type="color" v-model="cfg.bgColor2" class="ctrl-color" />
              </div>
            </div>
            <div v-if="cfg.bgType === 'linear'">
              <label class="ctrl-label">Ángulo: {{ cfg.gradientAngle }}°</label>
              <input type="range" v-model.number="cfg.gradientAngle" min="0" max="360" class="ctrl-range" />
            </div>
            <label class="ctrl-label">Imagen de fondo</label>
            <select v-model="cfg.bgImage" class="ctrl-select">
              <option value="none">Sin imagen</option>
              <option value="torre">Torre Damasco</option>
            </select>
            <div v-if="cfg.bgImage !== 'none'">
              <label class="ctrl-label">Opacidad imagen: {{ cfg.bgImageOpacity }}%</label>
              <input type="range" v-model.number="cfg.bgImageOpacity" min="5" max="100" class="ctrl-range" />
            </div>
          </section>

          <!-- Overlay -->
          <section class="ctrl-section">
            <h3 class="ctrl-title">🔲 Overlay</h3>
            <div class="ctrl-toggle-row">
              <label class="ctrl-label">Activar overlay</label>
              <input type="checkbox" v-model="cfg.overlayEnabled" class="ctrl-check" />
            </div>
            <div v-if="cfg.overlayEnabled">
              <div class="color-row">
                <div>
                  <label class="ctrl-label">Color</label>
                  <input type="color" v-model="cfg.overlayColor" class="ctrl-color" />
                </div>
              </div>
              <label class="ctrl-label">Opacidad: {{ cfg.overlayOpacity }}%</label>
              <input type="range" v-model.number="cfg.overlayOpacity" min="0" max="100" class="ctrl-range" />
            </div>
          </section>

          <!-- Decorations -->
          <section class="ctrl-section">
            <h3 class="ctrl-title">✨ Decoraciones</h3>
            <div class="ctrl-toggle-row">
              <label class="ctrl-label">Círculos</label>
              <input type="checkbox" v-model="cfg.decoCircles" class="ctrl-check" />
            </div>
            <div class="ctrl-toggle-row">
              <label class="ctrl-label">Líneas diagonales</label>
              <input type="checkbox" v-model="cfg.decoLines" class="ctrl-check" />
            </div>
            <div class="ctrl-toggle-row">
              <label class="ctrl-label">Brillo superior</label>
              <input type="checkbox" v-model="cfg.decoShine" class="ctrl-check" />
            </div>
          </section>

          <!-- Text & Logo -->
          <section class="ctrl-section">
            <h3 class="ctrl-title">🔤 Texto & Logo</h3>
            <label class="ctrl-label">Fuente</label>
            <select v-model="cfg.fontFamily" class="ctrl-select">
              <option value="'Poppins', sans-serif">Poppins</option>
              <option value="'Inter', sans-serif">Inter</option>
              <option value="'Roboto', sans-serif">Roboto</option>
              <option value="'Montserrat', sans-serif">Montserrat</option>
            </select>
            <div class="color-row">
              <div>
                <label class="ctrl-label">Color texto</label>
                <input type="color" v-model="cfg.textColor" class="ctrl-color" />
              </div>
              <div>
                <label class="ctrl-label">Color logo</label>
                <input type="color" v-model="cfg.logoColor" class="ctrl-color" />
              </div>
            </div>
          </section>

          <!-- Save -->
          <section class="ctrl-section save-section">
            <input v-model="designName" type="text" placeholder="Nombre (ej: Navidad 2026)" class="ctrl-input" required />
            <button class="btn-save" @click="saveDesign" :disabled="saving || !designName.trim()">
              <span v-if="!saving">💾 Guardar Diseño</span>
              <span v-else>Guardando...</span>
            </button>
            <div v-if="saveMsg" class="save-msg" :class="saveMsgType">{{ saveMsg }}</div>
          </section>
        </div>

        <!-- RIGHT: Preview -->
        <div class="preview-panel">
          <h3 class="preview-title">Vista Previa</h3>
          <div class="preview-wrapper">
            <div class="card-preview" :style="cardStyle">
              <!-- Background Image -->
              <div v-if="cfg.bgImage !== 'none'" class="card-bg-img" :style="bgImageStyle"></div>
              <!-- Overlay -->
              <div v-if="cfg.overlayEnabled" class="card-overlay" :style="overlayStyle"></div>
              <!-- Decorations -->
              <div v-if="cfg.decoCircles" class="deco-circle deco-circle-1"></div>
              <div v-if="cfg.decoCircles" class="deco-circle deco-circle-2"></div>
              <div v-if="cfg.decoLines" class="deco-lines"></div>
              <div v-if="cfg.decoShine" class="deco-shine"></div>
              <!-- Card Content -->
              <div class="card-inner" :style="{ fontFamily: cfg.fontFamily, color: cfg.textColor }">
                <div class="card-top">
                  <svg class="card-logo" :style="{ fill: cfg.logoColor }" viewBox="0 0 1652 199" xmlns="http://www.w3.org/2000/svg"><path d="M102.399 4.016H30.137L0 53.415h102.399c25.6 0 45.205 19.478 45.205 46.185 0 27.11-18.957 45.383-45.205 45.383H47.635V75.504H0v118.074h102.399c52.982 0 92.03-41.567 92.03-96.588C194.591 42.37 155.867 4.016 102.399 4.016z"/><path d="M621.201 128.717l14.583 66.869h47.797L644.371 26.507c-4.213-17.872-14.906-26.507-26.896-26.507-12.476 0-20.901 8.032-26.41 20.482l-24.79 54.62c-13.61 29.519-19.767 43.776-24.79 57.23-5.346-13.454-11.341-27.912-25.113-57.431l-24.79-54.218c-5.509-12.651-13.934-20.482-26.248-20.482-12.19 0-23.208 8.635-27.258 26.507L398.094 195.787h47.149l14.582-66.869c4.699-21.486 8.101-37.55 10.37-52.812 4.86 12.852 10.369 26.507 21.873 52.812l20.901 48.596c8.101 18.876 16.04 21.486 27.544 21.486 11.666 0 19.443-2.61 27.544-21.486l20.901-48.194c10.694-25.101 16.527-39.559 21.55-53.214 2.592 15.261 5.833 30.723 10.693 52.611z"/><path d="M1066.61 82.331H982.191c-11.179 0-16.526-3.815-16.526-13.454s5.347-13.254 16.526-13.254h107.589l30.78-49.999H985.918c-47.149 0-66.592 23.494-66.592 59.841 0 33.133 18.309 55.222 58.167 55.222h84.417c11.34 0 16.52 4.016 16.52 13.856s-5.02 14.056-16.52 14.056H944.602l-30.785 49.399h143.523c47.31 0 66.59-23.495 66.59-62.853-.16-35.141-20.57-52.812-57.32-52.812z"/><path d="M1226.69 56.226h75.18l29.81-48.194h-104.83c-51.85 0-90.09 36.547-90.09 90.966s38.24 94.58 90.09 94.58h75.18l29.81-47.591h-104.83c-25.28 0-43.91-18.073-43.91-44.379-.16-26.707 18.63-45.382 43.59-45.382z"/><path d="M1446.55 8.032c-71.77 0-107.74 28.916-107.74 94.179s35.8 94.379 107.74 94.379c71.62 0 107.75-29.117 107.75-94.379-.16-65.263-36.29-94.179-107.75-94.179zm0 141.168c-45.85 0-62.38-7.631-62.38-46.989 0-39.358 16.53-46.587 62.38-46.587s62.38 7.43 62.38 46.587c-.16 39.358-16.69 46.989-62.38 46.989z"/><path d="M389.02 196.189L307.36 7.631H267.34L185.68 196.189h42.45l16.527-37.752h85.225l16.364 37.752h42.774zM264.91 111.85l22.521-51.609 22.522 51.609H264.91z"/><path d="M780.633 7.631L698.973 196.189h42.45l16.527-37.752h85.225l16.364 37.752h42.775L820.653 7.631h-40.02zM778.203 111.85l22.521-51.609 23.522 51.609H778.203z"/></svg>
                  <span class="card-type">GIFT CARD</span>
                </div>
                <div class="card-number">DAM-2025-XXXX</div>
                <div class="card-bottom">
                  <div>
                    <div class="card-label">Saldo disponible</div>
                    <div class="card-balance">$100.00</div>
                  </div>
                  <div style="text-align:right">
                    <div class="card-label">Vence</div>
                    <div class="card-expiry">12/2026</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p class="preview-note">Las variables (logo, código, saldo, fecha) se llenan automáticamente con los datos reales de cada tarjeta.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/services/api'
import torreImg from '@/assets/img/torre-damasco-card.png'

export default {
  name: 'AdminDesignerView',
  data() {
    return {
      token: null,
      designName: '',
      saving: false,
      saveMsg: null,
      saveMsgType: '',
      cfg: {
        bgType: 'linear',
        bgColor1: '#E1052D',
        bgColor2: '#8B0000',
        gradientAngle: 135,
        bgImage: 'none',
        bgImageOpacity: 25,
        overlayEnabled: true,
        overlayColor: '#E1052D',
        overlayOpacity: 40,
        decoCircles: true,
        decoLines: false,
        decoShine: true,
        fontFamily: "'Poppins', sans-serif",
        textColor: '#FFFFFF',
        logoColor: '#FFFFFF'
      }
    }
  },
  computed: {
    cardStyle() {
      let bg
      if (this.cfg.bgType === 'solid') {
        bg = this.cfg.bgColor1
      } else if (this.cfg.bgType === 'linear') {
        bg = `linear-gradient(${this.cfg.gradientAngle}deg, ${this.cfg.bgColor1}, ${this.cfg.bgColor2})`
      } else {
        bg = `radial-gradient(circle at 30% 40%, ${this.cfg.bgColor1}, ${this.cfg.bgColor2})`
      }
      return { background: bg }
    },
    bgImageStyle() {
      const images = { torre: torreImg }
      const url = images[this.cfg.bgImage]
      if (!url) return {}
      return { backgroundImage: `url(${url})`, opacity: this.cfg.bgImageOpacity / 100 }
    },
    overlayStyle() {
      const c = this.cfg.overlayColor
      const r = parseInt(c.slice(1,3),16)
      const g = parseInt(c.slice(3,5),16)
      const b = parseInt(c.slice(5,7),16)
      return { background: `rgba(${r},${g},${b},${this.cfg.overlayOpacity/100})` }
    },
    generatedHtml() {
      const bg = this.cardStyle.background
      const ov = this.cfg.overlayEnabled ? `<div style="position:absolute;inset:0;${this.overlayStyle.background ? 'background:'+this.overlayStyle.background : ''};pointer-events:none;z-index:1"></div>` : ''
      const circles = this.cfg.decoCircles ? `<div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,0.08);pointer-events:none"></div><div style="position:absolute;bottom:-40px;left:-20px;width:160px;height:160px;border-radius:50%;background:rgba(255,255,255,0.05);pointer-events:none"></div>` : ''
      const lines = this.cfg.decoLines ? `<div style="position:absolute;inset:0;background:repeating-linear-gradient(45deg,transparent,transparent 20px,rgba(255,255,255,0.03) 20px,rgba(255,255,255,0.03) 22px);pointer-events:none"></div>` : ''
      const shine = this.cfg.decoShine ? `<div style="position:absolute;top:0;left:0;right:0;height:50%;background:linear-gradient(180deg,rgba(255,255,255,0.12) 0%,transparent 100%);pointer-events:none"></div>` : ''
      return `<div style="width:380px;height:240px;border-radius:14px;position:relative;overflow:hidden;background:${bg};font-family:${this.cfg.fontFamily};color:${this.cfg.textColor}">${ov}${circles}${lines}${shine}<div style="position:relative;z-index:2;padding:24px;display:flex;flex-direction:column;justify-content:space-between;height:100%"><div style="display:flex;justify-content:space-between;align-items:flex-start"><span style="font-size:1.1rem;font-weight:700;letter-spacing:0.05em">DAMASCO®</span><span style="font-size:0.7rem;font-weight:700;letter-spacing:0.2em;opacity:0.75">GIFT CARD</span></div><div style="font-family:monospace;font-size:1rem;letter-spacing:0.25em;opacity:0.7">DAM-2025-XXXX</div><div style="display:flex;justify-content:space-between;align-items:flex-end"><div><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;opacity:0.5;margin-bottom:2px">Saldo disponible</div><div style="font-size:1.5rem;font-weight:600">$100.00</div></div><div style="text-align:right"><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;opacity:0.5;margin-bottom:2px">Vence</div><div style="font-size:0.875rem;font-weight:500">12/2026</div></div></div></div></div>`
    }
  },
  created() {
    this.token = this.$route.query.token
  },
  methods: {
    async saveDesign() {
      this.saveMsg = null
      this.saving = true
      try {
        await api.saveDesign(this.token, {
          name: this.designName.trim(),
          html_code: this.generatedHtml
        })
        this.saveMsg = `"${this.designName}" guardado. Actívalo desde el Panel Admin.`
        this.saveMsgType = 'success'
        this.designName = ''
        setTimeout(() => { this.saveMsg = null }, 5000)
      } catch (err) {
        this.saveMsg = err.response?.data?.error || 'Error al guardar'
        this.saveMsgType = 'error'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.designer-page { min-height:100vh; background:#f5f5f5; font-family:'Poppins',sans-serif; }

.designer-header { background:linear-gradient(135deg,#E1052D,#b8042a); color:#fff; display:flex; align-items:center; justify-content:space-between; padding:16px 32px; box-shadow:0 2px 16px rgba(225,5,45,0.3); }
.header-left { display:flex; align-items:center; gap:16px; }
.header-logo { height:36px; }
.header-left h1 { font-size:1.25rem; font-weight:700; margin:0; }
.header-sub { font-size:0.75rem; opacity:0.8; }
.header-right { display:flex; gap:12px; }
.btn-back,.btn-logout { font-family:'Poppins',sans-serif; font-size:0.8rem; font-weight:600; padding:8px 16px; border:2px solid rgba(255,255,255,0.4); border-radius:8px; background:transparent; color:#fff; cursor:pointer; text-decoration:none; transition:all 0.2s; }
.btn-back:hover,.btn-logout:hover { background:rgba(255,255,255,0.15); border-color:#fff; }

.designer-content { max-width:1200px; margin:0 auto; padding:32px 24px; }
.designer-grid { display:grid; grid-template-columns:340px 1fr; gap:28px; align-items:start; }

/* Controls */
.controls-panel { display:flex; flex-direction:column; gap:16px; }
.ctrl-section { background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.ctrl-title { font-size:0.95rem; font-weight:700; color:#222; margin:0 0 14px; }
.ctrl-label { display:block; font-size:0.75rem; font-weight:600; color:#666; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px; margin-top:10px; }
.ctrl-label:first-child { margin-top:0; }
.ctrl-select { width:100%; font-family:'Poppins',sans-serif; font-size:0.85rem; padding:10px 12px; border:2px solid #e5e5e5; border-radius:8px; outline:none; background:#fff; cursor:pointer; }
.ctrl-select:focus { border-color:#E1052D; }
.color-row { display:flex; gap:16px; }
.ctrl-color { width:48px; height:36px; border:2px solid #e5e5e5; border-radius:8px; cursor:pointer; padding:2px; background:#fff; }
.ctrl-range { width:100%; accent-color:#E1052D; margin-top:4px; }
.ctrl-toggle-row { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.ctrl-check { width:18px; height:18px; accent-color:#E1052D; cursor:pointer; }
.ctrl-input { width:100%; font-family:'Poppins',sans-serif; font-size:0.85rem; padding:12px 14px; border:2px solid #e5e5e5; border-radius:8px; outline:none; margin-bottom:12px; }
.ctrl-input:focus { border-color:#E1052D; }
.btn-save { width:100%; font-family:'Poppins',sans-serif; font-size:0.9rem; font-weight:600; padding:14px; border:none; border-radius:10px; background:#E1052D; color:#fff; cursor:pointer; transition:background 0.2s; }
.btn-save:hover:not(:disabled) { background:#c5042a; }
.btn-save:disabled { opacity:0.5; cursor:not-allowed; }
.save-msg { margin-top:12px; padding:10px 14px; border-radius:8px; font-size:0.8rem; }
.save-msg.success { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.save-msg.error { background:#fef2f2; color:#E1052D; border:1px solid #fecaca; }

/* Preview */
.preview-panel { position:sticky; top:24px; }
.preview-title { font-size:1rem; font-weight:700; color:#222; margin:0 0 16px; }
.preview-wrapper { display:flex; justify-content:center; background:#e8e8e8; border-radius:14px; padding:32px; border:2px dashed #d0d0d0; }
.card-preview { width:380px; height:240px; border-radius:14px; position:relative; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.25); transition:all 0.3s ease; }
.card-bg-img { position:absolute; inset:0; background-size:cover; background-position:center; pointer-events:none; z-index:0; transition:opacity 0.3s; }
.card-overlay { position:absolute; inset:0; pointer-events:none; z-index:1; }

/* Decorations */
.deco-circle { position:absolute; border-radius:50%; pointer-events:none; }
.deco-circle-1 { top:-30px; right:-30px; width:120px; height:120px; background:rgba(255,255,255,0.08); }
.deco-circle-2 { bottom:-40px; left:-20px; width:160px; height:160px; background:rgba(255,255,255,0.05); }
.deco-lines { position:absolute; inset:0; background:repeating-linear-gradient(45deg,transparent,transparent 20px,rgba(255,255,255,0.03) 20px,rgba(255,255,255,0.03) 22px); pointer-events:none; }
.deco-shine { position:absolute; top:0; left:0; right:0; height:50%; background:linear-gradient(180deg,rgba(255,255,255,0.12) 0%,transparent 100%); pointer-events:none; }

/* Card Content */
.card-inner { position:relative; z-index:2; padding:24px; display:flex; flex-direction:column; justify-content:space-between; height:100%; }
.card-top { display:flex; justify-content:space-between; align-items:flex-start; }
.card-logo { height:24px; width:auto; transition: fill 0.3s; }
.card-type { font-size:0.7rem; font-weight:700; letter-spacing:0.2em; opacity:0.75; }
.card-number { font-family:monospace; font-size:1rem; letter-spacing:0.25em; opacity:0.7; }
.card-bottom { display:flex; justify-content:space-between; align-items:flex-end; }
.card-label { font-size:0.55rem; text-transform:uppercase; letter-spacing:0.1em; opacity:0.5; margin-bottom:2px; }
.card-balance { font-size:1.5rem; font-weight:600; }
.card-expiry { font-size:0.875rem; font-weight:500; }

.preview-note { text-align:center; font-size:0.75rem; color:#999; margin-top:14px; font-style:italic; }

.designer-empty { text-align:center; padding:120px 20px; color:#888; }
.designer-empty h2 { color:#333; margin-bottom:8px; }
.btn-primary { display:inline-block; margin-top:16px; padding:12px 24px; background:#E1052D; color:#fff; border-radius:10px; text-decoration:none; font-weight:600; }

@media (max-width: 900px) {
  .designer-header { flex-direction:column; gap:12px; padding:16px; text-align:center; }
  .header-right { justify-content:center; }
  .designer-grid { grid-template-columns:1fr; }
  .preview-panel { position:static; }
  .card-preview { width:100%; max-width:380px; }
}
</style>
