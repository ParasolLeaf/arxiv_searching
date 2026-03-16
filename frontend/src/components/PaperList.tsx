import { useState, useMemo, useEffect } from 'react'
import { FileText } from 'lucide-react'
import type { Paper } from '../types'
import PaperCard from './PaperCard'

type SortKey =
  | 'relevance_desc'
  | 'relevance_asc'
  | 'date_desc'
  | 'date_asc'
  | 'accepted'

const ACCEPTED_RE = /\b(accepted|published)\b/i

function isAccepted(paper: Paper): boolean {
  if (!paper.comment) return false
  return ACCEPTED_RE.test(paper.comment)
}

function sortPapers(papers: Paper[], key: SortKey): Paper[] {
  const sorted = [...papers]
  switch (key) {
    case 'relevance_desc':
      sorted.sort((a, b) => (b.relevance_score ?? 0) - (a.relevance_score ?? 0))
      break
    case 'relevance_asc':
      sorted.sort((a, b) => (a.relevance_score ?? 0) - (b.relevance_score ?? 0))
      break
    case 'date_desc':
      sorted.sort((a, b) => b.published.localeCompare(a.published))
      break
    case 'date_asc':
      sorted.sort((a, b) => a.published.localeCompare(b.published))
      break
    case 'accepted': {
      sorted.sort((a, b) => {
        const aAcc = isAccepted(a) ? 1 : 0
        const bAcc = isAccepted(b) ? 1 : 0
        if (bAcc !== aAcc) return bAcc - aAcc
        return (b.relevance_score ?? 0) - (a.relevance_score ?? 0)
      })
      break
    }
  }
  return sorted
}

interface Props {
  papers: Paper[]
  onSelect: (paper: Paper) => void
}

export default function PaperList({ papers, onSelect }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('relevance_desc')

  // Reset sort when new papers arrive
  useEffect(() => {
    setSortKey('relevance_desc')
  }, [papers])

  const sortedPapers = useMemo(() => sortPapers(papers, sortKey), [papers, sortKey])

  if (papers.length === 0) {
    return (
      <div className="paper-list empty">
        <FileText size={48} strokeWidth={1} />
        <p>论文推荐结果将显示在这里</p>
        <p className="hint">在左侧对话框中描述你的研究兴趣</p>
      </div>
    )
  }

  return (
    <div className="paper-list">
      <div className="paper-list-header">
        <h2>推荐论文 ({papers.length})</h2>
        <select
          className="sort-select"
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value as SortKey)}
        >
          <option value="relevance_desc">相关性从高到低</option>
          <option value="relevance_asc">相关性从低到高</option>
          <option value="date_desc">时间从近到远</option>
          <option value="date_asc">时间从远到近</option>
          <option value="accepted">会议接收优先</option>
        </select>
      </div>
      <div className="paper-cards">
        {sortedPapers.map((paper, index) => (
          <PaperCard
            key={paper.arxiv_id}
            paper={paper}
            index={index + 1}
            onClick={() => onSelect(paper)}
          />
        ))}
      </div>
    </div>
  )
}
