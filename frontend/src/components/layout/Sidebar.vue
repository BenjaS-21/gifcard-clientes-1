<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <span>D</span>
      </div>
      <transition name="fade">
        <span v-if="!isCollapsed" class="logo-text">DAMASCO</span>
      </transition>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path || ($route.path.startsWith(item.path) && item.path !== '/') }"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <transition name="fade">
          <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        </transition>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <button class="nav-item" @click="isCollapsed = !isCollapsed">
        <span class="nav-icon" v-html="isCollapsed ? '&#9654;' : '&#9664;'"></span>
        <transition name="fade">
          <span v-if="!isCollapsed" class="nav-label">Colapsar</span>
        </transition>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'

const isCollapsed = ref(false)

const navItems = [
  { path: '/', label: 'Dashboard', icon: '&#9632;' },
  { path: '/clientes', label: 'Clientes', icon: '&#9787;' },
  { path: '/giftcards', label: 'Gift Cards', icon: '&#9733;' },
]
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: linear-gradient(180deg, var(--color-dark) 0%, var(--color-dark-secondary) 100%);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width var(--transition-base);
  overflow: hidden;
}
.sidebar.collapsed { width: 72px; }

.sidebar-logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-icon span {
  color: white;
  font-weight: 900;
  font-size: 1.1rem;
}
.logo-text {
  color: white;
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: 0.1em;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: rgba(255,255,255,0.6);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--transition-fast);
  cursor: pointer;
  border: none;
  background: transparent;
  text-decoration: none;
  width: 100%;
  text-align: left;
}
.nav-item:hover {
  color: white;
  background: rgba(255,255,255,0.08);
}
.nav-item.active {
  color: white;
  background: var(--color-primary);
  box-shadow: 0 4px 12px rgba(227,24,55,0.3);
}
.nav-icon { font-size: 1.1rem; flex-shrink: 0; width: 24px; text-align: center; }
.nav-label { white-space: nowrap; }

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 1024px) {
  .sidebar { transform: translateX(-100%); }
}
</style>
