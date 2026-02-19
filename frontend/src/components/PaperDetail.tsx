import { X, Download, ExternalLink } from 'lucide-react'
import type { Paper } from '../types'
import { useState } from 'react'
import { downloadPaper } from '../services/api'

interface Props {
  paper: Paper
  onClose: () => void
}

export default function PaperDetail({ paper, onClose }: Props) {
  const [downloading, setDownloading] = useState(false)

  const handleDownload = async () => {
    setDownloading(true)
    try {
      await downloadPaper(paper)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={20} />
        </button>

        <h2>{paper.title}</h2>

        <div className="detail-meta">
          <p><strong>作者：</strong>{paper.authors.join(', ')}</p>
          <p><strong>发表日期：</strong>{paper.published}</p>
          <p><strong>分类：</strong>{paper.categories.join(', ')}</p>
          <p><strong>arXiv ID：</strong>{paper.arxiv_id}</p>
          {paper.relevance_score !== null && (
            <p><strong>相关性评分：</strong>{paper.relevance_score.toFixed(1)} / 10</p>
          )}
          {paper.relevance_reason && (
            <p><strong>推荐理由：</strong>{paper.relevance_reason}</p>
          )}
        </div>

        <div className="detail-abstract">
          <h3>摘要</h3>
          <p>{paper.abstract}</p>
        </div>

        <div className="detail-actions">
          <button className="btn-primary" onClick={handleDownload} disabled={downloading}>
            <Download size={16} />
            {downloading ? '下载中...' : '下载 PDF'}
          </button>
          <a
            className="btn-secondary"
            href={paper.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            <ExternalLink size={16} />
            在 arXiv 中查看
          </a>
        </div>
      </div>
    </div>
  )
}
