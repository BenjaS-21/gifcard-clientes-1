<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="header-logo">
        <img :src="logoDamasco" alt="Damasco" class="logo-img" />
      </router-link>

      <nav class="header-nav desktop-nav">
        <template v-if="!isCaja">
          <router-link to="/" class="header-link" :class="{ active: $route.path === '/' }">Mis Tarjetas</router-link>
          <router-link to="/movimientos" class="header-link" :class="{ active: $route.path === '/movimientos' }">Movimientos</router-link>
        </template>
        <template v-else>
          <router-link to="/caja" class="header-link" :class="{ active: $route.path === '/caja' }">Consulta Tarjeta</router-link>
        </template>
      </nav>

      <div class="header-actions">
        <div class="header-user" @click="showMenu = !showMenu">
          <div class="user-avatar">{{ userInitial }}</div>
          <span class="user-name">{{ userName }}</span>
        </div>
        
        <!-- Overlay for closing dropdown on mobile -->
        <div v-if="showMenu" class="dropdown-overlay" @click.stop="showMenu = false"></div>

        <div v-if="showMenu" class="header-dropdown" @click="showMenu = false">
          <button class="dropdown-item logout-btn" @click="handleLogout">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Mobile Bottom Nav -->
  <nav class="mobile-bottom-nav">
    <template v-if="!isCaja">
      <router-link to="/" class="bottom-nav-link" :class="{ active: $route.path === '/' }">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
          <line x1="1" y1="10" x2="23" y2="10"></line>
        </svg>
        <span>Tarjetas</span>
      </router-link>
      <router-link to="/movimientos" class="bottom-nav-link" :class="{ active: $route.path === '/movimientos' }">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8v4l3 3"></path>
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
        <span>Movimientos</span>
      </router-link>
    </template>
    <template v-else>
      <router-link to="/caja" class="bottom-nav-link" :class="{ active: $route.path === '/caja' }">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <span>Consulta</span>
      </router-link>
    </template>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logoDamasco from '@/assets/img/logo-damasco.svg'

const router = useRouter()
const showMenu = ref(false)

const isCaja = localStorage.getItem('userType') === 'caja'
const clienteStr = localStorage.getItem('cliente')
const cliente = clienteStr ? JSON.parse(clienteStr) : null
const userName = ref(isCaja ? 'Cajera' : (cliente?.nombre?.split(' ')[0] || 'Usuario'))
const userInitial = ref(isCaja ? 'C' : (cliente?.nombre || 'U')[0])

const handleLogout = () => {
  localStorage.removeItem('cliente')
  localStorage.removeItem('userType')
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 100;
}
.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  gap: var(--space-8);
}

/* Logo */
.header-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-img {
  height: 22px;
  width: auto;
}

/* Desktop Nav */
.header-nav {
  display: flex;
  gap: var(--space-2);
}
.header-link {
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--color-muted);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.header-link:hover {
  color: var(--color-foreground);
}
.header-link.active {
  color: var(--color-primary-inverse);
  background: var(--color-primary);
  font-weight: 500;
}

/* User Actions */
.header-actions { 
  position: relative; 
  display: flex;
  align-items: center;
}
.header-user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all var(--transition-fast);
  z-index: 102; /* Above overlay */
}
.header-user:hover { 
  background: rgba(0, 0, 0, 0.03); 
  border-color: rgba(0, 0, 0, 0.15);
}
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: var(--color-primary-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
}
.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-foreground);
}

/* Dropdown Overlay */
.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 101;
}

/* Dropdown */
.header-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: #FFFFFF;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: var(--radius-lg);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  min-width: 180px;
  overflow: hidden;
  z-index: 200;
  padding: 6px;
  animation: dropdownIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top right;
}
@keyframes dropdownIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-foreground);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  background: transparent;
  border: none;
  cursor: pointer;
}
.dropdown-item:hover { 
  background: var(--color-surface-hover); 
  color: var(--color-primary);
}
.dropdown-item svg {
  margin-right: 8px;
  opacity: 0.7;
}

/* Mobile Bottom Nav (Premium Floating Pill) */
.mobile-bottom-nav {
  display: none;
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  height: 64px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 100px;
  z-index: 90;
  padding: 8px;
  box-shadow: 0 16px 40px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.04), inset 0 1px 0 rgba(255,255,255,1);
  gap: 8px;
  width: max-content;
  max-width: 90vw;
}

.bottom-nav-link {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--color-muted);
  gap: 8px;
  padding: 0 20px;
  border-radius: 100px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  height: 100%;
}

.bottom-nav-link .nav-icon {
  width: 20px;
  height: 20px;
  stroke-width: 2.5;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  z-index: 2;
}

.bottom-nav-link span {
  font-size: 0.8125rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
  letter-spacing: -0.01em;
}

.bottom-nav-link:hover {
  color: var(--color-foreground);
  background: rgba(0, 0, 0, 0.03);
}

.bottom-nav-link.active {
  color: #ffffff;
  background: linear-gradient(135deg, var(--color-primary) 0%, #b31212 100%);
  box-shadow: 0 8px 24px rgba(220, 38, 38, 0.4), inset 0 1px 2px rgba(255,255,255,0.25);
}

.bottom-nav-link.active .nav-icon {
  transform: scale(1.15) rotate(-2deg);
}

/* Responsiveness */
@media (max-width: 768px) {
  .header-inner { gap: var(--space-4); }
  .header-link {
    padding: 6px 12px;
    font-size: 0.8125rem;
  }
}

@media (max-width: 640px) {
  .desktop-nav {
    display: none;
  }
  .mobile-bottom-nav {
    display: flex;
  }
  .header-inner {
    padding: 0 var(--space-4);
  }
  .logo-img {
    height: 18px;
  }
  .user-name {
    display: none;
  }
  .header-user {
    padding: 4px;
    border-radius: var(--radius-full);
    border: none;
    background: transparent;
  }
  .header-user:hover {
    background: transparent;
  }
  .user-avatar {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
  }
  .header-dropdown {
    right: 0;
    top: calc(100% + 8px);
    width: 160px;
  }
  
  /* Make pill smaller on very small screens */
  @media (max-width: 380px) {
    .bottom-nav-link {
      padding: 0 12px;
    }
    .bottom-nav-link span {
      font-size: 0.75rem;
    }
  }
}
</style>
