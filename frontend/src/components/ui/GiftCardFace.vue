<template>
  <div class="gift-card gift-card-face" :class="'gc-' + (gc.color || 'black')" :style="bgStyle">
    <div class="gc-type-label">GIFT CARD</div>
    <div class="gc-pattern"></div>
    <div class="gc-logo">
      <img src="@/assets/img/logo-damasco-white.svg" alt="Damasco" class="gc-logo-img" />
    </div>
    <CardCompanyLogo :logo="gc.empresa_logo" />
    <div class="gc-number">{{ gc.numero_tarjeta }}</div>
    <div class="gc-bottom">
      <div>
        <div class="gc-label">Saldo disponible</div>
        <div class="gc-balance">${{ formatMoney(saldoMostrado) }}</div>
      </div>
      <div class="gc-expiry" v-if="gc.fecha_vencimiento">
        <div class="gc-label">Vence</div>
        <div>{{ gc.fecha_vencimiento }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CardCompanyLogo from './CardCompanyLogo.vue'

/* Cara de la Gift Card tal como se descarga en PNG. */
const props = defineProps({
  gc: { type: Object, required: true },
  bgUrl: { type: String, default: null }
})

const bgStyle = computed(() => props.bgUrl ? { backgroundImage: `url(${props.bgUrl})` } : {})

/* Una tarjeta recién generada puede no tener U_Saldo cargado todavía:
   en ese caso se muestra el monto original con el que se emitió. */
const saldoMostrado = computed(() => {
  const estado = (props.gc.estado || '').toUpperCase()
  const sinVender = !estado || estado === 'GENERADA'
  return sinVender && !Number(props.gc.saldo) ? props.gc.saldo_inicial : props.gc.saldo
})

const formatMoney = (v) => Number(v || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
</script>

<style scoped>
.gift-card-face {
  max-width: 420px;
  border-radius: 16px;
  cursor: default;
}
.gift-card-face:hover { transform: none; }
.gc-logo-img {
  height: 20px;
  width: auto;
  opacity: 0.95;
}
.gc-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.06;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 20px, rgba(255,255,255,1) 20px, rgba(255,255,255,1) 21px);
  pointer-events: none;
  z-index: 1;
  border-radius: inherit;
}
</style>
