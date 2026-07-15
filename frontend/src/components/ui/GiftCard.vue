<template>
  <div class="gift-card" :class="'gc-' + (color || 'black')" @click="$emit('click')">
    <div class="gc-logo">
      <div class="logo-dot">D</div>
      <span>DAMASCO</span>
    </div>
    <div class="gc-number">{{ numero }}</div>
    <div class="gc-bottom">
      <div>
        <div class="gc-label">Saldo disponible</div>
        <div class="gc-balance">${{ formatMoney(saldo) }}</div>
      </div>
      <div class="gc-expiry" v-if="vencimiento">
        <div class="gc-label">Vence</div>
        <div>{{ vencimiento }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  numero: { type: String, default: '**** **** ****' },
  saldo: { type: Number, default: 0 },
  color: { type: String, default: 'black' },
  vencimiento: { type: String, default: '' }
})
defineEmits(['click'])

const formatMoney = (val) => {
  return Number(val || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
