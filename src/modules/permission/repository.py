from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_repository import BaseRepository
from src.modules.permission.model import Permission


class PermissionRepository(BaseRepository[Permission]):
    SEARCH_FIELDS = ["code", "name", ]

    def __init__(self, db: AsyncSession):
        super().__init__(Permission, db)

    async def get_by_code(self, code: str) -> Permission | None:
        # 根据 code 查询权限
        stmt = select(Permission).where(Permission.code == code)
        return await self.db.scalar(stmt)

    async def get_by_ids(self, ids: list[int]) -> list[Permission]:
        # 根据 ID 列表批量查询权限
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_page(
        self, offset: int, limit: int, keyword: str | None
    ) -> tuple[list[Permission], int]:
        return await self.get_page(
            offset=offset,
            limit=limit,
            keyword=keyword,
            search_fields=self.SEARCH_FIELDS,
        )
