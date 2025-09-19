// Simple reusable print utility based on a temporary iframe

export function printHtml(title, html, options = {}) {
  const iframe = document.createElement('iframe')
  iframe.style.position = 'fixed'
  iframe.style.right = '0'
  iframe.style.bottom = '0'
  iframe.style.width = '0'
  iframe.style.height = '0'
  iframe.style.border = '0'
  document.body.appendChild(iframe)

  const doc = iframe.contentWindow?.document
  if (!doc) return

  const styles = `
    body { padding: 24px; }
    .table-sm td, .table-sm th { padding: .4rem; }
    code { background-color: #f8f9fa; padding: 2px 6px; border-radius: 4px; }
    ${options.extraCss || ''}
  `

  doc.open()
  doc.write(`<!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${title || 'Documento'}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" />
        <style>${styles}</style>
      </head>
      <body>
        ${html}
      </body>
    </html>`)
  doc.close()

  iframe.onload = () => {
    try {
      iframe.contentWindow?.focus()
      iframe.contentWindow?.print()
    } finally {
      setTimeout(() => iframe.remove(), 500)
    }
  }
}

export function printElement(selector, title, options) {
  const el = typeof selector === 'string' ? document.querySelector(selector) : selector
  if (!el) return
  printHtml(title, el.outerHTML, options)
}



