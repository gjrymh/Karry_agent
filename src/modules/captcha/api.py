from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from src.core.base_schema import ResponseSchema
from src.infra.redis_cache import get_redis_client
from src.modules.captcha.schema import CaptchaRead, CaptchaVerifyRequest
from src.modules.captcha.service import CaptchaService

router = APIRouter(prefix="/captcha", tags=["Captcha"])


def get_captcha_service(redis: Redis = Depends(get_redis_client)) -> CaptchaService:
    return CaptchaService(redis)


@router.get("", response_model=ResponseSchema[CaptchaRead])
async def get_captcha(svc: CaptchaService = Depends(get_captcha_service)):
    """获取图片验证码，返回 key 和 base64 图片"""
    return ResponseSchema(data=await svc.create_captcha())


@router.post("/verify", response_model=ResponseSchema[None])
async def verify_captcha(
    body: CaptchaVerifyRequest,
    svc: CaptchaService = Depends(get_captcha_service),
):
    """验证验证码，验证成功后立即删除（一次性）"""
    await svc.verify(body)
    return ResponseSchema(message="验证成功")