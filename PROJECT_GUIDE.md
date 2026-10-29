# Karry Agent 项目说明书

> 面向对象：第一次接手本项目的工程师或 AI Coding Agent。  
> 目标：快速理解项目结构、启动方式、数据流、已完成功能、未完成功能和修改入口。  
> 整理时间：2026-10-28。  
> 代码基线：`D:\python\project\Karry_agent`，当前分支 `main`，最近提交 `68fdb03 RBAC基础功能实现`。  
> 说明：本文基于当前工作区代码静态阅读整理；未执行 `npm install`、前端构建或完整端到端联调。运行状态请按第 1 节自行验证。

---

## 0. 先看结论

### 0.1 项目是什么

Karry Agent 是一个“AI Agent 管理平台”的前后端项目：

- 后端：FastAPI + SQLAlchemy Async + MySQL + Redis + JWT + Alembic。
- 前端：React + TypeScript + Vite + Tailwind CSS + Shadcn/Radix UI。
- 目录约定：
  - `src/`：后端代码。
  - `app/`：前端代码，**所有前端页面、组件、服务、Mock 数据都在这里**。
  - `docker/`：MySQL、Redis、MinIO 的 Docker Compose 配置。
  - `alembic/`：数据库迁移。
  - `test/`：后端测试目录，目前基本为空。

### 0.2 当前完成度

后端目前真正实现的只有：

1. 图形验证码。
2. 用户名/密码登录 + JWT 签发。
3. 获取当前登录用户。
4. 用户、角色、权限的 RBAC 基础 CRUD/关联接口。

后端**没有实现**：

- Agent 管理
- 模型管理
- Prompt 管理
- 知识库/RAG
- 工具管理
- 对话日志
- 数据统计
- 工作台
- API Key
- 审计日志
- 告警规则
- 系统配置

前端有完整的 30+ 个页面和 Mock 数据，默认运行在 Mock 模式。因此：

> **默认打开前端看到的是 Mock 演示数据，不是后端真实数据。**  
> 只有设置 `VITE_USE_MOCK=false` 后，前端才会尝试连接后端。

### 0.3 最重要的注意事项

如果让 AI 或新同事直接改代码，必须先知道下面几件事：

1. `app/` 是辰光 Agent 平台最早版本的前端原型，很多页面仍是 Mock 或静态展示。
2. 前端和后端的接口契约目前没有完全对齐，尤其是系统管理模块。
3. 后端已配置 CORS，允许 Vite 开发服务器访问；前端 API Base 已统一为 `http://localhost:8000/api/v1`。
4. 用户/角色/权限接口已经要求 JWT 登录，并按 `system:user`、`system:role`、`system:permission` 校验权限；`is_superuser` 账号直接放行。
5. JWT 密钥已迁移到 `.env` 的 `JWT_SECRET_KEY`，不再硬编码在源码中。
6. 当前 `test/` 没有有效测试，不能把“有接口”当成“已验证”。

---

## 1. 快速开始

### 1.1 本机环境基线

当前机器已验证：

- Python：`Python 3.12.10`
- Node：`v22.22.2`
- npm：`10.9.7`
- Docker Desktop：已安装
- Git：已安装

建议使用 Python 3.12+、Node 20.19+（Vite 7 的要求）。

### 1.2 目录结构

```text
Karry_agent/
├─ src/                         # FastAPI 后端
│  ├─ main.py                   # 应用入口、路由注册
│  ├─ core/                     # 配置、数据库会话、依赖、基础模型、异常、日志
│  ├─ infra/                    # MySQL / Redis 连接
│  ├─ middlewares/              # 请求日志中间件
│  ├─ modules/                  # 业务模块
│  │  ├─ auth/                  # 登录
│  │  ├─ captcha/               # 图形验证码
│  │  ├─ user/                  # 用户
│  │  ├─ role/                  # 角色
│  │  └─ permission/            # 权限
│  └─ utils/                    # JWT、密码哈希
├─ alembic/                     # 数据库迁移
├─ app/                         # React 前端
│  ├─ src/App.tsx               # 前端路由入口
│  ├─ src/pages/                # 所有页面
│  ├─ src/services/             # Mock/API 服务层
│  ├─ src/components/           # 通用组件和 Shadcn UI
│  ├─ src/layouts/              # 布局
│  └─ docs/                     # 前端设计文档（部分内容已过时）
├─ docker/                      # MySQL/Redis/MinIO Compose
├─ test/                        # 后端测试目录（当前基本为空）
├─ .env                         # 本地密钥配置（已 gitignore）
├─ .env.example                 # 环境变量示例
├─ alembic.ini
├─ requirements.txt
└─ PROJECT_GUIDE.md             # 本文件
```

