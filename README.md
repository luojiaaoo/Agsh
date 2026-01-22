# Agsh

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## Overview

Agsh 是 [agno-agi/agent-ui](https://github.com/agno-agi/agent-ui) 的轻量级替代方案，可以实现Agno前端的私有化部署。

内置后端案例提供了智能化的深度研究与报告生成能力。通过强大的 AI Agent 编排技术，Agsh 能够自动规划研究任务、从多源收集信息（Web 搜索 + Arxiv 论文检索），并生成多种格式的专业报告（HTML、Markdown、PPT）。

## Features

- **[🏗️] 前后端分离**：Dash 前端 + FastAPI 后端架构
- **[🤖] Agno 框架**：强大的 AI Agent 编排能力
- **[🔐] JWT 认证**：安全的用户认证机制
- **[📡] SSE 消息队列**：实时通信支持
- **[🎨] Feffery 组件**：现代化的 UI 组件库

## Tech Stack

| 类别 | 技术 |
|------|------|
| **后端** | Agno AgentOS |
| **前端** | Dash、Feffery Antd Components |
| **LLM** | SiliconFlow (DeepSeek-V3.2) |
| **工具** | DuckDuckGo 搜索、Arxiv API |
| **开发** | Python 3.12+、UV 包管理 |

## Quick Start

### 前置要求

- Python 3.12 或更高版本
- [UV](https://github.com/astral-sh/uv) 包管理器

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/agsh.git
cd agsh

# 2. 安装 UV（如果尚未安装）
pip install uv

# 3. 安装依赖
uv sync

# 4. 配置 API Key
# 编辑 agno_backend/app.py，替换第 21 行的 API Key：
# api_key='sk-xxxx'  # 替换为你的 SiliconFlow API Key

# 5. 启动后端（端口 7777）
cd agno_backend
python app.py

# 6. 启动前端（端口 8000，新终端）
cd dash_frontend
python app.py

# 7. 访问应用
# 打开浏览器访问 http://127.0.0.1:8000
```

## Configuration

应用配置文件位于项目根目录的 `config.toml`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `app_title` | 应用名称 | `'DeepLoki'` |
| `launch_mode` | 运行模式（dev/prod） | `"dev"` |
| `log_filepath` | 日志保存路径 | `"../logs/frontend.log"` |
| `log_level` | 日志级别 | `"DEBUG"` |
| `host` | 前端服务地址 | `'127.0.0.1'` |
| `port` | 前端服务端口 | `8000` |
| `agno_agentos_url` | 后端 AgentOS 地址 | `"http://localhost:7777"` |
| `agno_id` | Agno 工作流 ID | `"deep-research-pipeline"` |
| `agno_type` | Agno 类型 | `'workflows'` |
| `agno_agentos_jwt_secret` | JWT 密钥（生产环境需修改） | 默认密钥 |

## Project Structure

```
agsh/
├── agno_backend/              # 后端服务
│   ├── app.py                # AgentOS 入口
│   ├── prompt.py             # Agent 提示词
│   ├── middleware.py         # JWT 中间件
│   └── utils.py              # 工具函数
├── dash_frontend/             # 前端服务
│   ├── app.py                # Dash 应用入口
│   ├── configure.py          # 配置读取
│   ├── server.py             # Flask 服务器配置
│   ├── components/           # UI 组件
│   │   ├── chat_header.py    # 聊天头部组件
│   │   ├── chat_area.py      # 聊天区域组件
│   │   └── chat_input.py     # 输入组件
│   ├── blueprint/            # API 路由
│   │   └── chat_api.py       # 暴露组件json的接口i
│   └── utils/                # 工具
├── downloads/                 # 报告下载目录
├── logs/                      # 日志目录
├── config.toml               # 应用配置
└── README.md                 # Python 项目配置
```

## Usage

1. **输入研究主题**：在聊天界面输入你想要研究的主题
2. **自动研究执行**：系统自动规划和执行研究任务
3. **实时进度查看**：通过流式输出实时查看研究进度
4. **下载报告**：研究完成后，下载生成的 HTML、Markdown 或 PPT 报告

## Development

### 依赖管理

使用 [UV](https://github.com/astral-sh/uv) 管理项目依赖：

```bash
# 添加新依赖
uv add package_name

# 更新依赖
uv sync
```

## Architecture

Agsh 采用前后端分离架构：

1. **后端（agno_backend）**：
   - 基于 Agno Framework 的 AgentOS
   - 包含任务规划、深度研究、报告生成等多个 Agent
   - 提供 RESTful API 和 JWT 认证

2. **前端（dash_frontend）**：
   - 基于 Dash 的 Web 应用
   - 使用 Feffery Antd Components 构建现代化 UI
   - 通过 SSE 与后端进行实时通信

## Acknowledgments

- [Agno Framework](https://github.com/agno-agi/agno) - 强大的 AI Agent 编排框架
- [agno-agi/agent-ui](https://github.com/agno-agi/agent-ui) - 原始项目灵感来源
- [Dash](https://dash.plotly.com/) - Python Web 应用框架
- [Feffery Antd Components](https://github.com/CNFeffery/feffery-antd-components) - UI 组件库
