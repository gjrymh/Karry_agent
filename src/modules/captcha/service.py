import base64
import random
import string
import uuid

from captcha.image import ImageCaptcha
from redis.asyncio import Redis

from src.core.exceptions import BizException
from src.modules.captcha.schema import CaptchaRead, CaptchaVerifyRequest

CAPTCHA_EXPIRE = 300  # 5分钟
CAPTCHA_PREFIX = "captcha:"


def _random_code(length: int = 4) -> str:
    """生成随机字母+数字验证码，去掉易混淆字符"""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
    return "".join(random.choices(chars, k=length))


class CaptchaService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.image_captcha = ImageCaptcha(width=108, height=36)

    async def create_captcha(self) -> CaptchaRead:
        """生成图片验证码，返回 key 和 base64 图片"""
        code = _random_code()
        captcha_id = str(uuid.uuid4())

        image_data = self.image_captcha.generate(code)
        b64 = base64.b64encode(image_data.read()).decode()

        # 存入 Redis，统一转小写，一次性验证
        await self.redis.set(f"{CAPTCHA_PREFIX}{captcha_id}", code.lower(), ex=CAPTCHA_EXPIRE)

        return CaptchaRead(key=captcha_id, image=f"data:image/png;base64,{b64}")

    async def verify(self, data: CaptchaVerifyRequest) -> None:
        """校验验证码，成功后立即删除（一次性）；失败抛业务异常"""
        redis_key = f"{CAPTCHA_PREFIX}{data.key}"
        stored = await self.redis.get(redis_key)

        if not stored:
            raise BizException(code=400, message="验证码已过期或不存在")
        if stored != data.code.lower():
            raise BizException(code=400, message="验证码错误")

        await self.redis.delete(redis_key)