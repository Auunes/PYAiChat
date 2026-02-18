from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import os

# 确保数据目录存在
os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)

# 创建异步引擎
DATABASE_URL = f"sqlite+aiosqlite:///{settings.DATABASE_PATH}"
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 创建基类
Base = declarative_base()


# 依赖注入：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 初始化数据库
async def init_db():
    """初始化数据库，确保所有表都存在"""
    # 导入所有模型以确保它们被注册到 Base.metadata
    from app.models import User, Channel, SystemConfig, BlockedIP, ChatLog, Announcement, Admin

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
