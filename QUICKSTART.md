# AI Chat 系统快速开始指南

## 开发完成情况

✅ 后端开发完成 (100%)
✅ 前端开发完成 (100%)
✅ 部署配置完成 (100%)

## 项目结构

```
pyaichat/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── routers/     # API 路由
│   │   ├── services/    # 业务逻辑
│   │   ├── utils/       # 工具函数
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库连接
│   │   └── main.py      # 应用入口
│   └── requirements.txt
├── frontend/            # Vue 3 前端
│   ├── src/
│   │   ├── api/        # API 客户端
│   │   ├── views/      # 页面视图
│   │   ├── stores/     # Pinia 状态
│   │   ├── router/     # 路由配置
│   │   └── main.ts     # 应用入口
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── PROGRESS.md
```

## 快速启动

### 方式一：Docker Compose（推荐）

1. 配置环境变量
```bash
cp .env .env
# 编辑 .env 文件，修改以下必需配置：
# - ADMIN_PASSWORD: 管理员密码
# - SECRET_KEY: JWT 签名密钥（随机字符串）
# - ENCRYPTION_KEY: API Key 加密密钥（随机字符串）
```

2. 启动服务
```bash
docker-compose up -d
```

3. 访问应用
- 用户页面: http://localhost:8000
- 管理员页面: http://localhost:8000/admin
- API 文档: http://localhost:8000/docs

### 方式二：本地开发

**后端开发**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env ../.env
# 编辑 .env 文件

# 启动后端
uvicorn app.main:app --reload --port 8000
```

**前端开发**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器会在 http://localhost:5173 启动，并自动代理 API 请求到后端。

## 首次使用

### 1. 配置管理员账号

在 `.env` 文件中设置：
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### 2. 登录管理员后台

访问 http://localhost:8000/admin/login，使用配置的管理员账号登录。

### 3. 添加 AI 模型渠道

在管理员后台 -> 渠道管理 -> 添加渠道：
- 名称: 例如 "OpenAI GPT-4"
- Base URL: 例如 "https://api.openai.com/v1"
- API Key: 你的 OpenAI API Key
- Model ID: 例如 "gpt-4"
- RPM 限制: 例如 60
- 状态: 启用

### 4. 开始使用

访问 http://localhost:8000，选择模型，开始对话！

## 功能说明

### 用户功能
- ✅ 游客模式聊天（无需登录）
- ✅ 用户注册和登录
- ✅ 选择不同的 AI 模型
- ✅ 流式对话输出
- ✅ 聊天历史（仅浏览器内存）

### 管理员功能
- ✅ 渠道管理（添加、编辑、删除、启用/禁用）
- ✅ 系统设置（限流配置、日志保留）
- ✅ IP 黑名单管理（支持 CIDR）
- ✅ 日志查询和导出
- ✅ 统计面板（调用量、趋势、Token 消耗）

### 安全特性
- ✅ JWT Token 认证
- ✅ bcrypt 密码加密
- ✅ API Key 加密存储
- ✅ 双层限流机制
- ✅ IP 黑名单

## 生产部署

### 使用 Docker

1. 构建镜像
```bash
docker build -t pyaichat:latest .
```

2. 运行容器
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your_password \
  -e SECRET_KEY=your_secret_key \
  -e ENCRYPTION_KEY=your_encryption_key \
  --name pyaichat \
  pyaichat:latest
```

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 环境变量说明

| 变量 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| ADMIN_USERNAME | 是 | 管理员用户名 | admin |
| ADMIN_PASSWORD | 是 | 管理员密码 | - |
| SECRET_KEY | 是 | JWT 签名密钥 | - |
| ENCRYPTION_KEY | 是 | API Key 加密密钥 | - |
| DATABASE_PATH | 否 | 数据库路径 | ./data/chat.db |
| GUEST_RPM | 否 | 游客 RPM 限制 | 10 |
| USER_RPM | 否 | 用户 RPM 限制 | 60 |
| LOG_RETENTION_DAYS | 否 | 日志保留天数 | 90 |

## 常见问题

### 1. 如何生成安全的密钥？

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. 如何重置管理员密码？

修改 `.env` 文件中的 `ADMIN_PASSWORD`，重启服务即可。

### 3. 数据存储在哪里？

SQLite 数据库存储在 `./data/chat.db`（可通过 `DATABASE_PATH` 配置）。

### 4. 如何备份数据？

备份 `./data` 目录即可。

### 5. 支持哪些 AI 模型？

支持所有兼容 OpenAI API 格式的模型，包括：
- OpenAI (GPT-3.5, GPT-4, GPT-4o)
- Anthropic Claude (通过兼容层)
- 其他兼容 OpenAI API 的服务

## 开发说明

### 后端技术栈
- FastAPI: Web 框架
- SQLAlchemy: ORM
- Pydantic: 数据验证
- python-jose: JWT
- passlib: 密码加密
- httpx: HTTP 客户端

### 前端技术栈
- Vue 3: 前端框架
- TypeScript: 类型系统
- Vite: 构建工具
- Tailwind CSS: 样式框架
- Pinia: 状态管理
- Axios: HTTP 客户端

### API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 API 文档。

## 下一步优化建议

1. 添加 ECharts 图表可视化
2. 实现日志自动清理定时任务
3. 添加更多的错误处理和用户提示
4. 实现 WebSocket 支持（可选）
5. 添加单元测试和集成测试
6. 优化前端 UI/UX
7. 添加更多的管理员功能（用户管理等）

## 许可证

MIT License
