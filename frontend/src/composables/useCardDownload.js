/**
 * useCardDownload — Descarga la Gift Card renderizada como imagen PNG
 * para adjuntarla en un correo, una por una o todas juntas en un ZIP.
 *
 * Los elementos marcados con `data-export-ignore` (ej. botón copiar)
 * no aparecen en la imagen.
 */
import { ref } from 'vue'
import { toPng, toBlob, getFontEmbedCSS } from 'html-to-image'

const EXPORT_OPTIONS = {
  cacheBust: true,
  // Sin tilt 3D / hover ni sombra en la imagen exportada
  style: { transform: 'none', boxShadow: 'none', margin: '0' },
  filter: (node) => !(node.dataset && 'exportIgnore' in node.dataset)
}

function saveFile(href, filename) {
  const link = document.createElement('a')
  link.download = filename
  link.href = href
  link.click()
}

export function useCardDownload() {
  // Número de la tarjeta que se está descargando (null si ninguna)
  const downloading = ref(null)
  // Progreso de la descarga de todas: { done, total } (null si no hay descarga en curso)
  const bulkProgress = ref(null)

  async function downloadCard(el, numero) {
    if (!el || downloading.value || bulkProgress.value) return
    downloading.value = numero
    try {
      const dataUrl = await toPng(el, { ...EXPORT_OPTIONS, pixelRatio: 3 })
      saveFile(dataUrl, `giftcard-damasco-${numero || 'tarjeta'}.png`)
    } catch (e) {
      console.error('Error generando imagen de la tarjeta', e)
      alert('No se pudo generar la imagen de la tarjeta. Intenta de nuevo.')
    } finally {
      downloading.value = null
    }
  }

  /**
   * Descarga varias tarjetas en un ZIP con un PNG por tarjeta.
   * @param {Array<{el: HTMLElement, numero: string}>} cards
   * @param {string} zipName
   */
  async function downloadAllCards(cards, zipName) {
    const items = cards.filter(c => c.el)
    if (!items.length || downloading.value || bulkProgress.value) return
    bulkProgress.value = { done: 0, total: items.length }
    try {
      const { default: JSZip } = await import('jszip')
      const zip = new JSZip()
      // Las fuentes se incrustan una sola vez para todas las tarjetas
      const fontEmbedCSS = await getFontEmbedCSS(items[0].el)
      for (const { el, numero } of items) {
        // pixelRatio 2 para que el ZIP no pese demasiado con muchas tarjetas
        const blob = await toBlob(el, { ...EXPORT_OPTIONS, pixelRatio: 2, fontEmbedCSS })
        zip.file(`giftcard-damasco-${numero}.png`, blob)
        bulkProgress.value = { done: bulkProgress.value.done + 1, total: items.length }
      }
      const content = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(content)
      saveFile(url, zipName)
      setTimeout(() => URL.revokeObjectURL(url), 10000)
    } catch (e) {
      console.error('Error generando el ZIP de tarjetas', e)
      alert('No se pudieron descargar las tarjetas. Intenta de nuevo.')
    } finally {
      bulkProgress.value = null
    }
  }

  return { downloading, bulkProgress, downloadCard, downloadAllCards }
}
