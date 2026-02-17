# AI Chat 系统开发需求文档

## 项目概述
基于 Python FastAPI + SQLite 的前后端一体 AI Chat 系统，支持多渠道模型管理和用户聊天功能。

---

## 技术栈

**后端**
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose（JWT）
- passlib + bcrypt（密码加密）
- httpx（调用上游 API）

**前端**
- Vue 3 + Vite + TypeScript
- Vue Router + Pinia
- Tailwind CSS + shadcn-vue
- ECharts（图表）
- axios（HTTP 客户端）

**部署**
- Docker
- GitHub Actions
- SQLite 3

---

## 核心功能

### 1. 用户页面
- **访问方式**：`http://your-ip:8000/`
- **模型选择**：从当前开启的模型中选择
- **AI 聊天**：标准 OpenAI 格式对话
- **深度思考预览**：显示支持 reasoning 的模型（如 OpenAI o1）的思考过程
- **流式输出**：实时显示 AI 回复
- **用户认证**：
  - 支持未登录访问（游客模式）
  - 支持邮箱 + 密码注册登录
  - 密码最低 8 位，使用 bcrypt 加密存储
  - 无需邮箱验证
- **聊天历史**：不保存到数据库，仅在浏览器内存中，刷新后清空
- **UI 风格**：现代化简约主题，优秀交互体验和动画效果

### 2. 管理员页面
- **访问方式**：`http://your-ip:8000/admin`
- **认证方式**：用户名 + 密码 + JWT Token（有效期 24 小时）

#### 2.1 渠道管理
- 添加/编辑/删除渠道
- 配置项：
  - 渠道名称
  - Base URL
  - API Key
  - Model ID
  - RPM 限制
  - 开启/禁用状态

#### 2.2 系统设置
- 未登录用户 RPM 限制（默认 10/分钟）
- 已登录用户 RPM 限制（默认 60/分钟）
- 日志保留天数（默认 90 天）

#### 2.3 IP 管理
- 禁用 IP 列表（支持 IP 段，如 192.168.1.0/24）
- 仅针对用户页面，管理员页面不受影响
- 自动记录被禁 IP 的访问尝试

#### 2.4 日志系统
- **记录内容**：
  - 调用 IP（必须）
  - 用户名/邮箱（如果已登录）
  - 调用模型
  - 调用渠道
  - 调用时间
  - 提问 tokens 数量（估算）
  - 回答 tokens 数量（估算）
- **不记录**：用户问题内容、AI 回答内容
- **筛选功能**：按时间范围、用户、IP、模型筛选
- **导出功能**：支持 CSV 格式导出

#### 2.5 统计面板
- 今日/本周/本月调用量
- 各模型使用占比（饼图）
- 调用趋势图（折线图，最近 7 天）
- Token 消耗统计（提问 + 回答）
- 活跃用户数量

### 3. 安全性
- 密码加密：bcrypt，最低 8 位
- JWT Token：管理员和用户登录认证
- 防止 API Key 泄露：用户无法直接访问上游 API

---

## 限流策略

### 双层限流机制

**1. 渠道级限流**
- 针对单个上游渠道的 RPM 限制
- 防止超出上游 API 配额

**2. 用户级限流**
- 未登录用户：按 IP 地址限流（管理员可配置）
- 已登录用户：用户统一限流（管理员可配置）

### 错误提示区分

**用户/IP 达到限制**（用户页面要弹窗显示）
```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "您超过当前使用限制，请稍后再试",
    "retry_after": 60
  }
}
```

**上游渠道错误**（用户页面要弹窗显示）
```json
{
  "error": {
    "type": "upstream_error",
    "message": "上游渠道暂时不可用，请稍后再试"
  }
}
```

---

## 数据库设计

### 表结构

**users（用户表）**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**channels（渠道表）**
```sql
CREATE TABLE channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT NOT NULL,
    model_id TEXT NOT NULL,
    rpm_limit INTEGER DEFAULT 60,
    is_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**system_config（系统配置表）**
```sql
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**blocked_ips（禁用 IP 表）**
```sql
CREATE TABLE blocked_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**chat_logs（聊天日志表）**
```sql
CREATE TABLE chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    ip_address TEXT NOT NULL,
    channel_id INTEGER,
    model_id TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 索引设计
```sql
CREATE INDEX idx_chat_logs_created_at ON chat_logs(created_at);
CREATE INDEX idx_chat_logs_user_id ON chat_logs(user_id);
CREATE INDEX idx_chat_logs_ip_address ON chat_logs(ip_address);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_blocked_ips_ip_address ON blocked_ips(ip_address);
```

---

## 项目结构

