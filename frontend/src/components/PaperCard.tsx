import { useState } from 'react'
import { Download, ExternalLink, CheckCircle, Loader2 } from 'lucide-react'
import type { Paper } from '../types'
import { downloadPaper } from '../services/api'

interface Props {
  paper: Paper
  index: number
  onClick: () => void
}

export default function PaperCard({ paper, index, onClick }: Props) {
  const [downloading, setDownloading] = useState(false)
  const [downloaded, setDownloaded] = useState(false)
  const [downloadMsg, setDownloadMsg] = useState('')

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setDownloading(true)
    setDownloadMsg('')
    try {
      const result = await downloadPaper(paper)
      setDownloaded(result.success)
      setDownloadMsg(result.message)
    } catch (err: any) {
      setDownloadMsg('下载失败')
    } finally {
      setDownloading(false)
    }
  }

  const scoreColor =
    (paper.relevance_score ?? 0) >= 7
      ? '#10b981'
      : (paper.relevance_score ?? 0) >= 4
        ? '#f59e0b'
        : '#6b7280'

  return (
    <div className="paper-card" onClick={onClick}>
      <div className="paper-card-header">
        <span className="paper-index">#{index}</span>
        {paper.relevance_score !== null && (
          <span className="paper-score" style={{ color: scoreColor }}>
            {paper.relevance_score.toFixed(1)}
          </span>
        )}
      </div>

      <h3 className="paper-title">{paper.title}</h3>

      <p className="paper-authors">
        {paper.authors.slice(0, 3).join(', ')}
        {paper.authors.length > 3 && ` 等 ${paper.authors.length} 人`}
      </p>

      <div className="paper-meta">
        <span className="paper-date">{paper.published}</span>
        {paper.categories.slice(0, 3).map((cat) => (
          <span key={cat} className="paper-category">{cat}</span>
        ))}
      </div>

      {paper.relevance_reason && (
        <p className="paper-reason">{paper.relevance_reason}</p>
      )}

      <p className="paper-abstract">
        {paper.abstract.length > 200
          ? paper.abstract.slice(0, 200) + '...'
          : paper.abstract}
      </p>

      <div className="paper-actions">
        <button
          className={`btn-download ${downloaded ? 'downloaded' : ''}`}
          onClick={handleDownload}
          disabled={downloading}
        >
          {downloading ? (
            <Loader2 size={14} className="spin" />
          ) : downloaded ? (
            <CheckCircle size={14} />
          ) : (
            <Download size={14} />
          )}
          {downloading ? '下载中...' : downloaded ? '已下载' : '下载PDF'}
        </button>
        <a
          className="btn-link"
          href={paper.pdf_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
        >
          <ExternalLink size={14} />
          arXiv
        </a>
      </div>
      {downloadMsg && <p className="download-msg">{downloadMsg}</p>}
    </div>
  )
}
