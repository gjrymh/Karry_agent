from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult, ResponseSchema
from src.core.deps import PageParams, require_any_permission
from src.infra.database import get_db
from src.modules.permission.schema import (
    PermissionCreate,
    PermissionRead,
    PermissionUpdate,
)
from src.modules.permission.service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permission"])

PERMISSION_MANAGE_PERMISSION = require_any_permission("system:permission")
PERMISSION_READ_PERMISSION = require_any_permission(
    "system:permission", "system:role"
)


def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(db)


@router.get(
    "",
    response_model=ResponseSchema[PageResult[PermissionRead]],
    summary="分页查询权限",
    dependencies=[Depends(PERMISSION_READ_PERMISSION)],
)
async def list_permissions(
    params: PageParams = Depends(),
    service: PermissionService = Depends(get_permission_service),
):
    page_result = await service.list_permissions(params)
    page_result.items = [PermissionRead.model_validate(p) for p in page_result.items]
    return ResponseSchema(data=page_result)


@router.get(
    "/search",
    response_model=ResponseSchema[PageResult[PermissionRead]],
    summary="搜索权限",
    dependencies=[Depends(PERMISSION_READ_PERMISSION)],
)
async def search_permissions(
    params: PageParams = Depends(),
    service: PermissionService = Depends(get_permission_service),
):
    page_result = await service.list_permissions(params)
    page_result.items = [PermissionRead.model_validate(p) for p in page_result.items]
    return ResponseSchema(data=page_result)


@router.post(
    "",
    response_model=ResponseSchema[PermissionRead],
    summary="创建权限",
    dependencies=[Depends(PERMISSION_MANAGE_PERMISSION)],
)
async def create_permission(
    data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
):
    permission = await service.create_permission(data)
    return ResponseSchema(data=PermissionRead.model_validate(permission))


@router.get(
    "/{permission_id}",
    response_model=ResponseSchema[PermissionRead],
    summary="根据 ID 获取权限详情",
    dependencies=[Depends(PERMISSION_READ_PERMISSION)],
)
async def get_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
):
    permission = await service.get_permission(permission_id)
    return ResponseSchema(data=PermissionRead.model_validate(permission))


@router.put(
    "/{permission_id}",
    response_model=ResponseSchema[PermissionRead],
    summary="更新权限",
    dependencies=[Depends(PERMISSION_MANAGE_PERMISSION)],
)
async def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
):
    permission = await service.update_permission(permission_id, data)
    return ResponseSchema(data=PermissionRead.model_validate(permission))


@router.delete(
    "/{permission_id}",
    response_model=ResponseSchema[None],
    summary="删除权限",
    dependencies=[Depends(PERMISSION_MANAGE_PERMISSION)],
)
async def delete_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
):
    await service.delete_permission(permission_id)
    return ResponseSchema(data=None)