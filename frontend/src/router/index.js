import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { layout: 'blank' }
  },
  {
    path: '/',
    name: 'MisTarjetas',
    component: () => import('../views/MisTarjetasView.vue')
  },
  {
    path: '/tarjeta/:id',
    name: 'TarjetaDetalle',
    component: () => import('../views/TarjetaDetalleView.vue')
  },
  {
    path: '/movimientos',
    name: 'Movimientos',
    component: () => import('../views/MovimientosView.vue')
  },
  {
    path: '/caja',
    name: 'Caja',
    component: () => import('../views/CajaView.vue')
  },
  {
    path: '/admin-login',
    name: 'AdminLogin',
    component: () => import('../views/AdminLoginView.vue'),
    meta: { layout: 'blank' }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { layout: 'blank' }
  },
  {
    path: '/admin/designer',
    name: 'AdminDesigner',
    component: () => import('../views/AdminDesignerView.vue'),
    meta: { layout: 'blank' }
  },
  {
    path: '/admin/logos',
    name: 'AdminLogos',
    component: () => import('../views/AdminLogosView.vue'),
    meta: { layout: 'blank' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
