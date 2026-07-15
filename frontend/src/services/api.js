import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://giftcardbackend.aplicacionesdamasco.com/api',
  headers: { 'Content-Type': 'application/json' }
})

export default {
  // Dashboard
  getDashboardStats: () => api.get('/dashboard/stats/'),
  
  // Clientes
  getClients: (params = {}) => api.get('/clients/', { params }),
  getClient: (id) => api.get(`/clients/${id}/`),
  
  // Gift Cards
  getGiftCards: (params = {}) => api.get('/giftcards/', { params }),
  getGiftCard: (id) => api.get(`/giftcards/${id}/`),
  getGiftCardTransactions: (id) => api.get(`/giftcards/${id}/transactions/`),
  lookupGiftCard: (numero) => api.get('/giftcards/lookup/', { params: { numero } }),
  activateGiftCard: (data) => api.post('/giftcards/activate/', data),
  
  // Auth
  login: (data) => api.post('/auth/login/', data),  // sends { identificador }
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
}
