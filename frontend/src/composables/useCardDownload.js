/**
 * useCardDownload — Descarga la Gift Card renderizada como imagen PNG
 * para adjuntarla en un correo.
 *
 * Los elementos marcados con `data-export-ignore` (ej. botón copiar)
 * no aparecen en la imagen.
 */
import { ref } from 'vue'
import { toPng } from 'html-to-image'

export function useCardDownload() {
  // Número de la tarjeta que se está descargando (null si ninguna)
  const downloading = ref(null)

  async function downloadCard(el, numero) {
    if (!el || downloading.value) return
    downloading.value = numero
    try {
      const dataUrl = await toPng(el, {
        pixelRatio: 3,
        cacheBust: true,
        // Sin tilt 3D / hover ni sombra en la imagen exportada
        style: { transform: 'none', boxShadow: 'none', margin: '0' },
        filter: (node) => !(node.dataset && 'exportIgnore' in node.dataset)
      })
      const link = document.createElement('a')
      link.download = `giftcard-damasco-${numero || 'tarjeta'}.png`
      link.href = dataUrl
      link.click()
    } catch (e) {
      console.error('Error generando imagen de la tarjeta', e)
      alert('No se pudo generar la imagen de la tarjeta. Intenta de nuevo.')
    } finally {
      downloading.value = null
    }
  }

  return { downloading, downloadCard }
}
