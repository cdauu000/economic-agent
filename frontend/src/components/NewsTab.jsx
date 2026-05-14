import React, { useState, useEffect } from 'react'
import './NewsTab.css'

/* ── Mock dữ liệu — thay bằng API thực khi có endpoint /news ── */
const MOCK_NEWS = [
  {
    id: 1, source: 'CafeF', sentiment: 'positive', time: '14:32',
    company: 'Vinamilk', sector: 'Tiêu dùng',
    title: 'Vinamilk ghi nhận doanh thu xuất khẩu tăng 15% trong quý 1',
    body: 'Công ty sữa hàng đầu báo cáo tăng trưởng mạnh ở thị trường ASEAN nhờ chiến lược mở rộng thương hiệu và cải thiện kênh phân phối hiện đại.',
    url: '#',
  },
  {
    id: 2, source: 'VnEconomy', sentiment: 'negative', time: '12:15',
    company: 'Ngành sản xuất', sector: 'Nguyên liệu',
    title: 'Giá nguyên liệu đầu vào tiếp tục leo thang, áp lực lên biên lợi nhuận',
    body: 'Giá sữa bột nhập khẩu tăng 8–12% do biến động từ thị trường châu Âu, tác động đến nhiều doanh nghiệp ngành tiêu dùng và chế biến thực phẩm.',
    url: '#',
  },
  {
    id: 3, source: 'Bloomberg VN', sentiment: 'positive', time: '10:44',
    company: 'Vĩ mô', sector: 'Tài chính',
    title: 'NHNN giữ nguyên lãi suất điều hành, hỗ trợ tăng trưởng tín dụng Q2',
    body: 'Ngân hàng Nhà nước tiếp tục duy trì chính sách tiền tệ nới lỏng có kiểm soát, tạo điều kiện cho doanh nghiệp tiếp cận vốn với chi phí hợp lý.',
    url: '#',
  },
  {
    id: 4, source: 'Twitter/X', sentiment: 'positive', time: '09:10',
    company: 'Vinamilk', sector: 'Tiêu dùng',
    title: '#VNM trending: Nhà đầu tư kỳ vọng cổ tức Q1 cao hơn năm ngoái',
    body: 'Sentiment mạng xã hội chủ yếu tích cực với mã VNM sau kết quả kinh doanh sơ bộ. Nhiều analyst nâng target price lên 85.000–90.000 VND.',
    url: '#',
  },
  {
    id: 5, source: 'VnDirect', sentiment: 'neutral', time: '08:30',
    company: 'HPG', sector: 'Thép',
    title: 'Hòa Phát: Sản lượng thép xây dựng Q1 tăng nhẹ 3%, chờ tín hiệu BĐS',
    body: 'Kết quả kinh doanh Q1 của Hòa Phát khả quan nhưng thị trường đang chờ chính sách gỡ vướng bất động sản để kích thích nhu cầu thép nội địa.',
    url: '#',
  },
  {
    id: 6, source: 'Reuters', sentiment: 'negative', time: '07:55',
    company: 'Vĩ mô', sector: 'Toàn cầu',
    title: 'USD mạnh lên trước thềm Fed họp — đồng tiền EM chịu áp lực',
    body: 'Đồng USD tăng 0.4% trong phiên châu Á, tạo áp lực lên tiền tệ thị trường mới nổi. VND có thể chịu áp lực mất giá nhẹ trong ngắn hạn.',
    url: '#',
  },
]

const SENT_CFG = {
  positive: { label: 'Tích cực', cls: 'badge-teal' },
  negative: { label: 'Rủi ro',   cls: 'badge-coral' },
  neutral:  { label: 'Trung tính', cls: 'badge-muted' },
}

export default function NewsTab() {
  const [filter, setFilter]   = useState('all')
  const [search, setSearch]   = useState('')
  const [news, setNews]       = useState(MOCK_NEWS)
  const [refreshing, setRefreshing] = useState(false)

  /* TODO: khi backend có /news endpoint, fetch thay thế mock */
  async function refresh() {
    setRefreshing(true)
    await new Promise(r => setTimeout(r, 900))
    setNews([...MOCK_NEWS].sort(() => Math.random() - .5))
    setRefreshing(false)
  }

  const filtered = news.filter(n => {
    if (filter !== 'all' && n.sentiment !== filter) return false
    if (search && !n.title.toLowerCase().includes(search.toLowerCase()) &&
        !n.company.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const counts = {
    positive: news.filter(n => n.sentiment === 'positive').length,
    negative: news.filter(n => n.sentiment === 'negative').length,
  }

  return (
    <div className="news-tab">
      {/* Toolbar */}
      <div className="news-toolbar">
        <input
          className="form-input news-search"
          placeholder="Tìm kiếm tin tức, công ty..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className={`btn btn-ghost news-refresh ${refreshing ? 'spinning' : ''}`} onClick={refresh} title="Làm mới">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="1 4 1 10 7 10"/>
            <path d="M3.51 15a9 9 0 1 0 .49-4"/>
          </svg>
        </button>
      </div>

      {/* Sentiment summary */}
      <div className="news-summary">
        {['all','positive','negative','neutral'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all'      ? `Tất cả (${news.length})`      :
             f === 'positive' ? `✓ Tích cực (${counts.positive})` :
             f === 'negative' ? `⚠ Rủi ro (${counts.negative})`   : 'Trung tính'}
          </button>
        ))}
      </div>

      {/* Feed */}
      <div className="news-feed">
        {filtered.length === 0 ? (
          <div className="news-empty">Không có tin tức phù hợp</div>
        ) : filtered.map(item => (
          <div key={item.id} className={`news-card news-${item.sentiment}`}>
            <div className="news-meta">
              <span className="badge badge-blue">{item.source}</span>
              <span className={`badge ${SENT_CFG[item.sentiment].cls}`}>
                {SENT_CFG[item.sentiment].label}
              </span>
              <span className="badge badge-muted">{item.company}</span>
              <span className="news-time mono">{item.time}</span>
            </div>
            <div className="news-title">{item.title}</div>
            <div className="news-body">{item.body}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
