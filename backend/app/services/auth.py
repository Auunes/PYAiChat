from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas import UserCreate
from app.utils import get_password_hash, verify_password, create_access_token
from app.config import settings
from typing import Optional


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("邮箱已被注册")

        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = User(email=user_data.email, password_hash=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """验证用户"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def authenticate_admin(username: str, password: str) -> bool:
        """验证管理员"""
        return (
            username == settings.ADMIN_USERNAME
            and password == settings.ADMIN_PASSWORD
        )

    @staticmethod
    def create_token(subject: str, token_type: str = "user") -> str:
        """创建访问令牌"""
        return create_access_token({"sub": subject, "type": token_type})
