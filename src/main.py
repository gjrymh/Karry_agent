from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import get_settings
from src.core.logger import setup_logger
from src.infra.database import engine
from src.core.exceptions import register_exception_handlers
from src.middlewares.logging import LoggingMiddleware
from src.modules.user.api import router as user_router
from src.modules.captcha.api import router as captcha_router
from src.modules.auth.api import router as auth_router
from src.modules.permission.api import router as permission_router
from src.modules.role.api import router as role_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    settings = get_settings()
    logger.info(f"{settings.APP_NAME} starting | env={settings.APP_ENV}")
    yield
    await engine.dispose()
    logger.info(f"{settings.APP_NAME} shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
    )

    # 异常处理
    register_exception_handlers(app)

    # CORS：Vite 固定端口 5173，保留 localhost 和 127.0.0.1 两种访问方式
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 中间件
    app.add_middleware(LoggingMiddleware)

    # 注册模块路由
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(captcha_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(permission_router, prefix="/api/v1")
    app.include_router(role_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health")
async def root():
    return {"status": "ok"}