# Project Management — Technical Design

## Architecture Decisions

### 1. 后端：遵循现有三层泛型模式

完全复用 `CRUDBase` + `CRUDRouter` 泛型架构，与 `User` 实体保持一致：

```
app/models/project.py    → SQLAlchemy Model
app/schemas/project.py   → Pydantic Schema (Create/Update/Response)
app/crud/project.py      → CRUDProject(CRUDBase[Project, Create, Update])
app/api/v1/endpoints/projects.py → 手写路由（同 users.py 风格）
```

**决策理由**: 项目没有类似 User 的 authenticate/get_by_email 特殊逻辑，直接继承 CRUDBase 即可。路由参照 users.py 手写风格（非 CRUDRouter 自动生成），保持一致性。

### 2. 数据库：SQLite 兼容 + Alembic 迁移

- `extend_json` 使用 `Text` 类型存储 JSON 字符串（SQLite 兼容）
- `llm_key` / `lvm_key` 列名避用 `key` 以避免 MySQL 关键字冲突（向前兼容）
- `created_at` 使用 `server_default=func.now()`，`updated_at` 使用 `onupdate=func.now()`

### 3. 前端：独立项目管理页面

新增 `views/Project.vue`：
- 卡片网格布局，复用 Home.vue 的设计语言（圆角、阴影、渐变色）
- Element Plus `el-dialog` 做新建/编辑弹窗
- 项目卡片显示：名称、描述（截断）、LLM/LVM 模型名、创建时间
- 卡片 hover 效果与 Home.vue action-card 一致

### 4. 路由设计

```
/projects → Project.vue（项目管理页面）
```

从首页"创建代理"卡片点击跳转到 `/projects`。

### 5. API 服务层

新增 `api/project.ts`，封装项目 CRUD 接口，风格与 `api/user.ts` 一致。

## Risk Assessment

- **低风险**: 完全遵循现有模式，无架构变更
- **兼容性**: extend_json 用 Text 存储，SQLite/MySQL 均兼容
- **设计一致性**: 复用现有 SCSS 变量和动画
