import { useState } from 'react'
import type { ChatMessage, Paper } from './types'
import { sendChat } from './services/api'
import ChatPanel from './components/ChatPanel'
import PaperList from './components/PaperList'
import PaperDetail from './components/PaperDetail'

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [papers, setPapers] = useState<Paper[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null)

  const handleSendMessage = async (content: string) => {
    const userMsg: ChatMessage = { role: 'user', content }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setLoading(true)

    try {
      const response = await sendChat({
        message: content,
        history: messages,
        current_papers: papers,
      })

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.reply,
      }
      setMessages([...newMessages, assistantMsg])

      if (response.papers.length > 0) {
        setPapers(response.papers)
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `请求出错: ${err.response?.data?.detail || err.message}`,
      }
      setMessages([...newMessages, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>arXiv Paper Recommender</h1>
        <span className="subtitle">对话式论文搜索与推荐</span>
      </header>
      <div className="app-body">
        <ChatPanel
          messages={messages}
          loading={loading}
          onSend={handleSendMessage}
        />
        <PaperList
          papers={papers}
          onSelect={setSelectedPaper}
        />
      </div>
      {selectedPaper && (
        <PaperDetail
          paper={selectedPaper}
          onClose={() => setSelectedPaper(null)}
        />
      )}
    </div>
  )
}