### 1.3 启动基础设施

在项目根目录执行：

```powershell
cd D:\python\project\Karry_agent
docker compose -f docker/docker-compose.yaml --env-file .env up -d
docker compose -f docker/docker-compose.yaml ps
```

端口映射：

| 服务 | 宿主机端口 | 容器端口 | 说明 |
|---|---:|---:|---|
| MySQL | 3307 | 3306 | 数据库 `chenguang` |
| Redis | 6379 | 6379 | 验证码、缓存 |
| MinIO API | 9000 | 9000 | 当前代码尚未使用 |
| MinIO Console | 9001 | 9001 | 当前代码尚未使用 |

注意：

- `docker/mysql/data`、`docker/redis/data`、`docker/minio/data` 是持久化数据，不要删除。
- 根目录 `.env` 是本地密钥文件，已加入 `.gitignore`，不要提交。
- 新增环境变量时同步更新 `.env.example`，但不要写入真实密码。

### 1.4 启动后端

```powershell
cd D:\python\project\Karry_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

如果 PowerShell 不允许激活虚拟环境，也可以直接：

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

验证：

- 健康检查：`http://localhost:8000/health`
- Swagger：`http://localhost:8000/docs`
- OpenAPI：`http://localhost:8000/openapi.json`

### 1.5 初始化管理员

项目提供 `scripts/seed_rbac.py`，用于创建默认 RBAC 权限、`admin` 角色和首个管理员账号：

```powershell
cd D:\python\project\Karry_agent
$env:ADMIN_USERNAME = 'admin'
$env:ADMIN_EMAIL = 'admin@example.com'
$env:ADMIN_PASSWORD = '请替换为强密码'
D:\Anaconda\envs\chenguang\python.exe scripts\seed_rbac.py
```

脚本会创建以下权限：

- `system:user`
- `system:role`
- `system:permission`

如果数据库中已有 `admin` 角色，会复用并补充缺失权限；如果管理员用户已存在，会复用并设置 `is_superuser=True`，不会覆盖已有密码。

说明：

- 密码会用 bcrypt 哈希后存入 `users.hashed_password`。
- 用户/角色/权限 CRUD 接口现在需要 Bearer Token。
- 登录需要图形验证码；验证码存在 Redis 的 `captcha:<key>` 中，5 分钟过期，值为小写验证码。
- 如果通过接口调试登录，可以从 Redis 读取验证码；更推荐通过前端登录页完成。
### 1.6 启动前端

```powershell
cd D:\python\project\Karry_agent\app
npm install
npm run dev
```

默认是 Mock 模式：

- 任意非空用户名和密码都可以登录。
- 验证码由前端本地生成并显示。
- 所有业务页面使用 `app/src/services/mock` 下的数据。

连接真实后端时，在 `app/.env.local` 中配置：

```env
VITE_USE_MOCK=false
VITE_API_BASE=http://localhost:8000/api/v1
```

然后重新执行：

```powershell
npm run dev
```

> 后端已在 `src/main.py` 配置 `CORSMiddleware`，允许 `http://localhost:5173` 和 `http://127.0.0.1:5173`。

---

## 2. 总体架构

### 2.1 数据流

```text
浏览器
  -> React 页面 (app/src/pages)
  -> 服务包装层 (app/src/services/<module>.ts)
       -> USE_MOCK=true  -> Mock 服务 (app/src/services/mock)
       -> USE_MOCK=false -> API 客户端 (app/src/services/api)
  -> fetch -> FastAPI /api/v1
  -> Router -> Service -> Repository -> SQLAlchemy AsyncSession
  -> MySQL / Redis
```

### 2.2 后端分层

| 层 | 位置 | 职责 |
|---|---|---|
| 入口 | `src/main.py` | 创建 FastAPI、注册路由、中间件、异常处理 |
| 配置 | `src/core/config.py` | 读取 `.env`，生成数据库/Redis URL |
| 会话 | `src/infra/database.py` | 创建异步引擎、`get_db` 自动提交/回滚 |
| 基础模型 | `src/core/base_model.py` | `id`、`created_at`、`updated_at` |
| 基础仓储 | `src/core/base_repository.py` | 通用 CRUD、分页、模糊搜索 |
| Schema | `src/core/base_schema.py` | 统一响应、分页响应 |
| 依赖 | `src/core/deps.py` | 当前用户、分页参数 |
| 异常 | `src/core/exceptions.py` | `BizException` 和全局异常处理 |
| 模块 | `src/modules/<module>/` | `model`、`schema`、`repository`、`service`、`api` |

