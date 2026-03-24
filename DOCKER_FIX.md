# Docker 部署修复说明

## 问题原因

Docker 容器中的数据库文件是旧版本，缺少新增的 `admins` 表。当调用修改管理员账密接口时，尝试查询或插入该表导致 500 错误。

## 修复内容

修改了 `backend/app/database.py` 文件，在 `init_db()` 函数中显式导入所有模型，确保在应用启动时创建缺失的表。

## 部署步骤

### 方案 1：重新构建镜像（推荐）

```bash
# 1. 构建新镜像
docker build -t ghcr.io/auunes/pyaichat:latest .

# 2. 推送到镜像仓库（如果需要）
docker push ghcr.io/auunes/pyaichat:latest

# 3. 停止并删除旧容器
docker stop pyaichat
docker rm pyaichat

# 4. 启动新容器
docker-compose up -d

# 5. 查看日志确认启动成功
docker logs -f pyaichat
```

### 方案 2：删除旧数据库（数据会丢失）

如果不需要保留旧数据：

```bash
# 1. 停止容器
docker stop pyaichat

# 2. 删除旧数据库
rm -f ./data/chat.db

# 3. 重新启动容器
docker start pyaichat
```

### 方案 3：手动添加表（保留数据）

如果需要保留数据，可以手动在数据库中创建 `admins` 表：

```bash
# 1. 进入容器
docker exec -it pyaichat bash

# 2. 安装 sqlite3（如果没有）
apt-get update && apt-get install -y sqlite3

# 3. 打开数据库
sqlite3 /app/data/chat.db

# 4. 创建 admins 表
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# 5. 创建索引
CREATE INDEX IF NOT EXISTS ix_admins_id ON admins (id);
CREATE INDEX IF NOT EXISTS ix_admins_username ON admins (username);

# 6. 退出
.exit
exit

# 7. 重启容器
docker restart pyaichat
```

## 验证

部署完成后，测试修改管理员账密接口：

```bash
# 1. 登录获取 token
curl -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"adminadmin"}'

# 2. 修改密码（替换 YOUR_TOKEN）
curl -X PUT http://localhost:8000/api/admin/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"current_password":"adminadmin","new_password":"newpassword123"}'
```

如果返回 `{"message": "更新成功，请重新登录"}`，说明修复成功。
