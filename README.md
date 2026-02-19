# arXiv Paper Recommender

对话式论文搜索与推荐系统 — 通过自然语言描述研究兴趣，从 arXiv 搜索并推荐最相关的论文，支持多轮对话细化筛选，一键下载 PDF。

## 项目结构

```
paperreading/
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 入口，CORS 配置
│   ├── .env                        # 环境变量（需填入 API Key）
│   ├── .env.example                # 环境变量模板
│   ├── requirements.txt            # Python 依赖
│   ├── models/
│   │   └── schemas.py              # Pydantic 数据模型
│   ├── routers/
│   │   ├── chat.py                 # /api/chat 对话推荐端点
│   │   └── papers.py               # /api/papers/download 下载端点
│   ├── services/
│   │   ├── arxiv_service.py        # arXiv 搜索封装
│   │   ├── llm_service.py          # OpenAI 意图解析 + 论文排序 + 详情解读
│   │   └── download_service.py     # PDF 下载管理
│   └── downloads/                  # 下载的 PDF 存储目录
└── frontend/                       # React + Vite + TypeScript 前端
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx                 # 主布局：左侧聊天 + 右侧论文列表
        ├── components/
        │   ├── ChatPanel.tsx       # 聊天面板
        │   ├── MessageBubble.tsx   # 消息气泡
        │   ├── PaperList.tsx       # 论文列表
        │   ├── PaperCard.tsx       # 论文卡片（含下载按钮）
        │   └── PaperDetail.tsx     # 论文详情弹窗
        ├── services/
        │   └── api.ts              # 后端 API 调用封装
        ├── types/
        │   └── index.ts            # TypeScript 类型定义
        └── styles/
            └── index.css           # 全局样式
```

## 环境要求

- Python 3.12（推荐通过 conda 管理）
- Node.js 18+
- OpenAI API Key

## 启动步骤

### 1. 配置 API Key

编辑 `backend/.env`，填入你的 OpenAI API Key：

```env
OPENAI_API_KEY=sk-your-actual-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

如果使用代理或第三方兼容服务，修改 `OPENAI_BASE_URL` 即可。

### 2. 启动后端

```bash
conda activate paperreading
cd backend
uvicorn main:app --reload --port 8000
```

启动后可访问 `http://localhost:8000/docs` 查看 API 文档。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 使用

浏览器打开 `http://localhost:5173`。

## 功能说明

| 功能 | 说明 |
|------|------|
| 自然语言搜索 | 在左侧聊天框输入研究兴趣描述，如「推荐关于大语言模型安全性的论文」 |
| 智能排序 | 右侧展示按相关性评分排序的论文列表，每篇附有推荐理由 |
| 多轮对话细化 | 继续输入如「只看2024年之后的」「排除综述类」来筛选结果 |
| 论文详情 | 点击论文卡片查看完整摘要、作者、分类等信息 |
| 论文解读 | 在对话中输入「第3篇论文讲了什么」获取 LLM 生成的详细解读 |
| PDF 下载 | 点击下载按钮，PDF 保存到 `backend/downloads/` 目录 |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 核心对话端点，接收消息+历史，返回推荐论文 |
| POST | `/api/papers/download` | 下载论文 PDF 到本地 |
| GET  | `/api/downloads` | 列出已下载的论文 |
| GET  | `/api/health` | 健康检查 |

## 技术栈

- **前端**: React 18 + Vite + TypeScript + Axios + Lucide Icons
- **后端**: Python FastAPI + Uvicorn
- **LLM**: OpenAI API (gpt-4o-mini)
- **论文源**: arXiv API（`arxiv` Python 库）
