import React, { useState, useMemo } from 'react'
import { predict } from '../api'
import ResultCard from './ResultCard'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts'
import './PredictTab.css'

const FINANCIAL_SIGNALS = [
  { key: 'revenue_up',      label: 'Doanh thu tăng',        weight: +2 },
  { key: 'revenue_down',    label: 'Doanh thu giảm',        weight: -2 },
  { key: 'cost_up',         label: 'Chi phí tăng',          weight: -1 },
  { key: 'cost_down',       label: 'Chi phí giảm',          weight: +1 },
  { key: 'margin_stable',   label: 'Biên lợi nhuận ổn',     weight: +1 },
  { key: 'margin_down',     label: 'Biên lợi nhuận giảm',   weight: -2 },
  { key: 'profit_up',       label: 'Lợi nhuận tăng',        weight: +2 },
  { key: 'debt_up',         label: 'Nợ tăng',               weight: -1 },
]
const SENTIMENT_SIGNALS = [
  { key: 'positive_news',   label: 'Tin tức tích cực',      weight: +2 },
  { key: 'negative_news',   label: 'Tin tức tiêu cực',      weight: -2 },
  { key: 'neutral',         label: 'Trung tính',            weight:  0 },
  { key: 'analyst_upgrade', label: 'Nâng hạng analyst',     weight: +2 },
  { key: 'analyst_downgrade',label:'Hạ hạng analyst',       weight: -2 },
]
const MACRO_SIGNALS = [
  { key: 'policy_support',   label: 'Hỗ trợ chính sách',   weight: +2 },
  { key: 'interest_rate_down',label:'Lãi suất giảm',        weight: +1 },
  { key: 'interest_rate_up', label: 'Lãi suất tăng',        weight: -1 },
  { key: 'fx_risk',          label: 'Rủi ro tỷ giá',        weight: -1 },
  { key: 'gdp_growth',       label: 'GDP tăng trưởng',      weight: +1 },
]

function calcScore(checked, signals, weight) {
  const maxPos = signals.reduce((s, sg) => s + Math.max(0, sg.weight * 2), 0)
  const actual = signals
    .filter(sg => checked.has(sg.key))
    .reduce((s, sg) => s + (sg.weight + 2), 0)
  return maxPos > 0 ? Math.round((actual / maxPos) * 100) : 0
}

export default function PredictTab({ onToast }) {
  const [company, setCompany] = useState('')
  const [checked, setChecked] = useState(new Set())
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)

  function toggle(key) {
    setChecked(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  const fScore = useMemo(() => calcScore(checked, FINANCIAL_SIGNALS, 0.5), [checked])
  const sScore = useMemo(() => calcScore(checked, SENTIMENT_SIGNALS, 0.3), [checked])
  const mScore = useMemo(() => calcScore(checked, MACRO_SIGNALS, 0.2),     [checked])
  const total  = useMemo(
    () => Math.round(fScore * 0.5 + sScore * 0.3 + mScore * 0.2),
    [fScore, sScore, mScore]
  )

  const radarData = [
    { subject: 'Tài chính', value: fScore },
    { subject: 'Sentiment', value: sScore },
    { subject: 'Vĩ mô',    value: mScore },
  ]

  async function handlePredict() {
    if (!company) return onToast('Vui lòng nhập tên công ty', 'error')
    setLoading(true)
    try {
      const res = await predict({
        company,
        financialSignals: FINANCIAL_SIGNALS.filter(s => checked.has(s.key)).map(s => s.key),
        sentimentSignals: SENTIMENT_SIGNALS.filter(s => checked.has(s.key)).map(s => s.key),
        macroSignals:     MACRO_SIGNALS.filter(s => checked.has(s.key)).map(s => s.key),
      })
      setResult(res)
    } catch (err) {
      onToast(`Lỗi: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const trendLabel = total >= 65 ? 'Tích cực' : total >= 45 ? 'Trung tính' : 'Tiêu cực'
  const trendCls   = total >= 65 ? 'teal' : total >= 45 ? 'amber' : 'coral'

  return (
    <div className="predict-tab">
      <div className="predict-scroll">

        {/* Company */}
        <div className="form-group">
          <label className="form-label">Tên công ty *</label>
          <input
            className="form-input"
            placeholder="VD: Vinamilk, VHM..."
            value={company}
            onChange={e => setCompany(e.target.value)}
          />
        </div>

        {/* Score preview */}
        <div className="score-preview">
          <div className="score-preview-main">
            <div className={`score-big badge-${trendCls}`}>{total}</div>
            <div className="score-big-label">/ 100</div>
            <span className={`badge badge-${trendCls}`}>{trendLabel}</span>
          </div>
          <div className="score-breakdown">
            <div className="score-row">
              <span>Tài chính <span className="mono text-muted">50%</span></span>
              <span className="mono text-teal">{fScore}</span>
            </div>
            <div className="score-row">
              <span>Sentiment <span className="mono text-muted">30%</span></span>
              <span className="mono text-amber">{sScore}</span>
            </div>
            <div className="score-row">
              <span>Vĩ mô <span className="mono text-muted">20%</span></span>
              <span className="mono text-blue">{mScore}</span>
            </div>
          </div>
          <div className="radar-wrap">
            <ResponsiveContainer width="100%" height={120}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#30363D" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#8B949E', fontSize: 10 }} />
                <Radar dataKey="value" stroke="#E3A140" fill="#E3A140" fillOpacity={0.2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Signal groups */}
        <SignalGroup
          title="Tài chính" subtitle="50%" color="teal"
          signals={FINANCIAL_SIGNALS} checked={checked} toggle={toggle}
        />
        <SignalGroup
          title="Sentiment" subtitle="30%" color="amber"
          signals={SENTIMENT_SIGNALS} checked={checked} toggle={toggle}
        />
        <SignalGroup
          title="Vĩ mô" subtitle="20%" color="blue"
          signals={MACRO_SIGNALS} checked={checked} toggle={toggle}
        />

        {/* Run */}
        <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>
          {loading
            ? <><div className="spinner" /> Đang phân tích...</>
            : <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Chạy phân tích → /predict
              </>
          }
        </button>

        {/* Result */}
        {result && (
          <div>
            <div className="card-title" style={{ marginBottom: 6 }}>Kết quả từ backend</div>
            <ResultCard data={result} />
          </div>
        )}
      </div>
    </div>
  )
}

function SignalGroup({ title, subtitle, color, signals, checked, toggle }) {
  return (
    <div className="signal-group">
      <div className="signal-group-header">
        <span className="signal-group-title">{title}</span>
        <span className={`badge badge-${color}`}>{subtitle}</span>
      </div>
      <div className="signal-list">
        {signals.map(s => {
          const on = checked.has(s.key)
          return (
            <label key={s.key} className={`signal-item ${on ? 'checked' : ''}`}>
              <input
                type="checkbox"
                checked={on}
                onChange={() => toggle(s.key)}
                className="signal-checkbox"
              />
              <span className="signal-label">{s.label}</span>
              <span className={`signal-weight ${s.weight > 0 ? 'pos' : s.weight < 0 ? 'neg' : 'neu'}`}>
                {s.weight > 0 ? `+${s.weight}` : s.weight}
              </span>
            </label>
          )
        })}
      </div>
    </div>
  )
}
