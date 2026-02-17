from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI Chat System"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # 数据库配置
    DATABASE_PATH: str = "./data/chat.db"

    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str

    # 限流配置
    GUEST_RPM: int = 10
    USER_RPM: int = 60

    # 日志配置
    LOG_RETENTION_DAYS: int = 90

    # CORS 配置
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = Settings()