```
pyaichat/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── channel.py
│   │   │   ├── config.py
│   │   │   ├── blocked_ip.py
│   │   │   └── chat_log.py
│   │   ├── schemas/             # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── channel.py
│   │   │   ├── chat.py
│   │   │   └── admin.py
│   │   ├── routers/             # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证接口（/api/auth/*）
│   │   │   ├── chat.py          # 聊天接口（/api/chat/*）
│   │   │   └── admin.py         # 管理员接口（/api/admin/*）
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证服务
│   │   │   ├── channel.py       # 渠道管理
│   │   │   ├── chat.py          # 聊天服务
│   │   │   └── rate_limit.py   # 限流服务
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       ├── security.py      # 加密解密
│   │       └── helpers.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Vue 组件
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInput.vue
│   │   │   │   ├── ChatMessage.vue
│   │   │   │   └── ThinkingPanel.vue
│   │   │   └── Admin/
│   │   │       ├── ChannelForm.vue
│   │   │       ├── LogTable.vue
│   │   │       └── StatsChart.vue
│   │   ├── views/               # 页面视图
│   │   │   ├── Chat.vue         # 用户聊天页面（/）
│   │   │   ├── Login.vue        # 登录页面（/login）
│   │   │   ├── Register.vue     # 注册页面（/register）
│   │   │   └── Admin/           # 管理员页面（/admin/*）
│   │   │       ├── Dashboard.vue
│   │   │       ├── Channels.vue
│   │   │       ├── Logs.vue
│   │   │       └── Settings.vue
│   │   ├── router/              # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/              # Pinia 状态管理
│   │   │   ├── user.ts
│   │   │   ├── chat.ts
│   │   │   └── admin.ts
│   │   ├── api/                 # API 请求
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   └── admin.ts
│   │   ├── types/               # TypeScript 类型
│   │   │   └── index.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── docker-build.yml     # GitHub Actions 配置
├── .env.example
└── README.md
```

---

## 部署方案

### 单端口部署架构
- FastAPI 服务监听单个端口（默认 8000）
- 前端构建后的静态文件由 FastAPI 提供服务

### 路由规则
- `http://your-ip:8000/` → 用户聊天页面
- `http://your-ip:8000/login` → 用户登录页面
- `http://your-ip:8000/register` → 用户注册页面
- `http://your-ip:8000/admin` → 管理员页面
- `http://your-ip:8000/api/*` → 后端 API 接口
- `http://your-ip:8000/docs` → API 文档（Swagger UI）

### 环境变量配置
```bash
# 必需配置
ADMIN_USERNAME=admin              # 初始管理员用户名
ADMIN_PASSWORD=change_me          # 初始管理员密码
SECRET_KEY=random_secret_key      # JWT 签名密钥
ENCRYPTION_KEY=random_encrypt_key # API Key 加密密钥

# 可选配置
DATABASE_PATH=/app/data/chat.db   # 数据库路径
LOG_RETENTION_DAYS=90             # 日志保留天数
GUEST_RPM=10                      # 未登录用户 RPM 限制
USER_RPM=60                       # 已登录用户 RPM 限制
CORS_ORIGINS=*                    # CORS 允许的源
APP_PORT=8000                     # 应用端口
```

### Docker 部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: your-registry/pyaichat:latest
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your_secure_password
      - SECRET_KEY=your_secret_key
      - ENCRYPTION_KEY=your_encryption_key
    restart: unless-stopped
```

### GitHub Actions 自动构建
- 支持 linux/amd64 和 linux/arm64 多架构
- 推送到 Docker Hub 和 GitHub Container Registry
- 自动打标签（latest, version）

---

## API 接口设计

### 认证接口（/api/auth）

**用户注册**
```
POST /api/auth/register
Body: { "email": "user@example.com", "password": "password123" }
Response: { "message": "注册成功" }
```

**用户登录**
```
POST /api/auth/login
Body: { "email": "user@example.com", "password": "password123" }
Response: { "access_token": "jwt_token", "token_type": "bearer" }
```

**管理员登录**
```
POST /api/auth/admin/login
Body: { "username": "admin", "password": "admin_password" }
Response: { "access_token": "jwt_token", "token_type": "bearer" }
```

### 聊天接口（/api/chat）

**获取可用模型列表**
```
GET /api/chat/models
Response: [
  { "id": "gpt-4", "name": "GPT-4" },
  { "id": "claude-3", "name": "Claude 3" }
]
```

**发送聊天消息（流式）**
```
POST /api/chat/completions
Headers: { "Authorization": "Bearer jwt_token" } (可选)
Body: {
  "model": "gpt-4",
  "messages": [
    { "role": "user", "content": "Hello" }
  ],
  "stream": true
}
Response: Server-Sent Events (SSE)
```

### 管理员接口（/api/admin）

**渠道管理**
```
GET /api/admin/channels              # 获取渠道列表
POST /api/admin/channels             # 创建渠道
PUT /api/admin/channels/{id}         # 更新渠道
DELETE /api/admin/channels/{id}      # 删除渠道
```

**系统配置**
```
GET /api/admin/config                # 获取系统配置
PUT /api/admin/config                # 更新系统配置
```

**IP 管理**
```
GET /api/admin/blocked-ips           # 获取禁用 IP 列表
POST /api/admin/blocked-ips          # 添加禁用 IP
DELETE /api/admin/blocked-ips/{id}   # 删除禁用 IP
```

**日志查询**
```
GET /api/admin/logs                  # 获取日志列表（支持筛选）
GET /api/admin/logs/export           # 导出日志（CSV）
```

**统计数据**
```
GET /api/admin/stats                 # 获取统计数据
```

---

## 开发流程

### 1. 开发环境搭建

**后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

### 2. 前端代理配置
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### 3. 构建部署
```bash
# 前端构建
cd frontend
npm run build

# Docker 构建
docker build -t pyaichat:latest .

# 运行
docker-compose up -d
```

---

## 下一步

1. 创建详细的 API 接口文档
2. 编写数据库初始化脚本
3. 实现后端核心功能
4. 实现前端页面和组件
5. 编写 Dockerfile 和 GitHub Actions 配置
6. 测试和优化
