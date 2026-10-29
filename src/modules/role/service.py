from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_schema import PageResult
from src.core.deps import PageParams
from src.core.exceptions import BizException
from src.modules.permission.repository import PermissionRepository
from src.modules.role.model import Role
from src.modules.role.repository import RoleRepository
from src.modules.role.schema import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)

    async def create_role(self, data: RoleCreate) -> Role:
        # 检查 code 是否已存在
        role = await self.repo.get_by_code(data.code)
        if role:
            raise BizException(code=400, message=f"角色 {data.code} 已存在")

        role = Role(**data.model_dump())
        return await self.repo.create(role)

    async def get_role(self, role_id: int) -> Role:
        # 查不到抛异常
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise BizException(code=404, message=f"角色 {role_id} 不存在")
        return role

    async def list_roles(self, params: PageParams) -> PageResult:
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

    async def update_role(self, role_id: int, data: RoleUpdate) -> Role:
        role = await self.get_role(role_id)

        # name 不允许被置空；description 允许通过显式传 null 清空
        if data.name is not None:
            role.name = data.name
        if "description" in data.model_fields_set:
            role.description = data.description

        return await self.repo.update(role)

    async def delete_role(self, role_id: int) -> None:
        role = await self.get_role(role_id)
        await self.repo.delete(role)

    async def assign_permissions(self, role_id: int, permission_ids: list[int]) -> Role:
        # 1. 查找角色，不存在抛异常
        role = await self.get_role(role_id)

        # 2. 根据 permission_ids 批量查询 Permission 对象
        permission_list = await self.permission_repo.get_by_ids(permission_ids)

        # 3. 校验：如果查到的数量 != 传入的数量，说明有无效 ID，抛异常
        if len(permission_list) != len(permission_ids):
            raise BizException(code=400, message="权限 ID 列表中包含无效 ID")

        # 4. 直接替换角色的权限列表
        role.permissions = permission_list

        # 5. flush + refresh，返回更新后的 role（会自动带上新的 permissions）
        return await self.repo.update(role)
