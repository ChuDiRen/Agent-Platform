"""用户接口测试。

每个测试用例严格对应后端代码中的实际业务逻辑：
- 注册：邮箱唯一性检查（users.py:13-15）、邮箱格式校验（EmailStr）
- 登录：邮箱+密码认证 + is_active 检查（crud/user.py:24-30）
- 更新：exclude_unset=True 部分更新（base.py:36）+ 邮箱唯一性（users.py:35-38）
- 删除：标准删除（users.py:40-45）
"""

import pytest


# ============================================================
# POST /api/v1/users/ — 注册
# ============================================================

@pytest.mark.users
class TestCreateUser:
    """注册接口测试。覆盖 users.py:create_user 中的业务逻辑。"""

    def test_success(self, client):
        """正常注册应返回用户信息，密码不暴露。"""
        resp = client.post("/api/v1/users/", json={
            "email": "zhangsan@company.com",
            "password": "MySecurePass123!",
            "full_name": "张三",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "zhangsan@company.com"
        assert data["full_name"] == "张三"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_full_name_optional(self, client):
        """full_name 是可选字段（UserCreate 继承 UserBase，full_name 默认 None）。"""
        resp = client.post("/api/v1/users/", json={
            "email": "lisi@example.com",
            "password": "StrongPass456!",
        })
        assert resp.status_code == 200
        assert resp.json()["full_name"] is None

    def test_duplicate_email_rejected(self, client):
        """重复邮箱应返回 400（users.py:13-15 get_by_email 检查）。"""
        client.post("/api/v1/users/", json={
            "email": "wangwu@company.com",
            "password": "Pass123!",
        })
        resp = client.post("/api/v1/users/", json={
            "email": "wangwu@company.com",
            "password": "AnotherPass!",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    @pytest.mark.parametrize("payload", [
        {"password": "Pass123!"},                    # 缺 email
        {"email": "test@example.com"},               # 缺 password
        {},                                           # 空 body
    ], ids=["no_email", "no_password", "empty"])
    def test_missing_required_fields(self, client, payload):
        """缺少必填字段应返回 422（Pydantic 校验 UserCreate）。"""
        resp = client.post("/api/v1/users/", json=payload)
        assert resp.status_code == 422

    def test_invalid_email_format(self, client):
        """无效邮箱格式应返回 422（EmailStr 校验）。"""
        resp = client.post("/api/v1/users/", json={
            "email": "not-an-email",
            "password": "Pass123!",
        })
        assert resp.status_code == 422


# ============================================================
# POST /api/v1/users/login — 登录
# ============================================================

@pytest.mark.users
@pytest.mark.auth
class TestLogin:
    """登录接口测试。覆盖 users.py:login 中的认证逻辑。"""

    def test_success(self, client):
        """正确邮箱密码应返回 access_token 和用户信息。"""
        client.post("/api/v1/users/", json={
            "email": "loginuser@company.com",
            "password": "MyPassword123!",
            "full_name": "登录用户",
        })
        resp = client.post("/api/v1/users/login", json={
            "email": "loginuser@company.com",
            "password": "MyPassword123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "loginuser@company.com"
        assert data["user"]["full_name"] == "登录用户"

    def test_wrong_password(self, client):
        """错误密码应返回 401（users.py:50-51 authenticate 失败）。"""
        client.post("/api/v1/users/", json={
            "email": "wrongpw@company.com",
            "password": "CorrectPass123!",
        })
        resp = client.post("/api/v1/users/login", json={
            "email": "wrongpw@company.com",
            "password": "WrongPass456!",
        })
        assert resp.status_code == 401
        assert "错误" in resp.json()["detail"]

    def test_nonexistent_email(self, client):
        """不存在的邮箱应返回 401（authenticate 返回 None）。"""
        resp = client.post("/api/v1/users/login", json={
            "email": "nonexistent@company.com",
            "password": "AnyPass123!",
        })
        assert resp.status_code == 401

    def test_inactive_user_rejected(self, client):
        """is_active=False 的用户应无法登录（crud/user.py:29 检查）。"""
        # 注册
        client.post("/api/v1/users/", json={
            "email": "inactive@company.com",
            "password": "Pass123!",
        })
        # 获取用户 ID 并禁用
        users = client.get("/api/v1/users/").json()
        user_id = next(u["id"] for u in users if u["email"] == "inactive@company.com")
        client.put(f"/api/v1/users/{user_id}", json={
            "email": "inactive@company.com",
            "is_active": False,
        })
        # 尝试登录
        resp = client.post("/api/v1/users/login", json={
            "email": "inactive@company.com",
            "password": "Pass123!",
        })
        assert resp.status_code == 401

    @pytest.mark.parametrize("payload", [
        {"email": "test@example.com"},               # 缺 password
        {"password": "Pass123!"},                     # 缺 email
        {},                                           # 空 body
    ], ids=["no_password", "no_email", "empty"])
    def test_missing_fields(self, client, payload):
        """缺少字段应返回 422（Pydantic 校验 LoginRequest）。"""
        resp = client.post("/api/v1/users/login", json=payload)
        assert resp.status_code == 422


# ============================================================
# GET /api/v1/users/ — 用户列表
# ============================================================

@pytest.mark.users
class TestReadUsers:
    """用户列表测试。覆盖 users.py:read_users 的分页逻辑。"""

    def test_empty_list(self, client):
        """无用户时应返回空列表。"""
        assert client.get("/api/v1/users/").json() == []

    def test_returns_all_users(self, client):
        """应返回所有已注册用户。"""
        for i in range(3):
            client.post("/api/v1/users/", json={
                "email": f"user{i}@company.com",
                "password": "Pass123!",
            })
        resp = client.get("/api/v1/users/")
        assert len(resp.json()) == 3

    @pytest.mark.parametrize("params,expected", [
        ({"skip": 2}, 3),       # 跳过前 2 条
        ({"limit": 2}, 2),      # 限制返回 2 条
        ({"skip": 1, "limit": 2}, 2),  # 组合
    ], ids=["skip", "limit", "skip+limit"])
    def test_pagination(self, client, params, expected):
        """skip/limit 分页应正确工作（users.py:28 get_multi 参数）。"""
        for i in range(5):
            client.post("/api/v1/users/", json={
                "email": f"page{i}@company.com",
                "password": "Pass123!",
            })
        resp = client.get("/api/v1/users/", params=params)
        assert len(resp.json()) == expected


# ============================================================
# GET /api/v1/users/{user_id} — 获取单个用户
# ============================================================

@pytest.mark.users
class TestReadUser:
    """获取单个用户测试。覆盖 users.py:read_user。"""

    def test_success(self, client):
        """按 ID 获取已存在的用户应成功。"""
        create_resp = client.post("/api/v1/users/", json={
            "email": "single@company.com",
            "password": "Pass123!",
            "full_name": "单个用户",
        })
        user_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["email"] == "single@company.com"
        assert resp.json()["full_name"] == "单个用户"

    def test_not_found(self, client):
        """不存在的用户应返回 404（users.py:22-23）。"""
        resp = client.get("/api/v1/users/99999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"


# ============================================================
# PUT /api/v1/users/{user_id} — 更新用户
# ============================================================

@pytest.mark.users
class TestUpdateUser:
    """更新用户测试。覆盖 users.py:update_user + base.py:update（exclude_unset=True）。"""

    def test_update_full_name(self, client):
        """更新 full_name 应成功。"""
        create_resp = client.post("/api/v1/users/", json={
            "email": "update@company.com",
            "password": "Pass123!",
            "full_name": "旧名字",
        })
        user_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/users/{user_id}", json={
            "email": "update@company.com",
            "full_name": "新名字",
        })
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "新名字"

    def test_update_email(self, client):
        """更新 email 应成功。"""
        create_resp = client.post("/api/v1/users/", json={
            "email": "old@company.com",
            "password": "Pass123!",
        })
        user_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/users/{user_id}", json={
            "email": "new@company.com",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "new@company.com"

    def test_partial_update_preserves_unset_fields(self, client):
        """部分更新只修改传入字段，其他不变（base.py:36 exclude_unset=True）。"""
        create_resp = client.post("/api/v1/users/", json={
            "email": "partial@company.com",
            "password": "Pass123!",
            "full_name": "保持不变",
        })
        user_id = create_resp.json()["id"]

        # 只传 email，不传 full_name
        resp = client.put(f"/api/v1/users/{user_id}", json={
            "email": "changed@company.com",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "changed@company.com"
        assert resp.json()["full_name"] == "保持不变"

    def test_not_found(self, client):
        """更新不存在的用户应返回 404（users.py:35-36）。"""
        resp = client.put("/api/v1/users/99999", json={
            "email": "ghost@company.com",
        })
        assert resp.status_code == 404

    def test_duplicate_email_rejected(self, client):
        """更新邮箱为已存在邮箱应返回 400（users.py:35-38 唯一性检查）。"""
        client.post("/api/v1/users/", json={
            "email": "taken@company.com",
            "password": "Pass123!",
        })
        create_resp = client.post("/api/v1/users/", json={
            "email": "updater@company.com",
            "password": "Pass123!",
        })
        user_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/users/{user_id}", json={
            "email": "taken@company.com",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()


# ============================================================
# DELETE /api/v1/users/{user_id} — 删除用户
# ============================================================

@pytest.mark.users
class TestDeleteUser:
    """删除用户测试。覆盖 users.py:delete_user。"""

    def test_success(self, client):
        """删除已存在的用户应返回被删用户信息。"""
        create_resp = client.post("/api/v1/users/", json={
            "email": "delete@company.com",
            "password": "Pass123!",
        })
        user_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["email"] == "delete@company.com"

        # 确认已删除
        assert client.get(f"/api/v1/users/{user_id}").status_code == 404

    def test_not_found(self, client):
        """删除不存在的用户应返回 404（users.py:42-43）。"""
        resp = client.delete("/api/v1/users/99999")
        assert resp.status_code == 404


# ============================================================
# 完整 CRUD 流程集成测试
# ============================================================

@pytest.mark.users
@pytest.mark.integration
class TestCRUDLifecycle:
    """注册 → 查询 → 登录 → 更新 → 删除 完整流程。"""

    def test_full_lifecycle(self, client):
        """验证所有接口串联工作。"""
        # 1. 注册
        create_resp = client.post("/api/v1/users/", json={
            "email": "lifecycle@company.com",
            "password": "LifecyclePass123!",
            "full_name": "生命周期用户",
        })
        assert create_resp.status_code == 200
        user_id = create_resp.json()["id"]

        # 2. 查询
        get_resp = client.get(f"/api/v1/users/{user_id}")
        assert get_resp.json()["email"] == "lifecycle@company.com"

        # 3. 登录
        login_resp = client.post("/api/v1/users/login", json={
            "email": "lifecycle@company.com",
            "password": "LifecyclePass123!",
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 4. 更新
        update_resp = client.put(f"/api/v1/users/{user_id}", json={
            "email": "lifecycle@company.com",
            "full_name": "更新后",
        })
        assert update_resp.json()["full_name"] == "更新后"

        # 5. 删除
        assert client.delete(f"/api/v1/users/{user_id}").status_code == 200
        assert client.get(f"/api/v1/users/{user_id}").status_code == 404
