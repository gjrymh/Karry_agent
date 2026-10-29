from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# config.py 位于：
# project/src/core/config.py
#
# parents[0] = src/core
# parents[1] = src
# parents[2] = project
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """应用全局配置。"""

    # ==================== 应用配置 ====================

    APP_NAME: str = "Karry Agent"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # ==================== JWT 配置 ====================
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # ==================== MySQL 配置 ====================

    # Python 应用当前运行在 Windows 宿主机上，因此使用 127.0.0.1:3307。
    #
    # 如果以后把 Python 应用也放进同一个 Docker Compose 网络：
    # DB_HOST 应改成 mysql
    # DB_PORT 应改成 3306
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3307
    DB_USER: str = "root"

    # 变量名与当前 .env 保持一致
    MYSQL_ROOT_PASSWORD: SecretStr
    MYSQL_DATABASE: str

    # ==================== Redis 配置 ====================

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # 变量名与当前 .env 保持一致
    REDIS_PASSWORD: SecretStr

    # ==================== MinIO 配置 ====================

    # MinIO Python SDK 一般使用 host:port，不带 http://
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_SECURE: bool = False

    # 变量名与当前 .env 保持一致
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: SecretStr

    # ==================== 日志配置 ====================

    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: Path = Path("logs")

    # ==================== 组合连接地址 ====================

    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy 异步 MySQL 连接地址。"""

        user = quote_plus(self.DB_USER)
        password = quote_plus(
            self.MYSQL_ROOT_PASSWORD.get_secret_value()
        )
        database = quote_plus(self.MYSQL_DATABASE)

        return (
            f"mysql+asyncmy://{user}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{database}"
            f"?charset=utf8mb4"
        )

    @property
    def REDIS_URL(self) -> str:
        """带密码的 Redis 连接地址。"""

        password = quote_plus(
            self.REDIS_PASSWORD.get_secret_value()
        )

        return (
            f"redis://:{password}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    @property
    def MINIO_URL(self) -> str:
        """带协议的 MinIO API 地址，适用于 HTTP 客户端或 boto3。"""

        scheme = "https" if self.MINIO_SECURE else "http"
        return f"{scheme}://{self.MINIO_ENDPOINT}"

    # Pydantic Settings v2 配置
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """创建并缓存全局 Settings 实例。"""

    return Settings()


settings = get_settings()