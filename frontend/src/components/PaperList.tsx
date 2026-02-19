import { FileText } from 'lucide-react'
import type { Paper } from '../types'
import PaperCard from './PaperCard'

interface Props {
  papers: Paper[]
  onSelect: (paper: Paper) => void
}

export default function PaperList({ papers, onSelect }: Props) {
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
      </div>
      <div className="paper-cards">
        {papers.map((paper, index) => (
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
