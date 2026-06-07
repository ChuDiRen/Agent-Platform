---
name: api-automation-script
description: 接口自动化脚本技能。指导 Agent 生成可执行的 pytest + httpx 测试脚本。
---

# 接口自动化脚本技能

## 脚本规范

### 框架选型
- 测试框架: pytest
- HTTP 客户端: httpx (支持同步/异步)
- 断言: pytest 原生 assert

### 脚本结构
```python
import pytest
import httpx

BASE_URL = "http://localhost:8000"

class TestXxx:
    """xxx 模块测试套件"""

    def test_normal_case(self):
        """正向用例"""
        response = httpx.post(f"{BASE_URL}/api/...", json={...})
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 3

    def test_missing_param(self):
        """缺少必选参数"""
        response = httpx.post(f"{BASE_URL}/api/...", json={})
        assert response.status_code == 400
```

### 断言策略
1. 状态码断言 (必须)
2. 响应体结构断言 (必须)
3. 响应时间断言 (建议 < 3s)
4. 业务逻辑断言 (根据场景)

### 数据驱动
使用 pytest.mark.parametrize:
```python
@pytest.mark.parametrize("username,password,expected", [
    ("valid@test.com", "Test@123", 200),
    ("", "Test@123", 400),
    ("valid@test.com", "", 400),
])
def test_login(username, password, expected):
    ...
```

## 报告输出
使用 pytest-html 生成 HTML 报告。
