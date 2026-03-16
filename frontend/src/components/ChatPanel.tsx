import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Search, FileText } from 'lucide-react'
import type { ChatMessage } from '../types'
import MessageBubble from './MessageBubble'

interface Props {
  messages: ChatMessage[]
  loading: boolean
  searchMode: 'keyword' | 'abstract'
  onSearchModeChange: (mode: 'keyword' | 'abstract') => void
  onSend: (content: string) => void
}

export default function ChatPanel({ messages, loading, searchMode, onSearchModeChange, onSend }: Props) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || loading) return
    onSend(trimmed)
    setInput('')
  }

  const placeholder = searchMode === 'abstract'
    ? '粘贴论文摘要或详细描述你的研究方向...'
    : '描述你的研究兴趣，或输入细化条件...'

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h2>欢迎使用论文推荐助手</h2>
            <p>描述你的研究兴趣，我会帮你从 arXiv 上找到最相关的论文。</p>
            <div className="chat-examples">
              <p className="examples-title">试试这样说：</p>
              {searchMode === 'keyword' ? (
                <>
                  <button onClick={() => onSend('推荐一些关于大语言模型安全性的最新论文')}>
                    推荐一些关于大语言模型安全性的最新论文
                  </button>
                  <button onClick={() => onSend('我想找用强化学习做机器人控制的论文')}>
                    我想找用强化学习做机器人控制的论文
                  </button>
                  <button onClick={() => onSend('有哪些关于图神经网络在药物发现中应用的工作')}>
                    有哪些关于图神经网络在药物发现中应用的工作
                  </button>
                </>
              ) : (
                <>
                  <button onClick={() => onSend('我在研究如何用大语言模型来自动生成单元测试，特别关注基于代码上下文理解的测试用例生成方法，以及如何评估生成测试的质量和覆盖率')}>
                    描述研究方向：LLM自动生成单元测试
                  </button>
                  <button onClick={() => onSend('We propose a novel framework that combines graph neural networks with attention mechanisms for molecular property prediction. Our approach leverages both local atomic interactions and global molecular topology to achieve state-of-the-art performance on benchmark datasets.')}>
                    粘贴论文摘要：GNN分子性质预测
                  </button>
                </>
              )}
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="message assistant loading-msg">
            <Loader2 className="spin" size={18} />
            <span>{searchMode === 'abstract' ? '正在多策略搜索和分析论文...' : '正在搜索和分析论文...'}</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-area">
        <div className="search-mode-toggle">
          <button
            className={`mode-btn ${searchMode === 'keyword' ? 'active' : ''}`}
            onClick={() => onSearchModeChange('keyword')}
            disabled={loading}
          >
            <Search size={14} />
            关键词搜索
          </button>
          <button
            className={`mode-btn ${searchMode === 'abstract' ? 'active' : ''}`}
            onClick={() => onSearchModeChange('abstract')}
            disabled={loading}
          >
            <FileText size={14} />
            精量推荐
          </button>
        </div>
        <form className="chat-input" onSubmit={handleSubmit}>
          {searchMode === 'abstract' ? (
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              disabled={loading}
              rows={3}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
          ) : (
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              disabled={loading}
            />
          )}
          <button type="submit" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  )
}
