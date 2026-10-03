import axios from 'axios'
import { session } from './session'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://giftcardbackend.aplicacionesdamasco.com/api',
  headers: { 'Content-Type': 'application/json' }
})

// Sesiones de cliente y caja en cada petición
api.interceptors.request.use((config) => {
  const clientToken = session.clientToken()
  if (clientToken) config.headers['X-Client-Token'] = clientToken
  const cajaToken = session.cajaToken()
  if (cajaToken) config.headers['X-Caja-Token'] = cajaToken
  const vendedorToken = session.vendedorToken()
  if (vendedorToken) config.headers['X-Vendedor-Token'] = vendedorToken
  return config
})

// Sesión vencida: volver a pedir login (cliente) o PIN (caja)
api.interceptors.response.use((res) => res, (err) => {
  const code = err.response?.status === 401 ? err.response.data?.code : null
  if (code === 'client_auth') {
    session.clearClient()
    if (window.location.pathname !== '/login') window.location.assign('/login')
  } else if (code === 'caja_auth') {
    session.clearCaja()
    window.location.reload()
  } else if (code === 'vendedor_auth') {
    session.clearVendedor()
    if (window.location.pathname !== '/vendedor-login') window.location.assign('/vendedor-login')
  } else if (code === 'admin_auth') {
    session.clearAdmin()
  }
  return Promise.reject(err)
})

export default {
  // Dashboard
  getDashboardStats: () => api.get('/dashboard/stats/'),
  
  // Clientes
  getClients: (params = {}) => api.get('/clients/', { params }),
  getClient: (id) => api.get(`/clients/${id}/`),
  
  // Gift Cards
  getGiftCards: (params = {}) => api.get('/giftcards/', { params }),
  // Todas las páginas de gift cards (el endpoint pagina de 20 en 20 por defecto)
  getAllGiftCards: async (params = {}) => {
    const results = []
    for (let page = 1; ; page++) {
      const res = await api.get('/giftcards/', { params: { ...params, page, page_size: 100 } })
      results.push(...(res.data.results || []))
      if (page >= (res.data.total_pages || 1)) return results
    }
  },
  getGiftCard: (id) => api.get(`/giftcards/${id}/`),
  getGiftCardTransactions: (id) => api.get(`/giftcards/${id}/transactions/`),
  lookupGiftCard: (numero) => api.get('/giftcards/lookup/', { params: { numero } }),
  activateGiftCard: (data) => api.post('/giftcards/activate/', data),
  
  // Auth
  login: (data) => api.post('/auth/login/', data),  // sends { identificador }
  cajaLogin: (pin) => api.post('/caja/login/', { pin }),

  // Vendedores
  vendedorLogin: (username, password) => api.post('/vendedor/login/', { username, password }),
  getVendedorGiftCards: (params = {}) => api.get('/vendedor/giftcards/', { params }),
  getVendedorLotes: () => api.get('/vendedor/lotes/'),
  logout: () => api.post('/auth/logout/'),
  checkAuth: () => api.get('/auth/check/'),

  // Card Templates (público)
  getActiveTemplate: () => api.get('/card-templates/active/'),

  // Admin
  adminLogin: (username, password) => api.post('/admin/login/', { username, password }),
  getTemplates: (token) => api.get('/admin/templates/', {
    headers: { Authorization: `Token ${token}` }
  }),
  uploadTemplate: (token, formData) => api.post('/admin/templates/', formData, {
    headers: {
      Authorization: `Token ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  }),
  activateTemplate: (token, id) => api.post(`/admin/templates/${id}/activate/`, {}, {
    headers: { Authorization: `Token ${token}` }
  }),
  deleteTemplate: (token, id) => api.delete(`/admin/templates/${id}/`, {
    headers: { Authorization: `Token ${token}` }
  }),

  // Diseñador IA
  saveDesign: (token, data) => api.post('/admin/designs/', data, {
    headers: { Authorization: `Token ${token}` }
  }),

  // Logos de empresas compradoras (por lote)
  getCompanies: (token) => api.get('/admin/companies/', {
    headers: { Authorization: `Token ${token}` }
  }),
  createCompany: (token, formData) => api.post('/admin/companies/', formData, {
    headers: {
      Authorization: `Token ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  }),
  updateCompany: (token, id, formData) => api.patch(`/admin/companies/${id}/`, formData, {
    headers: {
      Authorization: `Token ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  }),
  deleteCompany: (token, id) => api.delete(`/admin/companies/${id}/`, {
    headers: { Authorization: `Token ${token}` }
  }),
  getLotes: (token) => api.get('/admin/lotes/', {
    headers: { Authorization: `Token ${token}` }
  }),

  // Gestión de vendedores (admin)
  getVendedores: (token) => api.get('/admin/vendedores/', {
    headers: { Authorization: `Token ${token}` }
  }),
  createVendedor: (token, data) => api.post('/admin/vendedores/', data, {
    headers: { Authorization: `Token ${token}` }
  }),
  updateVendedor: (token, id, data) => api.patch(`/admin/vendedores/${id}/`, data, {
    headers: { Authorization: `Token ${token}` }
  }),
}
