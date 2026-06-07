---
name: api-document-analysis
description: 接口文档分析技能。指导 Agent 提取端点、检查 RESTful 规范、发现安全和完整性问题。
---

# 接口文档分析技能

## 分析流程

### 1. 端点提取
调用 `extract_endpoints` 识别所有接口:
- HTTP 方法 (GET/POST/PUT/DELETE/PATCH)
- URL 路径和参数
- 请求体结构
- 响应体结构

### 2. 规范检查
调用 `check_api_compliance`:
- GET 不应有副作用 (写操作)
- URL 层级不超过 4 层
- 命名风格一致 (camelCase 或 snake_case)
- 状态码使用正确 (200/201/400/401/403/404/500)

### 3. 安全审查
调用 `analyze_api_document`:
- 是否有鉴权说明
- 是否有频率限制
- 是否有输入校验
- 敏感数据是否脱敏

## RESTful 检查清单

| 规则 | 说明 |
|------|------|
| 资源命名 | 使用名词复数 (users, orders) |
| HTTP 语义 | GET 读/POST 创建/PUT 全量更新/PATCH 部分更新/DELETE 删除 |
| 状态码 | 2xx 成功/4xx 客户端错/5xx 服务端错 |
| 分页 | 列表接口必须支持分页 (page, size) |
| 版本 | URL 或 Header 中包含 API 版本 |

## 输出格式
```json
{
  "endpoints": [{"method": "POST", "path": "/api/v1/users/login"}],
  "compliance_issues": [{"rule": "RESTful", "detail": "GET 请求不应执行写操作"}],
  "security_issues": [{"severity": "high", "title": "缺少鉴权说明"}],
  "suggestions": ["建议添加请求频率限制"]
}
```
