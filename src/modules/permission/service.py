from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult
from src.core.deps import PageParams
from src.core.exceptions import BizException
from src.modules.permission.model import Permission
from src.modules.permission.repository import PermissionRepository
from src.modules.permission.schema import PermissionCreate, PermissionUpdate


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.repo = PermissionRepository(db)

    async def create_permission(self, data: PermissionCreate) -> Permission:
        # 1. 检查 code 是否已存在，已存在则抛 BizException
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise BizException(code=400, message="权限码已经存在")

        # 2. 创建 Permission 对象
        permission = Permission(
            code=data.code,
            name=data.name,
            description=data.description,
        )
        return await self.repo.create(permission)

    async def get_permission(self, permission_id: int) -> Permission:
        # 查不到抛 BizException(code=404)
        permission = await self.repo.get_by_id(permission_id)
        if not permission:
            raise BizException(code=404, message="权限不存在")
        return permission

    async def list_permissions(self, params: PageParams) -> PageResult:
        items, total = await self.repo.search_page(
            offset=params.offset,
            limit=params.page_size,
            keyword=params.keyword,
        )
        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def update_permission(
        self, permission_id: int, data: PermissionUpdate
    ) -> Permission:
        # 1. 查找权限，不存在抛异常
        permission = await self.get_permission(permission_id)

        # 2. name 不允许被置空；description 允许通过显式传 null 清空
        if data.name is not None:
            permission.name = data.name
        if "description" in data.model_fields_set:
            permission.description = data.description

        # 3. 调用 repo.update()
        return await self.repo.update(permission)

    async def delete_permission(self, permission_id: int) -> None:
        permission = await self.get_permission(permission_id)
        await self.repo.delete(permission)
