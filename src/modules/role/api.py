from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult, ResponseSchema
from src.core.deps import PageParams, require_any_permission
from src.infra.database import get_db
from src.modules.role.schema import (
    RoleAssignPermissions,
    RoleCreate,
    RoleRead,
    RoleUpdate,
)
from src.modules.role.service import RoleService

router = APIRouter(prefix="/roles", tags=["Role"])

ROLE_MANAGE_PERMISSION = require_any_permission("system:role")
ROLE_READ_PERMISSION = require_any_permission("system:role", "system:user")


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db)


@router.post(
    "",
    response_model=ResponseSchema[RoleRead],
    summary="创建角色",
    dependencies=[Depends(ROLE_MANAGE_PERMISSION)],
)
async def create_role(
    role: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    data = await service.create_role(role)
    return ResponseSchema(data=RoleRead.model_validate(data))


@router.get(
    "",
    response_model=ResponseSchema[PageResult[RoleRead]],
    summary="分页查询角色",
    dependencies=[Depends(ROLE_READ_PERMISSION)],
)
async def list_roles(
    params: PageParams = Depends(),
    service: RoleService = Depends(get_role_service),
):
    page_result = await service.list_roles(params)
    page_result.items = [RoleRead.model_validate(r) for r in page_result.items]
    return ResponseSchema(data=page_result)


@router.get(
    "/search",
    response_model=ResponseSchema[PageResult[RoleRead]],
    summary="搜索角色",
    dependencies=[Depends(ROLE_READ_PERMISSION)],
)
async def search_roles(
    params: PageParams = Depends(),
    service: RoleService = Depends(get_role_service),
):
    page_result = await service.list_roles(params)
    page_result.items = [RoleRead.model_validate(r) for r in page_result.items]
    return ResponseSchema(data=page_result)


@router.get(
    "/{role_id}",
    response_model=ResponseSchema[RoleRead],
    summary="角色详情",
    dependencies=[Depends(ROLE_READ_PERMISSION)],
)
async def get_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    data = await service.get_role(role_id)
    return ResponseSchema(data=RoleRead.model_validate(data))


@router.put(
    "/{role_id}",
    response_model=ResponseSchema[RoleRead],
    summary="更新角色",
    dependencies=[Depends(ROLE_MANAGE_PERMISSION)],
)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    data = await service.update_role(role_id, role)
    return ResponseSchema(data=RoleRead.model_validate(data))


@router.delete(
    "/{role_id}",
    response_model=ResponseSchema[None],
    summary="删除角色",
    dependencies=[Depends(ROLE_MANAGE_PERMISSION)],
)
async def delete_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
):
    await service.delete_role(role_id)
    return ResponseSchema(data=None)


@router.put(
    "/{role_id}/permissions",
    response_model=ResponseSchema[RoleRead],
    summary="给角色分配权限",
    dependencies=[Depends(ROLE_MANAGE_PERMISSION)],
)
async def update_role_permissions(
    role_id: int,
    role_permissions: RoleAssignPermissions,
    service: RoleService = Depends(get_role_service),
):
    data = await service.assign_permissions(role_id, role_permissions.permission_ids)
    return ResponseSchema(data=RoleRead.model_validate(data))