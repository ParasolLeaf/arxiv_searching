import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import type { ChatMessage } from '../types'
import MessageBubble from './MessageBubble'

interface Props {
  messages: ChatMessage[]
  loading: boolean
  onSend: (content: string) => void
}

export default function ChatPanel({ messages, loading, onSend }: Props) {
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

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h2>欢迎使用论文推荐助手</h2>
            <p>描述你的研究兴趣，我会帮你从 arXiv 上找到最相关的论文。</p>
            <div className="chat-examples">
              <p className="examples-title">试试这样说：</p>
              <button onClick={() => onSend('推荐一些关于大语言模型安全性的最新论文')}>
                推荐一些关于大语言模型安全性的最新论文
              </button>
              <button onClick={() => onSend('我想找用强化学习做机器人控制的论文')}>
                我想找用强化学习做机器人控制的论文
              </button>
              <button onClick={() => onSend('有哪些关于图神经网络在药物发现中应用的工作')}>
                有哪些关于图神经网络在药物发现中应用的工作
              </button>
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="message assistant loading-msg">
            <Loader2 className="spin" size={18} />
            <span>正在搜索和分析论文...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="描述你的研究兴趣，或输入细化条件..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  )
}
