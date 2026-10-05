<template>
  <div class="dash-page">
    <header class="page-header">
      <div class="header-left">
        <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="header-logo" />
        <div>
          <h1>Dashboard</h1>
          <span class="header-sub">Venta y uso de las Gift Cards</span>
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
      <GiftDashboard :admin-token="token" />
    </main>
  </div>
</template>

<script>
import { session, takeAdminToken } from '@/services/session'
import GiftDashboard from '@/components/dashboard/GiftDashboard.vue'

export default {
  name: 'AdminDashboardView',
  components: { GiftDashboard },
  data() {
    return { token: null }
  },
  created() {
    this.token = takeAdminToken(this.$route, this.$router)
  },
  methods: {
    logout() {
      session.clearAdmin()
      this.$router.push('/admin-login')
    }
  }
}
</script>

<style scoped>
.dash-page { min-height: 100vh; background: #f5f5f5; font-family: 'Poppins', sans-serif; }
.page-header { background: linear-gradient(135deg, #E1052D, #b8042a); color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 16px 32px; box-shadow: 0 2px 16px rgba(225,5,45,0.3); }
.header-left { display: flex; align-items: center; gap: 16px; }
.header-logo { height: 36px; }
.header-left h1 { font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-sub { font-size: 0.75rem; opacity: 0.8; }
.header-right { display: flex; gap: 12px; }
.btn-back, .btn-logout { font-family: 'Poppins', sans-serif; font-size: 0.8rem; font-weight: 600; padding: 8px 16px; border: 2px solid rgba(255,255,255,0.4); border-radius: 8px; background: transparent; color: #fff; cursor: pointer; text-decoration: none; transition: all 0.2s; }
.btn-back:hover, .btn-logout:hover { background: rgba(255,255,255,0.15); border-color: #fff; }
.page-content { max-width: 1280px; margin: 0 auto; padding: 28px 24px 48px; }
.page-empty { text-align: center; padding: 120px 20px; color: #888; }
.page-empty h2 { color: #333; margin-bottom: 8px; }
.btn-primary { display: inline-block; margin-top: 16px; padding: 12px 24px; background: #E1052D; color: #fff; border-radius: 10px; text-decoration: none; font-weight: 600; }
@media (max-width: 760px) {
  .page-header { flex-direction: column; gap: 12px; padding: 16px; text-align: center; }
  .page-content { padding: 20px 16px 40px; }
}
</style>
