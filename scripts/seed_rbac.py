r"""Bootstrap RBAC permissions, the admin role, and optionally an admin user.

Usage (PowerShell, from project root):

    $env:ADMIN_USERNAME = 'admin'
    $env:ADMIN_EMAIL = 'admin@example.com'
    $env:ADMIN_PASSWORD = '<strong-password>'
    D:\Anaconda\envs\chenguang\python.exe scripts\seed_rbac.py

If ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD are omitted, only the
permissions and admin role are created.
"""

import asyncio
import os
import sys
from pathlib import Path

# Allow running as: python scripts\seed_rbac.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.infra.database import AsyncSessionLocal
from src.modules.permission.model import Permission
from src.modules.role.model import Role
from src.modules.user.model import User
from src.utils.password_utils import hash_password

PERMISSIONS = {
    "system:user": ("用户管理", "管理用户账号和用户角色"),
    "system:role": ("角色管理", "管理角色和角色权限"),
    "system:permission": ("权限管理", "管理权限项"),
}


async def get_or_create_permission(
    session,
    code: str,
    name: str,
    description: str,
) -> Permission:
    permission = await session.scalar(
        select(Permission).where(Permission.code == code)
    )
    if permission:
        return permission

    permission = Permission(code=code, name=name, description=description)
    session.add(permission)
    await session.flush()
    return permission


async def main() -> None:
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    async with AsyncSessionLocal() as session:
        permissions = []
        for code, (name, description) in PERMISSIONS.items():
            permissions.append(
                await get_or_create_permission(session, code, name, description)
            )

        role = await session.scalar(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.code == "admin")
        )
        if not role:
            role = Role(
                code="admin",
                name="管理员",
                description="系统管理员",
                permissions=permissions,
            )
            session.add(role)
            await session.flush()
        else:
            existing_codes = {permission.code for permission in role.permissions}
            for permission in permissions:
                if permission.code not in existing_codes:
                    role.permissions.append(permission)

        if username and email and password:
            user = await session.scalar(
                select(User)
                .options(selectinload(User.roles))
                .where(User.username == username)
            )
            if not user:
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hash_password(password),
                    is_active=True,
                    is_superuser=True,
                    roles=[role],
                )
                session.add(user)
                await session.flush()
            else:
                user.is_active = True
                user.is_superuser = True
                user.roles = [role]

            print(f"Admin user ready: {username}")
        else:
            print(
                "RBAC permissions and admin role are ready. "
                "Set ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD to create an admin user."
            )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())