### 2.3 前端分层

| 层 | 位置 | 职责 |
|---|---|---|
| 路由 | `app/src/App.tsx` | 页面路由和登录保护 |
| 布局 | `app/src/layouts/DashboardLayout.tsx` | 侧边栏、顶栏、面包屑 |
| 页面 | `app/src/pages/` | 各业务页面 |
| 通用组件 | `app/src/components/` | AuthGuard、Pagination、Shadcn UI |
| 服务包装 | `app/src/services/*.ts` | 根据 `USE_MOCK` 选择 Mock 或 API |
| Mock | `app/src/services/mock/` | 本地模拟数据和延迟 |
| API | `app/src/services/api/` | fetch 请求封装 |
| 类型 | `app/src/services/types/` | 前端业务类型 |

---

## 3. 后端详解

### 3.1 入口 `src/main.py`

- 使用 `lifespan` 初始化日志和关闭数据库引擎。
- 注册 `LoggingMiddleware`。
- 注册 5 个路由模块：
  - `user_router` -> `/api/v1/users`
  - `captcha_router` -> `/api/v1/captcha`
  - `auth_router` -> `/api/v1/auth`
  - `permission_router` -> `/api/v1/permissions`
  - `role_router` -> `/api/v1/roles`
- 额外健康检查：`GET /health`。
- 已配置 CORS。
- 没有静态文件托管。
- 没有注册 Agent/模型/Prompt/知识库/工具/对话/统计路由。

### 3.2 配置 `src/core/config.py`

从项目根目录 `.env` 读取配置，主要字段：

| 字段 | 默认值/说明 |
|---|---|
| `APP_NAME` | `Karry Agent` |
| `APP_ENV` | `development` |
| `APP_DEBUG` | `true` |
| `DB_HOST` | `127.0.0.1` |
| `DB_PORT` | `3307` |
| `DB_USER` | `root` |
| `MYSQL_ROOT_PASSWORD` | 必填，`SecretStr` |
| `MYSQL_DATABASE` | 必填，当前为 `chenguang` |
| `REDIS_HOST` | `127.0.0.1` |
| `REDIS_PORT` | `6379` |
| `REDIS_DB` | `0` |
| `REDIS_PASSWORD` | 必填，`SecretStr` |
| `MINIO_ENDPOINT` | `127.0.0.1:9000` |
| `MINIO_SECURE` | `false` |
| `MINIO_ROOT_USER` | 必填 |
| `MINIO_ROOT_PASSWORD` | 必填，`SecretStr` |
| `JWT_SECRET_KEY` | 必填，`SecretStr`，使用随机长字符串 |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRE_MINUTES` | `30` |
| `LOG_LEVEL` | `DEBUG` |
| `LOG_DIR` | `logs` |

生成的连接串：

- `DATABASE_URL`：`mysql+asyncmy://...`
- `REDIS_URL`：`redis://:...`
- `MINIO_URL`：`http://127.0.0.1:9000`

安全要求：

- 不要把 `.env` 提交到 Git。
- 不要把真实密码、JWT 密钥写进 Markdown 或代码注释。
- `MINIO_*` 目前只有配置，没有业务代码使用。

### 3.3 数据库会话 `src/infra/database.py`

- 使用 `create_async_engine` + `asyncmy`。
- `AsyncSessionLocal` 的 `expire_on_commit=False`。
- `get_db()` 的行为：
  - 正常结束：`await session.commit()`。
  - 异常：`await session.rollback()` 后重新抛出。

因此业务 Service 中通常只需要 `flush()`，不需要手动 `commit()`。

### 3.4 基础模型和仓储

`BaseModel`：

- `id: BigInteger, primary_key=True, autoincrement=True`
- `created_at: DateTime, server_default=now()`
- `updated_at: DateTime, server_default=now(), onupdate=now()`

`BaseRepository` 提供：

- `get_by_id`
- `get_all`
- `create`
- `update`
- `delete`
- `get_page(offset, limit, keyword, search_fields)`

