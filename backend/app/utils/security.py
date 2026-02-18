from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
import hashlib
import secrets

# 使用 PBKDF2-SHA256 替代 bcrypt，支持任意长度密码
HASH_ITERATIONS = 100000  # PBKDF2 迭代次数


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 格式: algorithm$salt$hash
        parts = hashed_password.split('$')
        if len(parts) != 3:
            return False

        algorithm, salt, stored_hash = parts
        if algorithm != 'pbkdf2_sha256':
            return False

        # 使用相同的 salt 计算哈希
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            bytes.fromhex(salt),
            HASH_ITERATIONS
        ).hex()

        # 常量时间比较，防止时序攻击
        return secrets.compare_digest(password_hash, stored_hash)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # 生成随机 salt (32 字节)
    salt = secrets.token_bytes(32)

    # 使用 PBKDF2-SHA256 计算哈希
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        HASH_ITERATIONS
    ).hex()

    # 返回格式: algorithm$salt$hash
    return f'pbkdf2_sha256${salt.hex()}${password_hash}'


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
