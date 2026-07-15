<template>
  <header class="navbar">
    <div class="navbar-left">
      <h2 class="navbar-title">{{ pageTitle }}</h2>
    </div>
    <div class="navbar-right">
      <div class="navbar-user">
        <div class="user-avatar">
          <span>A</span>
        </div>
        <div class="user-info">
          <span class="user-name">Admin</span>
          <span class="user-role">Damasco</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const titles = {
  '/': 'Dashboard',
  '/clientes': 'Clientes',
  '/giftcards': 'Gift Cards',
}

const pageTitle = computed(() => {
  if (route.path.startsWith('/clientes/')) return 'Detalle Cliente'
  if (route.path.startsWith('/giftcards/')) return 'Detalle Gift Card'
  return titles[route.path] || 'Damasco'
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: var(--sidebar-width);
  right: 0;
  height: var(--navbar-height);
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  z-index: 90;
  transition: left var(--transition-base);
}
.navbar-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
}
.navbar-right { display: flex; align-items: center; gap: 16px; }
.navbar-user { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
}
.user-info { display: flex; flex-direction: column; }
.user-name { font-size: 0.85rem; font-weight: 600; color: var(--color-text); }
.user-role { font-size: 0.7rem; color: var(--color-text-secondary); }

@media (max-width: 1024px) {
  .navbar { left: 0; }
}
</style>
