import React, { useState, useEffect } from 'react'
import ChatTab    from './components/ChatTab'
import UploadTab  from './components/UploadTab'
import PredictTab from './components/PredictTab'
import NewsTab    from './components/NewsTab'
import { getHealth } from './api'
import './App.css'

const TABS = [
  {
    id: 'chat',
    label: 'Chat',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
  },
  {
    id: 'upload',
    label: 'Upload',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
    ),
  },
  {
    id: 'predict',
    label: 'Dự đoán',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    ),
  },
  {
    id: 'news',
    label: 'Tin tức',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
        <path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>
      </svg>
    ),
  },
]

/* ── Toast ─────────────────────────────────────────────────── */
function ToastLayer({ toasts }) {
  return (
    <div className="toast-wrap">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.type === 'success' && '✓'}
          {t.type === 'error'   && '✕'}
          {t.type === 'info'    && 'ℹ'}
          {t.msg}
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [tab,    setTab]    = useState('chat')
  const [health, setHealth] = useState(null)  // null | 'ok' | 'err'
  const [toasts, setToasts] = useState([])

  /* Health check on mount */
  useEffect(() => {
    getHealth()
      .then(() => setHealth('ok'))
      .catch(() => setHealth('err'))
  }, [])

  function addToast(msg, type = 'info') {
    const id = Date.now()
    setToasts(t => [...t, { id, msg, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500)
  }

  return (
    <div className="app-shell">
      {/* Top bar */}
      <header className="app-topbar">
        <div className="app-logo">
          <div className="logo-mark">EA</div>
          <div className="logo-text">
            <span className="logo-title">Economic Agent</span>
            <span className="logo-sub">RAG · Trend Engine · Q&amp;A</span>
          </div>
        </div>

        <nav className="app-nav">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`nav-item ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
              aria-label={t.label}
            >
              {t.icon}
              <span>{t.label}</span>
            </button>
          ))}
        </nav>

        <div className="app-status">
          <div className={`status-dot ${health === 'ok' ? 'online' : health === 'err' ? 'offline' : 'pending'}`} />
          <span className="status-label mono">
            {health === 'ok' ? 'Backend online' : health === 'err' ? 'Backend offline' : 'Checking...'}
          </span>
        </div>
      </header>

      {/* Body */}
      <main className="app-body">
        {/* Mobile tab bar */}
        <div className="mobile-tabbar">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`mobile-tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
            >
              {t.icon}
              <span>{t.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="app-content">
          {tab === 'chat'    && <ChatTab    onToast={addToast} />}
          {tab === 'upload'  && <UploadTab  onToast={addToast} />}
          {tab === 'predict' && <PredictTab onToast={addToast} />}
          {tab === 'news'    && <NewsTab />}
        </div>
      </main>

      <ToastLayer toasts={toasts} />
    </div>
  )
}
