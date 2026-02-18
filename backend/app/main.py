from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select
from app.config import settings
from app.database import init_db, get_db
from app.routers import auth_router, chat_router, admin_router
from app.models import BlockedIP
from app.utils import is_ip_in_range
from contextlib import asynccontextmanager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("数据库初始化完成")
    yield
    # 关闭时清理资源
    print("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
if settings.CORS_ORIGINS == "*":
    # 开发模式：允许所有源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # 通配符时不能用 credentials
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 生产模式：指定源
    origins = settings.CORS_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# IP 黑名单中间件
@app.middleware("http")
async def block_ip_middleware(request: Request, call_next):
    """IP 黑名单拦截"""
    # 管理员接口和 API 文档不受限制
    if request.url.path.startswith("/api/admin") or request.url.path.startswith("/docs"):
        return await call_next(request)

    # 检查 IP 是否被禁用
    ip_address = request.client.host
    async for db in get_db():
        result = await db.execute(select(BlockedIP))
        blocked_ips = result.scalars().all()

        for blocked in blocked_ips:
            if is_ip_in_range(ip_address, blocked.ip_address):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您的 IP 已被禁止访问",
                )
        break

    return await call_next(request)


# 注册路由
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)


# 静态文件服务（前端）
# Docker 环境下前端文件在 /app/frontend/dist
# 本地开发环境下在 ../../frontend/dist
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if not os.path.exists(frontend_dist):
    # Docker 环境路径
    frontend_dist = "/app/frontend/dist"

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """服务前端页面"""
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # SPA 路由回退到 index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
