export interface Paper {
  arxiv_id: string
  title: string
  authors: string[]
  abstract: string
  published: string
  categories: string[]
  pdf_url: string
  relevance_score: number | null
  relevance_reason: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  history: ChatMessage[]
  current_papers: Paper[]
}

export interface ChatResponse {
  reply: string
  papers: Paper[]
  search_query: string | null
}

export interface DownloadResponse {
  success: boolean
  message: string
  file_path: string | null
}
