<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <div class="login-header">
        <img src="@/assets/img/logo-damasco.svg" alt="Damasco" class="login-logo" />
        <h1>Panel Administrativo</h1>
        <p class="login-sub">Gift Cards · Gestión de Templates</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Usuario</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Ingrese su usuario"
            autocomplete="username"
            :disabled="loading"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Ingrese su contraseña"
            autocomplete="current-password"
            :disabled="loading"
            required
          />
        </div>

        <div v-if="error" class="login-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ error }}
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          <span v-if="!loading">Iniciar Sesión</span>
          <span v-else class="btn-loading">
            <span class="spinner-sm"></span>
            Autenticando...
          </span>
        </button>
      </form>

      <div class="login-footer">
        <span>© {{ new Date().getFullYear() }} Damasco · Todos los derechos reservados</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { session } from '@/services/session'

export default {
  name: 'AdminLoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.error = null
      this.loading = true
      try {
        const res = await api.adminLogin(this.username, this.password)
        // El token se guarda en la pestaña, no en la URL
        session.setAdminToken(res.data.token)
        this.$router.push('/admin')
      } catch (err) {
        this.error = err.response?.data?.error || 'Error al conectar con el servidor'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E1052D 0%, #b5042a 50%, #8a0320 100%);
  padding: 20px;
}

.admin-login-card {
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-logo {
  height: 48px;
  width: auto;
  margin-bottom: 16px;
}

.login-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #111;
  margin: 0;
}

.login-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #888;
  margin-top: 4px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group input {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  padding: 12px 16px;
  border: 2px solid #e5e5e5;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s;
  color: #111;
  background: #fafafa;
}

.form-group input:focus {
  border-color: #E1052D;
  background: #fff;
}

.form-group input::placeholder {
  color: #bbb;
}

.login-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  color: #E1052D;
  font-size: 0.875rem;
  font-family: 'Poppins', sans-serif;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.btn-login {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  padding: 14px;
  border: none;
  border-radius: 10px;
  background: #E1052D;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-login:hover:not(:disabled) {
  background: #c5042a;
  transform: translateY(-1px);
}

.btn-login:active:not(:disabled) {
  transform: translateY(0);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner-sm {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  color: #aaa;
}

@media (max-width: 480px) {
  .admin-login-card {
    padding: 32px 24px;
  }
}
</style>
