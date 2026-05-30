# Project Management Feature

## Why

Agent-Platform 目前缺少项目级别的资源隔离和配置管理能力。用户需要将不同的 Agent 工作按"项目"维度组织，每个项目可独立配置 LLM/LVM 模型参数（URL、Key、Model），实现多项目并行管理和资源隔离。

## What

### 功能范围

1. **后端 API** — 完整的项目 CRUD 接口，遵循现有三层泛型架构（Model → Schema → CRUDBase → CRUDRouter）
2. **前端页面** — 卡片式项目列表，支持创建、编辑、删除项目
3. **数据库** — Project 表，含 LLM/LVM 配置字段、密码保护、扩展 JSON

### 数据库字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer, PK | 主键 |
| name | String(255), NOT NULL | 项目名称 |
| description | Text | 项目描述 |
| password | String(255) | 项目密码 |
| llm_url | String(255) | LLM 服务地址 |
| llm_key | String(255) | LLM API Key |
| llm_model | String(255) | LLM 模型名 |
| lvm_url | String(255) | LVM 服务地址 |
| lvm_key | String(255) | LVM API Key |
| lvm_model | String(255) | LVM 模型名 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| extend_json | Text | 扩展 JSON |

### 用户交互

- 首页快速操作区域的"创建代理"卡片点击后进入项目管理页
- 项目以卡片形式展示，每张卡片显示项目名称、描述、创建时间
- 支持新建项目对话框（含 LLM/LVM 配置表单）
- 支持编辑和删除操作

## Acceptance Criteria

- [ ] 后端 `POST /api/v1/projects/` 创建项目
- [ ] 后端 `GET /api/v1/projects/` 获取项目列表
- [ ] 后端 `GET /api/v1/projects/{id}` 获取单个项目
- [ ] 后端 `PUT /api/v1/projects/{id}` 更新项目
- [ ] 后端 `DELETE /api/v1/projects/{id}` 删除项目
- [ ] 前端项目管理页面，卡片式布局
- [ ] 新建/编辑项目对话框，含完整表单
- [ ] Alembic 迁移脚本
- [ ] 与现有设计主题一致（白色风格、蓝紫渐变）
