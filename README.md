# Chat Service

多轮对话服务，Azure OpenAI GPT-4o 驱动，SSE 流式输出。运行在端口 **8003**。

---

## Requirements

- Python 3.11+
- Poetry
- MySQL 8.0+（共用 `beryl` 数据库）
- auth_service 已启动（端口 8002）

---

## Setup

```bash
poetry install
cp .env.example .env
# 编辑 .env，填写 Azure OpenAI 密钥和端点
poetry run alembic upgrade head
```

---

## Run

**Development**

```bash
poetry run uvicorn app.main:app --reload --port ${PORT:-8003}
```

**Stop**

```bash
# 前台运行直接 Ctrl+C
# 后台运行：
lsof -ti :8003 | xargs kill
```

**Production (PM2)**

```bash
pm2 start ecosystem.config.js
pm2 logs chat_service
pm2 stop chat_service
```

---

## API Docs

- Swagger: `http://localhost:8003/docs`
- Health: `http://localhost:8003/health`
