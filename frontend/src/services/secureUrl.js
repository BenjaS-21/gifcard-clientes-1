/**
 * secureUrl — Pasa a https las imágenes del backend cuando el portal se abre por https.
 *
 * En pantalla el navegador corrige solo una imagen http dentro de una página
 * https, pero al generar el PNG la imagen se vuelve a descargar con fetch, y
 * ahí el navegador la bloquea por contenido mixto y la descarga falla.
 */
export function secureUrl(url) {
  if (!url || typeof window === 'undefined' || window.location.protocol !== 'https:') return url
  return url.replace(/^http:\/\//i, 'https://')
}
