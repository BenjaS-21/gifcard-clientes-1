<template>
  <div class="login-page">
    <div class="login-card fade-up">
      <div class="login-header">
        <img :src="logoDamasco" alt="Damasco" class="login-logo" />
        <h2 style="margin:0;font-size:1.25rem;font-weight:700">Bienvenido</h2>
        <p class="text-secondary" style="margin-top:8px">{{ modoTarjeta ? 'Ingresa el número de tarjeta' : 'Ingresa tu cédula para validar tu tarjeta' }}</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Cédula mode -->
        <div v-if="!modoTarjeta" class="form-group">
          <label class="form-label">Cédula</label>
          <div class="cedula-row">
            <select v-model="cedulaTipo" class="form-select cedula-tipo">
              <option value="V">V</option>
              <option value="J">J</option>
              <option value="E">E</option>
            </select>
            <input
              class="form-input cedula-numero"
              type="text"
              v-model="cedulaNumero"
              placeholder="12345678"
              inputmode="numeric"
              @input="cedulaNumero = cedulaNumero.replace(/\D/g, '')"
              required
              autofocus
            />
          </div>
        </div>

        <!-- Tarjeta mode -->
        <div v-else class="form-group">
          <label class="form-label">Número de Tarjeta</label>
          <input
            class="form-input"
            type="text"
            v-model="tarjetaNumero"
            placeholder="Ej: 6A6KU3W8"
            required
            autofocus
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button type="submit" class="btn btn-primary btn-lg login-submit" :disabled="loading">
          {{ loading ? 'Verificando...' : 'Continuar' }}
        </button>
      </form>

      <div class="login-toggle">
        <button type="button" class="btn-link" @click="modoTarjeta = !modoTarjeta; error = ''">
          {{ modoTarjeta ? '← Buscar por cédula' : 'Tengo el número de tarjeta →' }}
        </button>
      </div>

      <div class="login-footer">
        <p>¿Problemas para ingresar? <a href="#" class="btn-link">Contacta soporte</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import logoDamasco from '@/assets/img/logo-damasco.svg'

const router = useRouter()
const modoTarjeta = ref(false)
const cedulaTipo = ref('V')
const cedulaNumero = ref('')
const tarjetaNumero = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  // Compose the identifier
  const identificador = modoTarjeta.value
    ? tarjetaNumero.value.trim()
    : `${cedulaTipo.value}-${cedulaNumero.value.trim()}`

  if (!identificador || (!modoTarjeta.value && !cedulaNumero.value.trim())) {
    error.value = 'Ingresa tu identificación'
    loading.value = false
    return
  }

  try {
    const res = await api.login({ identificador })
    const data = res.data

    if (data.tipo === 'tarjeta') {
      localStorage.setItem('userType', 'caja')
      router.push({ path: '/caja', query: { numero: data.numero_tarjeta } })
    } else if (data.tipo === 'cliente') {
      localStorage.setItem('userType', 'cliente')
      localStorage.setItem('cliente', JSON.stringify(data.cliente))
      router.push('/')
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al verificar'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--color-bg); padding: var(--space-4); position: relative; overflow: hidden;
}
.login-page::before {
  content: ''; position: absolute; top: -20vh; left: 50%; transform: translateX(-50%);
  width: 80vw; height: 80vw; max-width: 800px; max-height: 800px;
  background: radial-gradient(circle, rgba(200,16,46,0.04) 0%, transparent 60%); pointer-events: none;
}
.login-card {
  width: 100%; max-width: 420px; background: rgba(255,255,255,0.8);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0,0,0,0.08); border-radius: var(--radius-lg);
  padding: var(--space-10) var(--space-8); box-shadow: var(--shadow-hover); position: relative; z-index: 1;
}
.login-header { text-align: center; margin-bottom: var(--space-8); }
.login-logo { height: 28px; width: auto; margin: 0 auto var(--space-5); display: block; }
.login-submit { width: 100%; margin-top: var(--space-4); }
.login-error {
  color: var(--color-destructive); font-size: 0.875rem; text-align: center;
  margin-bottom: var(--space-4); padding: 10px;
  background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: var(--radius-sm);
}
.login-footer { margin-top: var(--space-8); text-align: center; font-size: 0.875rem; color: var(--color-muted); }

.login-toggle { text-align: center; margin-top: var(--space-5); }
.login-toggle .btn-link { font-size: 0.8125rem; font-weight: 500; }

.cedula-row { display: flex; gap: 8px; }
.cedula-tipo {
  width: 70px; padding: 10px 8px; font-size: 0.9375rem; font-weight: 600;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  background: var(--color-bg); color: var(--color-foreground);
  cursor: pointer; outline: none; text-align: center;
  transition: all var(--transition-fast);
  appearance: none; -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 8px center;
  padding-right: 24px;
}
.cedula-tipo:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(200,16,46,0.08); }
.cedula-numero { flex: 1; }
</style>
