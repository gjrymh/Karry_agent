from fastapi import Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import BizException
from src.infra.database import get_db
from src.modules.role.model import Role
from src.modules.user.model import User
from src.utils.jwt_utils import oauth2_scheme, verify_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT token 中解析当前登录用户，并预加载角色/权限。"""
    try:
        payload = verify_jwt(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise BizException(code=401, message="未登录或 token 已过期")

    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = await db.scalar(stmt)
    if not user:
        raise BizException(code=401, message="用户不存在")
    if not user.is_active:
        raise BizException(code=401, message="账号已被禁用")

    return user


def require_any_permission(*permission_codes: str):
    """要求当前用户至少拥有一个指定权限；超级管理员直接放行。"""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        granted = {
            permission.code
            for role in current_user.roles
            for permission in role.permissions
        }
        if not granted.intersection(permission_codes):
            raise BizException(code=403, message="无权限执行此操作")
        return current_user

    return checker


class PageParams:
    """通用分页参数，通过 Depends 注入到接口中"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码，从1开始"),
        page_size: int = Query(10, ge=1, le=100, description="每页条数"),
        keyword: str | None = Query(None, description="搜索关键词"),
    ):
        self.page = page
        self.page_size = page_size
        self.keyword = keyword

    @property
    def offset(self) -> int:
        """计算 SQL OFFSET"""
        return (self.page - 1) * self.page_size