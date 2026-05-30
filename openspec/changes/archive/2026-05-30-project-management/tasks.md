# Project Management — Tasks

## Backend

- [x] 1. 创建 `app/models/project.py` — SQLAlchemy Project 模型
- [x] 2. 创建 `app/schemas/project.py` — Pydantic Schema (ProjectBase/ProjectCreate/ProjectUpdate/Project)
- [x] 3. 创建 `app/crud/project.py` — CRUDProject 继承 CRUDBase
- [x] 4. 创建 `app/api/v1/endpoints/projects.py` — CRUD 路由
- [x] 5. 在 `app/db/base.py` 导入 Project 模型
- [x] 6. 在 `app/main.py` 注册 projects 路由
- [x] 7. 生成 Alembic 迁移并执行

## Frontend

- [x] 8. 创建 `src/api/project.ts` — 项目 API 封装
- [x] 9. 创建 `src/views/Project.vue` — 卡片式项目管理页面
- [x] 10. 更新 `src/router/index.ts` — 添加 /projects 路由
- [x] 11. 更新 `src/views/Home.vue` — "创建代理"卡片跳转到 /projects

## Verification

- [x] 12. 后端模型/Schema/CRUD/路由导入验证通过
- [x] 13. 前端 TypeScript 类型检查通过
