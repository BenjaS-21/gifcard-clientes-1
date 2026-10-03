/**
 * session.js — Tokens de sesión del portal.
 *
 * - Cliente: localStorage (se mantiene al cerrar el navegador; vence en el servidor a las 8 h).
 * - Caja y admin: sessionStorage (se borran al cerrar la pestaña).
 *
 * El storage puede no estar disponible (modo privado, bloqueado): toda
 * lectura y escritura va protegida y en ese caso simplemente no hay sesión.
 */
function read(store, key) {
  try { return store.getItem(key) } catch { return null }
}

function write(store, key, value) {
  try {
    if (value == null) store.removeItem(key)
    else store.setItem(key, value)
  } catch { /* sin storage: la sesión no se guarda */ }
}

export const session = {
  // Cliente
  clientToken: () => read(localStorage, 'clientToken'),
  setClient(cliente, token) {
    write(localStorage, 'userType', 'cliente')
    write(localStorage, 'cliente', JSON.stringify(cliente))
    write(localStorage, 'clientToken', token)
  },
  clearClient() {
    write(localStorage, 'cliente', null)
    write(localStorage, 'userType', null)
    write(localStorage, 'clientToken', null)
  },

  // Caja
  cajaToken: () => read(sessionStorage, 'cajaToken'),
  setCajaToken: (token) => write(sessionStorage, 'cajaToken', token),
  clearCaja: () => write(sessionStorage, 'cajaToken', null),

  // Vendedor (localStorage: lo usan a diario; vence en el servidor a las 12 h)
  vendedorToken: () => read(localStorage, 'vendedorToken'),
  vendedorNombre: () => read(localStorage, 'vendedorNombre'),
  setVendedor(token, nombre) {
    write(localStorage, 'vendedorToken', token)
    write(localStorage, 'vendedorNombre', nombre)
  },
  clearVendedor() {
    write(localStorage, 'vendedorToken', null)
    write(localStorage, 'vendedorNombre', null)
  },

  // Admin
  adminToken: () => read(sessionStorage, 'adminToken'),
  setAdminToken: (token) => write(sessionStorage, 'adminToken', token),
  clearAdmin: () => write(sessionStorage, 'adminToken', null)
}

/**
 * Token admin para las vistas del panel. Si llega en la URL (enlaces
 * viejos con ?token=), lo guarda y lo quita de la barra de direcciones.
 */
export function takeAdminToken(route, router) {
  if (route.query.token) {
    session.setAdminToken(route.query.token)
    const { token, ...query } = route.query
    router.replace({ path: route.path, query })
  }
  return session.adminToken()
}
