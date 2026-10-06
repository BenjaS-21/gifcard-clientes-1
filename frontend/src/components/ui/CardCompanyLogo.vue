<template>
  <img
    v-if="logo && logo.url"
    class="gc-company-logo"
    :src="secureUrl(logo.url)"
    :alt="logo.empresa || 'Logo de la empresa'"
    :style="logoStyle"
    draggable="false"
  />
</template>

<script setup>
import { computed } from 'vue'
import { secureUrl } from '../../services/secureUrl'

/* Logo de la empresa compradora sobre la Gift Card.
   x / y = centro del logo, width = ancho; todo en % de la tarjeta. */
const props = defineProps({
  logo: { type: Object, default: null }
})

const logoStyle = computed(() => ({
  left: props.logo.x + '%',
  top: props.logo.y + '%',
  width: props.logo.width + '%'
}))
</script>
