import axios from 'axios'
import type { ChatRequest, ChatResponse, Paper, DownloadResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // LLM calls can be slow
})

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/chat', request)
  return data
}

export async function downloadPaper(paper: Paper): Promise<DownloadResponse> {
  const { data } = await api.post<DownloadResponse>('/papers/download', paper)
  return data
}

export async function getDownloads(): Promise<{ filename: string; file_path: string; file_size: number }[]> {
  const { data } = await api.get('/downloads')
  return data
}
