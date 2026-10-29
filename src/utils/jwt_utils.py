from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer

from src.core.config import get_settings

settings = get_settings()
SECRET_KEY = settings.JWT_SECRET_KEY.get_secret_value()
ALGORITHM = settings.JWT_ALGORITHM

# 配置 OAuth2 Bearer 模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def encode_jwt(payload: dict) -> str:
    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload_copy["iat"] = datetime.now(timezone.utc)
    return jwt.encode(payload_copy, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("token已经过期")
    except jwt.InvalidTokenError:
        raise Exception("非法token")
    except Exception as e:
        raise Exception(f"token校验失败: {str(e)}")