const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

/* ── /health ──────────────────────────────────────────────── */
export async function getHealth() {
  return request('/health')
}

/* ── /ask  ────────────────────────────────────────────────── */
export async function ask({ question, company = '', sector = '' }) {
  return request('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, company, sector }),
  })
}

/* ── /upload (file / url / text) ─────────────────────────── */
export async function uploadData({ file, url, text, company, sector }) {
  const form = new FormData()
  if (file) {
    form.append('file', file)
    form.append('source_type', 'file')
  } else if (url) {
    form.append('url', url)
    form.append('source_type', 'url')
  } else {
    form.append('text', text)
    form.append('source_type', 'text')
  }
  if (company) form.append('company', company)
  if (sector)  form.append('sector', sector)

  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

/* ── /predict ─────────────────────────────────────────────── */
export async function predict({ company, financialSignals, sentimentSignals, macroSignals }) {
  return request('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company,
      financial_signals: financialSignals,
      sentiment_signals: sentimentSignals,
      macro_signals:     macroSignals,
    }),
  })
}
