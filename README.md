# AI Chat System

基于 Python FastAPI + Vue 3 的前后端一体 AI Chat 系统，支持多渠道模型管理和用户聊天功能。

## 功能特性

- 🤖 多模型支持：管理多个 AI 模型渠道
- 💬 流式对话：实时显示 AI 回复
- 👥 用户系统：支持注册登录和游客模式
- 🔐 安全认证：JWT Token + bcrypt 密码加密
- 📊 统计面板：调用量、趋势、Token 消耗统计
- 🚦 双层限流：用户级 + 渠道级 RPM 限制
- 🚫 IP 黑名单：支持 CIDR 格式
- 📝 日志系统：查询、筛选、导出功能
- 🐳 Docker 部署：单端口部署，开箱即用

## 技术栈

**后端**
- FastAPI
- SQLAlchemy + SQLite
- Pydantic
- python-jose (JWT)
- passlib + bcrypt

**前端**
- Vue 3 + TypeScript
- Vite
- Tailwind CSS
- Pinia
- Axios

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆仓库
```bash
git clone <repository-url>
cd pyaichat
```

2. 配置环境变量
```bash
cp .env .env
# 编辑 .env 文件，设置管理员密码和密钥
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 用户页面: http://localhost:8000
- 管理员页面: http://localhost:8000/admin
- API 文档: http://localhost:8000/docs

### 本地开发

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

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| ADMIN_USERNAME | 管理员用户名 | admin |
| ADMIN_PASSWORD | 管理员密码 | - |
| SECRET_KEY | JWT 签名密钥 | - |
| ENCRYPTION_KEY | API Key 加密密钥 | - |
| DATABASE_PATH | 数据库路径 | ./data/chat.db |
| GUEST_RPM | 游客 RPM 限制 | 10 |
| USER_RPM | 用户 RPM 限制 | 60 |
| LOG_RETENTION_DAYS | 日志保留天数 | 90 |
| CORS_ORIGINS | CORS 允许的源 | * |
| APP_PORT | 应用端口 | 8000 |

## 使用说明

### 管理员操作

1. 登录管理员页面 (http://localhost:8000/admin)
2. 添加 AI 模型渠道（配置 Base URL、API Key、Model ID）
3. 配置系统设置（限流、日志保留）
4. 管理 IP 黑名单
5. 查看统计数据和日志

### 用户操作

1. 访问用户页面 (http://localhost:8000)
2. 选择可用模型
3. 开始对话（支持游客模式或登录后使用）

## API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/admin/login` - 管理员登录

### 聊天接口
- `GET /api/chat/models` - 获取可用模型
- `POST /api/chat/completions` - 聊天完成（流式）

### 管理员接口
- `GET /api/admin/channels` - 获取渠道列表
- `POST /api/admin/channels` - 创建渠道
- `PUT /api/admin/channels/{id}` - 更新渠道
- `DELETE /api/admin/channels/{id}` - 删除渠道
- `GET /api/admin/config` - 获取系统配置
- `PUT /api/admin/config` - 更新系统配置
- `GET /api/admin/blocked-ips` - 获取禁用 IP
- `POST /api/admin/blocked-ips` - 添加禁用 IP
- `DELETE /api/admin/blocked-ips/{id}` - 删除禁用 IP
- `GET /api/admin/logs` - 查询日志
- `GET /api/admin/logs/export` - 导出日志
- `GET /api/admin/stats` - 获取统计数据

## 项目结构

```
pyaichat/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── routers/     # API 路由
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   └── requirements.txt
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── api/        # API 客户端
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面视图
│   │   ├── stores/     # Pinia 状态
│   │   └── router/     # 路由配置
│   └── package.json
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