`get_page` 会返回 `(items, total)`，并支持简单 `LIKE` 模糊搜索。

### 3.5 统一响应和异常

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

分页响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 10
  }
}
```

业务异常：

```json
{
  "code": 400,
  "message": "业务错误信息",
  "data": null
}
```

注意：

- `BizException` 当前由异常处理器返回 **HTTP 200**，业务错误码放在 JSON 的 `code` 字段。
- 未处理异常返回 HTTP 500。
- 前端 `apiClient` 会检查 `json.code`，但只在 HTTP 401 时跳转登录页；业务 401 不会自动跳转。

### 3.6 认证链路

#### 验证码

- `GET /api/v1/captcha`
- 生成 4 位字母数字验证码，去掉易混淆字符。
- 返回 `key` 和 base64 图片。
- Redis key：`captcha:<uuid>`。
- 有效期：300 秒。
- 验证成功后立即删除，一次性使用。

#### 登录

- `POST /api/v1/auth/login`
- 请求体：

```json
{
  "username": "admin",
  "password": "******",
  "captcha_key": "uuid",
  "captcha_code": "ABCD"
}
```

- 校验验证码。
- 查询用户。
- bcrypt 校验密码。
- 校验 `is_active`。
- 更新 `last_login`。
- 签发 JWT，默认 30 分钟过期，`sub` 为用户 ID。

#### 当前用户

- `GET /api/v1/users/me`
- 依赖 `get_current_user`：解析 Bearer Token -> 查询用户 -> 校验 `is_active`。
- 当前只有这个接口使用了登录依赖。

#### 已知安全缺口

- JWT `SECRET_KEY` 硬编码在 `src/utils/jwt_utils.py`。
- 没有 refresh token。
- 没有服务端 logout / token 黑名单。
- 用户、角色、权限 CRUD 接口大多没有 `get_current_user` 依赖。
- 没有真正的权限码校验，RBAC 目前只是数据模型和 CRUD。

### 3.7 数据库表

当前只有 RBAC 相关表：

| 表 | 字段 |
|---|---|
| `users` | `id`, `username`, `email`, `hashed_password`, `is_active`, `is_superuser`, `last_login`, `created_at`, `updated_at` |
| `roles` | `id`, `code`, `name`, `description`, `created_at`, `updated_at` |
| `permissions` | `id`, `code`, `name`, `description`, `created_at`, `updated_at` |
| `user_roles` | `user_id`, `role_id` |
| `role_permissions` | `role_id`, `permission_id` |

关系：

- 用户 `<-> 角色`：多对多，`user_roles`。
- 角色 `<-> 权限`：多对多，`role_permissions`。
- `User.roles`、`Role.permissions` 使用 `lazy="selectin"`。

### 3.8 当前后端接口清单

| 方法 | 路径 | 功能 | 是否保护 |
|---|---|---|---|
| GET | `/health` | 健康检查 | 否 |
| GET | `/api/v1/captcha` | 获取验证码 | 否 |
| POST | `/api/v1/captcha/verify` | 校验验证码 | 否 |
| POST | `/api/v1/auth/login` | 登录 | 否 |
| GET | `/api/v1/users` | 用户分页列表 | 否 |
| GET | `/api/v1/users/search` | 用户搜索（兼容前端） | 否 |
| POST | `/api/v1/users` | 创建用户 | 否 |
| GET | `/api/v1/users/me` | 当前用户 | 是 |
| GET | `/api/v1/users/{user_id}` | 用户详情（含 roles） | 否 |
| PUT | `/api/v1/users/{user_id}/roles` | 给用户分配角色（`{role_ids}`） | 否 |
| GET | `/api/v1/users/{user_id}/roles` | 查询用户角色 | 否 |
| DELETE | `/api/v1/users/{user_id}` | 删除用户 | 否 |
| POST | `/api/v1/roles` | 创建角色 | 否 |
| GET | `/api/v1/roles` | 角色分页列表 | 否 |
| GET | `/api/v1/roles/search` | 角色搜索（兼容前端） | 否 |
| GET | `/api/v1/roles/{role_id}` | 角色详情 | 否 |
| PUT | `/api/v1/roles/{role_id}` | 更新角色 | 否 |
| DELETE | `/api/v1/roles/{role_id}` | 删除角色 | 否 |
| PUT | `/api/v1/roles/{role_id}/permissions` | 给角色分配权限 | 否 |
| GET | `/api/v1/permissions` | 权限分页列表 | 否 |
| GET | `/api/v1/permissions/search` | 权限搜索（兼容前端） | 否 |
| POST | `/api/v1/permissions` | 创建权限 | 否 |
| GET | `/api/v1/permissions/{permission_id}` | 权限详情 | 否 |
| PUT | `/api/v1/permissions/{permission_id}` | 更新权限 | 否 |
| DELETE | `/api/v1/permissions/{permission_id}` | 删除权限 | 否 |

注意：`PUT /users/{user_id}/roles` 的请求体是对象，例如：

```json
{"role_ids": [1, 2]}
```

---

## 4. 前端详解

### 4.1 实际技术栈

以 `app/package.json` 为准：

| 类别 | 实际版本/说明 |
|---|---|
| React | `^19.2.0` |
| React Router | `^7.13.0` |
| Vite | `^7.2.4` |
| TypeScript | `~5.9.3` |
| Tailwind CSS | `^4.1.18` |
| UI | Shadcn/Radix 组件 |
| 图标 | Lucide React |
| 构建 | `tsc -b && vite build` |

注意：

- `app/README.md` 写的是 React 18 + React Router v6，已过时。
- `app/docs/00-架构总览.md` 也把后端标为“待实现”，但当前后端已经有一部分 RBAC。
- 前端严格模式 `"strict": true`，但现有代码中存在多处类型不一致，详见第 6 节。

### 4.2 前端路由

入口：`app/src/App.tsx`。

| 路由 | 页面 |
|---|---|
| `/login` | 登录 |
| `/` | 工作台 |
| `/profile` | 个人资料 |
| `/settings` | 个人设置 |
| `/agents` | Agent 列表 |
| `/agents/create` | 创建 Agent |
| `/agents/:id` | Agent 详情 |
| `/agents/:id/edit` | 编辑 Agent |
| `/agents/:id/test` | Agent 测试 |
| `/agents/:id/versions` | Agent 版本 |
| `/agents/:id/monitor` | Agent 监控 |
| `/models` | 模型列表 |
| `/models/providers` | 模型供应商 |
| `/prompts` | Prompt 列表 |
| `/prompts/create` | 创建 Prompt |
| `/prompts/:id` | 编辑 Prompt |
| `/prompts/:id/versions` | Prompt 版本 |
| `/knowledge` | 知识库列表 |
| `/knowledge/create` | 创建知识库 |
| `/knowledge/:id` | 知识库详情 |
| `/knowledge/:id/documents` | 文档管理 |
| `/knowledge/:id/segments` | 分段管理 |
| `/knowledge/:id/test` | 检索测试 |
| `/tools` | 工具列表 |
| `/tools/create` | 注册工具 |
| `/tools/:id` | 工具详情 |
| `/conversations` | 对话列表 |
| `/conversations/:id` | 对话详情 |
| `/analytics` | 用量统计 |
| `/analytics/costs` | 费用分析 |
| `/analytics/evaluation` | 效果评估 |
| `/system/users` | 用户管理 |
| `/system/roles` | 角色管理 |
| `/system/permissions` | 权限管理 |
| `/system/api-keys` | API Key 管理 |
| `/system/audit` | 审计日志 |
| `/system/alerts` | 告警 |
| `/system/settings` | 系统配置 |

### 4.3 布局和登录保护

- `DashboardLayout`：
  - 左侧导航：工作台、Agent、模型、Prompt、知识库、工具、对话、统计、系统设置。
  - 顶部面包屑、用户菜单、退出登录。
- `AuthGuard`：
  - 只检查 `localStorage` 中是否有 `access_token`。
  - 不调用后端校验 token 是否有效。
  - 没有 token 时跳转 `/login`。

### 4.4 服务层和 Mock/API 切换

核心文件：

- `app/src/services/config.ts`
- `app/src/services/api/client.ts`
- `app/src/services/mock/*`
- `app/src/services/<module>.ts`

切换逻辑：

```ts
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
```

每个模块有统一包装：

```ts
export const agentService = USE_MOCK ? mockAgentService : apiAgentService
```

因此：

- 默认 `USE_MOCK=true`。
- 页面不应该直接 import Mock 数据；应通过 `*Service`。
- 系统管理页面 `Users/Roles/Permissions` 目前是例外：页面内部直接根据 `USE_MOCK` 分支调用 `mockSystemService` 或 `apiSystemService`。

### 4.5 API 客户端

`apiClient` 提供：

- `get(path, { params })`
- `post(path, body)`
- `put(path, body)`
- `delete(path)`
- 自动附带 `Authorization: Bearer <token>`
- 自动解包 `json.data`
- 业务错误码检查
- HTTP 401 时清除 token 并跳转登录

当前限制：

- `post` 只接收 2 个参数，不能传自定义 headers。
- `get` 只支持 `params`，不支持 `responseType: 'blob'`。
- 因此知识库上传、统计导出、对话导出等真实 API 实现会存在类型错误或功能缺失。

### 4.6 前端业务类型

类型目录：`app/src/services/types/`。

主要实体：

| 文件 | 实体 |
|---|---|
| `agent.ts` | Agent、AgentConfig、AgentVersion、AgentStats |
| `model.ts` | Model、ModelProvider |
| `prompt.ts` | Prompt、PromptVariable、PromptVersion |
| `knowledge.ts` | KnowledgeBase、Document、Segment、RetrievalResult |
| `tool.ts` | Tool、ToolDetail、HttpApiConfig、FunctionDefinition |
| `conversation.ts` | Conversation、ConversationTurn、TraceStep、Annotation |
| `analytics.ts` | 用量、费用、效果评估 |
| `dashboard.ts` | 工作台统计、趋势、排行、告警、资源 |
| `system.ts` | User、Role、Permission、ApiKey、AuditLog、Alert、SystemSettings |
| `common.ts` | ApiResponse、PaginatedResponse、分页参数 |

---

## 5. 当前功能状态矩阵

| 模块 | 后端 | 前端页面 | 真实 API 可联调性 |
|---|---|---|---|
| 登录/验证码 | 已实现 | 已实现 | 基本可用，但需要 Redis 和已初始化用户；CORS 已配置 |
| 工作台 | 无 | Mock | 不可用 |
| Agent 管理 | 无 | Mock | 不可用 |
| 模型管理 | 无 | Mock | 不可用 |
| Prompt 管理 | 无 | Mock | 不可用 |
| 知识库 | 无 | Mock | 不可用 |
| 工具管理 | 无 | Mock | 不可用 |
| 对话日志 | 无 | Mock | 不可用 |
| 数据统计 | 无 | Mock | 不可用 |
| 系统-用户 | 部分 | 有真实 API 分支 | 部分接口路径/参数不匹配 |
| 系统-角色 | 部分 | 有真实 API 分支 | 列表路径和返回结构不匹配 |
| 系统-权限 | 部分 | 有真实 API 分支 | 列表路径和返回结构不匹配 |
| 系统-API Key | 无 | Mock | 非 Mock 模式会调用不存在的方法 |
| 系统-审计 | 无 | Mock | 非 Mock 模式会调用不存在的方法 |
| 系统-告警 | 无 | Mock | 非 Mock 模式会调用不存在的方法 |
| 系统-配置 | 无 | Mock | 非 Mock 模式会调用不存在的方法 |

---

## 6. 已知问题和技术债

以下问题按优先级排列。接手后不要假设“页面能打开”等于“功能已完成”。

### P0：会直接阻塞真实联调

#### 1. CORS 已配置

后端已在 `src/main.py` 配置 `CORSMiddleware`，只允许固定前端端口：

- `http://localhost:5173`
- `http://127.0.0.1:5173`

`app/vite.config.ts` 已设置 `server.port = 5173` 和 `strictPort = true`，Vite 不会再自动切换端口。如果 5173 被占用，Vite 会直接报错退出。
#### 2. 系统管理接口已对齐

- 后端新增 `/users/search`、`/roles/search`、`/permissions/search` 兼容路由。
- 新增 `DELETE /users/{id}`。
- `GET /users/{id}` 返回 `roles`。
- `PUT /users/{id}/roles` 接收 `{"role_ids": [...]}`。
- 前端 `getRoles()`/`getPermissions()` 解包 `PageResult.items`。
#### 3. API 基础路径已统一

`app/src/services/config.ts` 默认 `API_BASE` 已改为 `http://localhost:8000/api/v1`。Agent、模型、Prompt 等未来模块的 `/agents`、`/models` 会请求 `/api/v1/...`；这些业务模块本身后端仍未实现。
#### 4. 前端存在类型/构建风险

静态阅读可确认：

- `apiClient.post` 只接收 2 个参数，但 `knowledge.ts` 上传文档传了 3 个参数。
- `apiClient.get` 的 options 只支持 `params`，但统计导出/对话导出传了 `responseType: 'blob'`。
- `systemService` 在非 Mock 模式下会切换到 `apiSystemService`，但后者没有 `getApiKeys`、`getAuditLogs`、`getSystemAlerts`、`getSettings` 等方法。
- Mock 服务返回 `{data, total, page, pageSize}`，类型 `PaginatedResponse` 却定义成 `{code, message, data: {items...}}`，两者不一致。

建议：

- 首次接手先运行 `npm run build`，记录完整 TypeScript 错误。
- 不要为了让 build 通过而盲目加 `any`；应统一响应类型和客户端能力。

### P1：功能缺失

- 后端没有 Agent、模型、Prompt、知识库、工具、对话、统计、工作台模块。
- 没有 API Key、审计、告警、系统配置的后端实现。
- 已提供 `scripts/seed_rbac.py`，但数据库需要手动初始化管理员。
- 没有有效的后端测试。
- 前端部分页面仍是静态展示或占位保存。

### P2：安全和工程规范

- JWT 密钥已迁移到 `.env` 的 `JWT_SECRET_KEY`。
- 用户、角色、权限 CRUD 已要求 JWT 登录。
- 已按 `system:user`、`system:role`、`system:permission` 校验权限；`is_superuser` 直接放行。
- 前端 `AuthGuard` 仍只检查 token 是否存在，但 `apiClient` 已处理业务 401 并清理 token。
- MinIO 已配置但未使用。
- `app/README.md` 和部分设计文档的版本信息已过时。
- `is_superuser` 迁移是 `nullable=False` 且无默认值，如果 `users` 表已有数据，新增列可能失败；执行迁移前先检查数据。

---

## 7. 修改指南

### 7.1 新增后端模块的标准步骤

以新增 `agent` 模块为例：

1. 创建目录：

```text
src/modules/agent/
├─ __init__.py
├─ model.py
├─ schema.py
├─ repository.py
├─ service.py
└─ api.py
```

2. `model.py` 继承 `src.core.base_model.BaseModel`。
3. `schema.py` 定义 Create/Update/Read，ORM 读取模型加：

```python
model_config = {"from_attributes": True}
```

4. `repository.py` 继承 `BaseRepository`，必要时重写搜索字段。
5. `service.py` 处理业务规则，抛 `BizException`。
6. `api.py` 定义 `APIRouter`，使用 `ResponseSchema`、`PageResult`、`PageParams`。
7. 在 `src/main.py` 注册：

```python
from src.modules.agent.api import router as agent_router
app.include_router(agent_router, prefix="/api/v1")
```

8. 在 `alembic/env.py` 导入模型，确保 Alembic 能发现表。
9. 生成并检查迁移：

```powershell
alembic revision --autogenerate -m "add agent tables"
alembic upgrade head
```

10. 加登录依赖和权限校验，参考现有的 `require_any_permission`。

### 7.2 新增前端模块/页面的标准步骤

1. 在 `app/src/services/types/` 增加类型。
2. 在 `app/src/services/mock/` 增加 Mock 实现和 `mock/data/` 数据。
3. 在 `app/src/services/api/` 增加真实 API 实现，统一使用 `/v1/...`。
4. 在 `app/src/services/<module>.ts` 增加：

```ts
export const xxxService = USE_MOCK ? mockXxxService : apiXxxService
```

5. 在 `app/src/pages/<module>/` 新建页面。
6. 在 `pages/<module>/index.ts` 导出。
7. 在 `app/src/App.tsx` 注册路由。
8. 如果是顶级菜单，在 `DashboardLayout.tsx` 增加导航项。
9. 在 Mock 和真实 API 两种模式下分别验证。

### 7.3 接口契约约定

新增接口时统一遵守：

- 成功响应：`ResponseSchema`
- 分页：`PageResult`，字段为 `items/total/page/page_size`
- 业务错误：抛 `BizException`
- 认证：`Authorization: Bearer <token>`
- 前端 API 路径：`/<resource>`，因为 `API_BASE` 默认已包含 `/api/v1`
- 后端路由：`prefix="/api/v1"` + 模块 router
- 时间字段：ISO 8601 字符串
- 主键：整数 ID
- 分页参数：`page`、`page_size`、`keyword`

### 7.4 不要随意做的事情

- 不要删除 `docker/mysql/data`、`docker/redis/data`、`docker/minio/data`。
- 不要提交 `.env`。
- 不要执行 `git reset --hard`，当前工作区可能有未提交修改。
- 不要把 Mock 数据直接写进页面组件。
- 不要只改后端不检查前端调用路径。
- 不要只改前端不检查后端响应结构。
- 不要在没有测试的情况下声称“功能完成”。

---

## 8. 测试和验收

### 8.1 后端

当前 `test/` 基本为空。建议至少补充：

- 验证码生成/过期/一次性校验。
- 登录成功、密码错误、账号禁用、验证码错误。
- 用户创建、分页、详情、分配角色。
- 角色 CRUD、分配权限。
- 权限 CRUD。
- 未登录访问受保护接口应返回 401 业务码。
- 有权限/无权限访问应区分。

运行：

```powershell
cd D:\python\project\Karry_agent
pytest -q
```

注意：测试需要可用的 MySQL/Redis，或使用测试数据库和 fakeredis。

### 8.2 前端

当前没有测试框架，只能：

```powershell
cd D:\python\project\Karry_agent\app
npm run lint
npm run build
```

但当前 `npm run build` 预计会因类型问题失败，先按第 6 节修复。

### 8.3 手工验收清单

真实后端联调前：

1. `GET /health` 返回 `{"status":"ok"}`。
2. `GET /api/v1/captcha` 返回 key 和 base64 图片。
3. 创建用户成功。
4. 登录成功并拿到 `access_token`。
5. 带 Bearer Token 请求 `/api/v1/users/me` 成功。
6. 创建角色、创建权限、给角色分配权限、给用户分配角色成功。
7. 前端 Mock 模式下所有页面可打开。
8. 前端真实模式下登录、用户列表、角色列表、权限列表可用。
9. 确认浏览器 Network 面板无跨域错误。
10. 修复契约后，用户/角色/权限页面的增删改查无控制台错误。

---

## 9. 推荐阅读顺序

给第一次接手项目的 AI/工程师：

1. 本文件 `PROJECT_GUIDE.md`。
2. `src/main.py`：知道后端注册了哪些路由。
3. `src/core/`：配置、数据库、响应、异常、依赖。
4. `src/modules/auth`、`captcha`、`user`、`role`、`permission`：现有后端实现。
5. `app/src/App.tsx`：前端页面全貌。
6. `app/src/services/config.ts` 和 `app/src/services/api/client.ts`：Mock/API 切换和请求封装。
7. `app/src/services/api/system.ts`：当前最接近真实后端的接口层。
8. `app/src/pages/system/Users.tsx`、`Roles.tsx`、`Permissions.tsx`：真实 API 分支和当前契约问题。
9. `app/docs/00-架构总览.md`、`app/docs/10-API接口规范.md`：设计意图；注意部分内容已过时。
10. 最后再看目标业务模块的页面和 Mock 数据。

---

## 10. 附录

### 10.1 端口和环境变量

| 项目 | 值 |
|---|---|
| 后端 | `http://localhost:8000` |
| 前端 Vite | `http://localhost:5173` |
| MySQL | `127.0.0.1:3307` |
| Redis | `127.0.0.1:6379` |
| MinIO API | `127.0.0.1:9000` |
| MinIO Console | `127.0.0.1:9001` |
| 数据库名 | `chenguang` |
| 前端 Mock | `VITE_USE_MOCK=true`（默认） |
| 前端 API 地址 | `VITE_API_BASE=http://localhost:8000/api/v1` |

### 10.2 当前 Mock 登录行为

- 任意非空用户名 + 任意非空密码可登录。
- 验证码由前端本地生成并显示。
- 登录后 token 存在 `localStorage.access_token`。
- Mock 用户信息存在 `localStorage.user`。

### 10.3 当前 Git 历史

```text
68fdb03 RBAC基础功能实现
051d00c 无
b8e4810 无
```

说明：当前仓库提交历史很短，`RBAC基础功能实现` 是主要基线；不要根据提交信息判断所有功能都已完成。

---

## 11. 一句话交接

> 这是一个“前端页面和 Mock 数据很完整、后端只完成登录/验证码和 RBAC 基础接口”的项目。  
> 接手时先保证 Mock 模式可运行，再验证 CORS 和系统管理接口契约，最后按模块补 Agent、模型、Prompt、知识库、工具、对话和统计后端。