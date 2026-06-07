---
name: api-test-case-design
description: 接口用例设计技能。指导 Agent 为 API 设计全面的测试用例，覆盖参数组合、鉴权、幂等性。
---

# 接口用例设计技能

## 用例维度

### 正向用例
- 正常参数，预期 200/201
- 可选参数不传，返回默认值
- 边界参数 (最小值/最大值)

### 反向用例
- 缺少必选参数 → 400
- 参数类型错误 → 400
- 参数格式非法 → 400
- 资源不存在 → 404

### 鉴权用例
- 无 Token → 401
- Token 过期 → 401
- 无权限资源 → 403
- 越权操作 → 403

### 幂等用例
- 重复创建同一资源
- 重复删除已删资源
- 并发更新同一资源

## 断言模板

```json
[
  {"field": "status_code", "operator": "equals", "expected": 200},
  {"field": "$.data.id", "operator": "exists"},
  {"field": "$.data.created_at", "operator": "not_null"},
  {"field": "response_time", "operator": "less_than", "expected": "3000ms"}
]
```

## 参数组合矩阵
对每个参数列出: 正常值 / 空值 / 边界值 / 非法类型 / SQL注入 / XSS
组合时优先: 全正常 > 单参数异常 > 多参数异常
