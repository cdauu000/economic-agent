import React, { useState, useRef, useEffect } from 'react'
import { ask } from '../api'
import ResultCard from './ResultCard'
import './ChatTab.css'

const WELCOME = {
  id: 'welcome',
  role: 'bot',
  type: 'text',
  text: 'Xin chào! Tôi là Economic Agent — trợ lý phân tích tài chính của bạn.\n\nBạn có thể hỏi tôi về báo cáo tài chính, xu hướng kinh tế, rủi ro đầu tư hoặc dự đoán ngắn hạn.',
  time: new Date().toLocaleTimeString('vi', { hour: '2-digit', minute: '2-digit' }),
}

function formatTime() {
  return new Date().toLocaleTimeString('vi', { hour: '2-digit', minute: '2-digit' })
}

export default function ChatTab() {
  const [messages, setMessages]   = useState([WELCOME])
  const [input, setInput]         = useState('')
  const [company, setCompany]     = useState('')
  const [sector, setSector]       = useState('')
  const [loading, setLoading]     = useState(false)
  const [showContext, setShowContext] = useState(false)
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send() {
    const q = input.trim()
    if (!q || loading) return
    setInput('')

    const userMsg = { id: Date.now(), role: 'user', type: 'text', text: q, time: formatTime() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const data = await ask({ question: q, company, sector })

      // Backend có thể trả về { answer, result } hoặc chỉ { answer }
      const botMsg = {
        id: Date.now() + 1,
        role: 'bot',
        type: data.result ? 'rich' : 'text',
        text: data.answer || data.response || JSON.stringify(data),
        result: data.result || null,
        sources: data.sources || [],
        time: formatTime(),
      }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'bot',
        type: 'error',
        text: `Lỗi: ${err.message}`,
        time: formatTime(),
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  function clearChat() {
    setMessages([WELCOME])
  }

  return (
    <div className="chat-tab">
      {/* Context bar */}
      <div className="chat-context-bar">
        <button
          className={`context-toggle ${showContext ? 'active' : ''}`}
          onClick={() => setShowContext(p => !p)}
          title="Bộ lọc ngữ cảnh"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
          </svg>
          Ngữ cảnh
          {(company || sector) && <span className="context-badge">●</span>}
        </button>
        {showContext && (
          <div className="context-fields">
            <input
              className="form-input context-input"
              placeholder="Công ty (VD: Vinamilk)"
              value={company}
              onChange={e => setCompany(e.target.value)}
            />
            <input
              className="form-input context-input"
              placeholder="Ngành (VD: Tiêu dùng)"
              value={sector}
              onChange={e => setSector(e.target.value)}
            />
          </div>
        )}
        <button className="btn btn-ghost btn-clear" onClick={clearChat} title="Xóa lịch sử">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="1 4 1 10 7 10"/><polyline points="23 20 23 14 17 14"/>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`msg msg-${msg.role}`}>
            {msg.role === 'bot' && (
              <div className="msg-avatar">
                <span>EA</span>
              </div>
            )}
            <div className="msg-body">
              {msg.type === 'rich' ? (
                <>
                  <div className="msg-bubble msg-bubble-bot">
                    {msg.text && <p style={{ marginBottom: msg.result ? 8 : 0 }}>{msg.text}</p>}
                    <ResultCard data={msg.result} />
                  </div>
                  {msg.sources?.length > 0 && (
                    <div className="msg-sources">
                      {msg.sources.map((s, i) => (
                        <span key={i} className="badge badge-muted">{s}</span>
                      ))}
                    </div>
                  )}
                </>
              ) : msg.type === 'error' ? (
                <div className="msg-bubble msg-bubble-error">{msg.text}</div>
              ) : msg.role === 'user' ? (
                <div className="msg-bubble msg-bubble-user">{msg.text}</div>
              ) : (
                <div className="msg-bubble msg-bubble-bot">
                  {msg.text.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < msg.text.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
              )}
              <span className="msg-time">{msg.time}</span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg msg-bot">
            <div className="msg-avatar"><span>EA</span></div>
            <div className="msg-body">
              <div className="msg-bubble msg-bubble-bot msg-thinking">
                <div className="dot-pulse">
                  <span /><span /><span />
                </div>
                <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 4 }}>
                  Đang phân tích...
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            ref={inputRef}
            className="chat-textarea"
            placeholder="Hỏi về tài chính, xu hướng, rủi ro..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
          />
          <button
            className="chat-send-btn"
            onClick={send}
            disabled={!input.trim() || loading}
            aria-label="Gửi"
          >
            {loading
              ? <div className="spinner" />
              : (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              )
            }
          </button>
        </div>
        <p className="chat-hint">Enter gửi · Shift+Enter xuống dòng</p>
      </div>
    </div>
  )
}
