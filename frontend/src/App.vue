<template>
  <div class="app-shell">
    <template v-if="$route.meta.layout === 'blank'">
      <router-view />
    </template>
    <template v-else>
      <AppHeader />
      <main class="app-content">
        <router-view />
      </main>
    </template>
  </div>
</template>

<script setup>
import AppHeader from './components/layout/AppHeader.vue'
</script>

<style>
#app { width: 100%; min-height: 100vh; }

@media (max-width: 640px) {
  #app {
    padding-bottom: calc(65px + env(safe-area-inset-bottom));
  }
}
</style>
