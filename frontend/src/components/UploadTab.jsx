import React, { useState, useRef } from 'react'
import { uploadData } from '../api'
import './UploadTab.css'

const ACCEPTED = '.pdf,.xlsx,.csv,.docx,.txt'

export default function UploadTab({ onToast }) {
  const [mode, setMode]       = useState('file') // 'file' | 'url' | 'text'
  const [file, setFile]       = useState(null)
  const [url, setUrl]         = useState('')
  const [rawText, setRawText] = useState('')
  const [company, setCompany] = useState('')
  const [sector, setSector]   = useState('')
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading]   = useState(false)
  const [history, setHistory]   = useState([])
  const fileRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault(); setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) { setFile(f); setMode('file') }
  }

  async function handleSubmit() {
    if (loading) return
    if (mode === 'file' && !file)    return onToast('Vui lòng chọn file', 'error')
    if (mode === 'url'  && !url)     return onToast('Vui lòng nhập URL', 'error')
    if (mode === 'text' && !rawText) return onToast('Vui lòng nhập văn bản', 'error')
    if (!company)                    return onToast('Vui lòng nhập tên công ty', 'error')

    setLoading(true)
    try {
      const res = await uploadData({
        file:    mode === 'file' ? file    : null,
        url:     mode === 'url'  ? url     : null,
        text:    mode === 'text' ? rawText : null,
        company, sector,
      })
      const entry = {
        id: Date.now(),
        company, sector,
        source: mode === 'file' ? file.name : mode === 'url' ? url : 'raw text',
        chunks: res.chunks_stored ?? res.chunks ?? '?',
        time: new Date().toLocaleTimeString('vi', { hour: '2-digit', minute: '2-digit' }),
      }
      setHistory(h => [entry, ...h.slice(0, 9)])
      onToast(`Đã nạp ${entry.chunks} chunks cho ${company}`, 'success')
      // Reset
      setFile(null); setUrl(''); setRawText('')
    } catch (err) {
      onToast(`Lỗi upload: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-tab">
      <div className="upload-scroll">

        {/* Mode tabs */}
        <div className="mode-tabs">
          {['file','url','text'].map(m => (
            <button
              key={m}
              className={`mode-tab ${mode === m ? 'active' : ''}`}
              onClick={() => setMode(m)}
            >
              {m === 'file' ? '📄 File' : m === 'url' ? '🔗 URL' : '✏️ Văn bản'}
            </button>
          ))}
        </div>

        {/* Drop zone / input */}
        {mode === 'file' && (
          <div
            className={`drop-zone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            <input
              ref={fileRef} type="file" accept={ACCEPTED} style={{ display: 'none' }}
              onChange={e => e.target.files[0] && setFile(e.target.files[0])}
            />
            {file ? (
              <>
                <div className="drop-icon drop-icon-ok">✓</div>
                <div className="drop-name">{file.name}</div>
                <div className="drop-sub">{(file.size / 1024).toFixed(1)} KB · Bấm để đổi file</div>
              </>
            ) : (
              <>
                <div className="drop-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                </div>
                <div className="drop-name">Kéo thả hoặc bấm để chọn</div>
                <div className="drop-sub">PDF · Excel · CSV · DOCX · TXT · tối đa 20 MB</div>
              </>
            )}
          </div>
        )}

        {mode === 'url' && (
          <div className="url-input-wrap">
            <label className="form-label">URL tin tức / báo cáo</label>
            <input
              className="form-input"
              placeholder="https://cafef.vn/..."
              value={url}
              onChange={e => setUrl(e.target.value)}
            />
            <p className="url-hint">Hỗ trợ: CafeF, VnEconomy, Bloomberg, báo cáo thường niên</p>
          </div>
        )}

        {mode === 'text' && (
          <div className="form-group">
            <label className="form-label">Văn bản thô</label>
            <textarea
              className="form-input"
              style={{ minHeight: 120 }}
              placeholder="Dán nội dung báo cáo tài chính, tin tức, bình luận..."
              value={rawText}
              onChange={e => setRawText(e.target.value)}
            />
          </div>
        )}

        {/* Metadata */}
        <div className="meta-section">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Tên công ty *</label>
              <input
                className="form-input"
                placeholder="VD: Vinamilk, VHM, HPG..."
                value={company}
                onChange={e => setCompany(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Ngành</label>
              <input
                className="form-input"
                placeholder="VD: Tiêu dùng, BĐS..."
                value={sector}
                onChange={e => setSector(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <button
          className={`btn ${loading ? 'btn-ghost' : 'btn-primary'}`}
          onClick={handleSubmit}
          disabled={loading}
          style={{ marginTop: 4 }}
        >
          {loading
            ? <><div className="spinner" /> Đang xử lý...</>
            : <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                Nạp vào Vector Store
              </>
          }
        </button>

        {/* History */}
        {history.length > 0 && (
          <div className="upload-history">
            <div className="card-title" style={{ marginBottom: 8 }}>Lịch sử nạp dữ liệu</div>
            {history.map(h => (
              <div key={h.id} className="history-item">
                <div className="history-left">
                  <span className="history-company">{h.company}</span>
                  {h.sector && <span className="badge badge-muted">{h.sector}</span>}
                  <span className="history-source" title={h.source}>{h.source}</span>
                </div>
                <div className="history-right">
                  <span className="badge badge-teal">{h.chunks} chunks</span>
                  <span className="history-time">{h.time}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
