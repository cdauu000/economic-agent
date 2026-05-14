import React from 'react'
import './ResultCard.css'

/* ── Score ring ────────────────────────────────────────────── */
function ScoreRing({ value, label, color }) {
  const r = 22
  const circ = 2 * Math.PI * r
  const fill = ((value ?? 0) / 100) * circ

  const colorMap = {
    amber: '#E3A140',
    teal:  '#2EA043',
    blue:  '#1F6FEB',
    coral: '#CF4A32',
  }
  const c = colorMap[color] || colorMap.amber

  return (
    <div className="score-ring-wrap">
      <svg width="56" height="56" viewBox="0 0 56 56">
        <circle cx="28" cy="28" r={r} fill="none" stroke="#21262D" strokeWidth="4" />
        <circle
          cx="28" cy="28" r={r}
          fill="none"
          stroke={c}
          strokeWidth="4"
          strokeDasharray={`${fill} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 28 28)"
        />
        <text x="28" y="32" textAnchor="middle" fontSize="12" fontWeight="600"
              fontFamily="'JetBrains Mono', monospace" fill={c}>
          {Math.round(value ?? 0)}
        </text>
      </svg>
      <span className="score-ring-label">{label}</span>
    </div>
  )
}

/* ── Signal badges ─────────────────────────────────────────── */
function SignalBadge({ sig }) {
  const pos = ['revenue_up','margin_stable','positive_news','policy_support','interest_rate_down','cost_down','profit_up']
  const neg = ['revenue_down','cost_up','negative_news','interest_rate_up','fx_risk','margin_down','debt_up']
  const cls = pos.includes(sig) ? 'badge badge-teal' : neg.includes(sig) ? 'badge badge-coral' : 'badge badge-muted'
  return <span className={cls}>{sig}</span>
}

/* ── Trend bar ─────────────────────────────────────────────── */
function TrendBar({ value, label }) {
  const pct = Math.min(100, Math.max(0, value ?? 0))
  const color = pct >= 65 ? '#2EA043' : pct >= 45 ? '#E3A140' : '#CF4A32'
  return (
    <div className="trend-bar-wrap">
      <div className="trend-bar-labels">
        <span>{label}</span>
        <span style={{ color, fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}>
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className="trend-bar-track">
        <div className="trend-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

/* ── Main ResultCard ───────────────────────────────────────── */
export default function ResultCard({ data }) {
  if (!data) return null

  const {
    company, sector,
    summary,
    score_total, score_financial, score_sentiment, score_macro,
    trend, confidence,
    signals, financial_signals, sentiment_signals, macro_signals,
    risks = [], opportunities = [],
  } = data

  const allSignals = signals || [
    ...(financial_signals || []),
    ...(sentiment_signals || []),
    ...(macro_signals || []),
  ]

  const trendColor =
    trend === 'positive' || trend === 'Tích cực'  ? 'var(--teal-text)'  :
    trend === 'negative' || trend === 'Tiêu cực'  ? 'var(--coral-text)' :
    'var(--amber-text)'

  return (
    <div className="result-card">
      {/* Header */}
      <div className="result-header">
        <div className="result-header-left">
          <span className="result-company">{company || 'N/A'}</span>
          {sector && <span className="badge badge-muted">{sector}</span>}
        </div>
        <span className="badge badge-amber" style={{ color: trendColor }}>
          {trend || 'N/A'}
        </span>
      </div>

      {/* Scores */}
      <div className="result-scores">
        <ScoreRing value={score_total}     label="Tổng"     color="amber" />
        <ScoreRing value={score_financial} label="Tài chính" color="teal" />
        <ScoreRing value={score_sentiment} label="Sentiment" color="amber" />
        <ScoreRing value={score_macro}     label="Vĩ mô"     color="blue" />
      </div>

      {/* Confidence */}
      {confidence != null && (
        <TrendBar value={confidence * 100} label="Confidence" />
      )}

      {/* Summary */}
      {summary && (
        <p className="result-summary">{summary}</p>
      )}

      {/* Signals */}
      {allSignals.length > 0 && (
        <div className="result-section">
          <span className="result-section-title">Tín hiệu phát hiện</span>
          <div className="result-signals">
            {allSignals.map((s, i) => <SignalBadge key={i} sig={s} />)}
          </div>
        </div>
      )}

      {/* Risks & Opportunities */}
      {(risks.length > 0 || opportunities.length > 0) && (
        <div className="result-risks-opps">
          {risks.length > 0 && (
            <div className="result-section">
              <span className="result-section-title" style={{ color: 'var(--coral-text)' }}>
                ⚠ Rủi ro
              </span>
              <ul className="result-list">
                {risks.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          {opportunities.length > 0 && (
            <div className="result-section">
              <span className="result-section-title" style={{ color: 'var(--teal-text)' }}>
                ✓ Cơ hội
              </span>
              <ul className="result-list">
                {opportunities.map((o, i) => <li key={i}>{o}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
