from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult, ResponseSchema
from src.core.deps import PageParams, get_current_user, require_any_permission
from src.infra.database import get_db
from src.modules.user.model import User
from src.modules.user.schema import (
    UserAssignRoles,
    UserCreate,
    UserRead,
    UserWithRolesRead,
)
from src.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["User"])

USER_PERMISSION = require_any_permission("system:user")


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


async def _list_users_page(params: PageParams, svc: UserService):
    page_result = await svc.list_users(params)
    page_result.items = [UserRead.model_validate(u) for u in page_result.items]
    return ResponseSchema(data=page_result)


@router.get(
    "",
    response_model=ResponseSchema[PageResult[UserRead]],
    dependencies=[Depends(USER_PERMISSION)],
)
async def list_users(
    params: PageParams = Depends(),
    svc: UserService = Depends(get_user_service),
):
    return await _list_users_page(params, svc)


@router.get(
    "/search",
    response_model=ResponseSchema[PageResult[UserRead]],
    summary="搜索用户",
    dependencies=[Depends(USER_PERMISSION)],
)
async def search_users(
    params: PageParams = Depends(),
    svc: UserService = Depends(get_user_service),
):
    return await _list_users_page(params, svc)


@router.post(
    "",
    response_model=ResponseSchema[UserRead],
    dependencies=[Depends(USER_PERMISSION)],
)
async def create_user(
    data: UserCreate,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.create_user(data)
    return ResponseSchema(data=UserRead.model_validate(user))


# /me 只要求登录，不要求管理用户权限
@router.get("/me", response_model=ResponseSchema[UserRead])
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需要 token）"""
    return ResponseSchema(data=UserRead.model_validate(current_user))


@router.get(
    "/{user_id}",
    response_model=ResponseSchema[UserWithRolesRead],
    dependencies=[Depends(USER_PERMISSION)],
)
async def get_user(
    user_id: int,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user(user_id)
    return ResponseSchema(data=UserWithRolesRead.model_validate(user))


@router.put(
    "/{user_id}/roles",
    response_model=ResponseSchema[UserWithRolesRead],
    summary="给用户分配角色",
    dependencies=[Depends(USER_PERMISSION)],
)
async def assign_roles_to_user(
    user_id: int,
    data: UserAssignRoles,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.assign_roles(user_id, data.role_ids)
    return ResponseSchema(data=UserWithRolesRead.model_validate(user))


@router.delete(
    "/{user_id}",
    response_model=ResponseSchema[None],
    summary="删除用户",
    dependencies=[Depends(USER_PERMISSION)],
)
async def delete_user(
    user_id: int,
    svc: UserService = Depends(get_user_service),
):
    await svc.delete_user(user_id)
    return ResponseSchema(data=None)


@router.get(
    "/{user_id}/roles",
    response_model=ResponseSchema[list[UserWithRolesRead]],
    summary="查看用户的角色列表",
    dependencies=[Depends(USER_PERMISSION)],
)
async def get_user_roles(
    user_id: int,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user_with_roles(user_id)
    return ResponseSchema(data=[UserWithRolesRead.model_validate(user)])