"""用户接口完整测试。

覆盖以下场景：
- 注册：成功、重复邮箱、缺失字段
- 登录：成功、密码错误、邮箱不存在
- 获取用户列表：基本查询、分页
- 获取单个用户：成功、404
- 更新用户：成功（全量/部分）、404
- 删除用户：成功、404
"""


# ============================================================
# 用户注册测试
# ============================================================

class TestCreateUser:
    """POST /api/v1/users/"""

    def test_create_user_success(self, client):
        """正常注册应返回 200 和用户信息。"""
        response = client.post(
            "/api/v1/users/",
            json={"email": "new@example.com", "password": "pass123456", "full_name": "New User"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        # 响应中不应包含密码
        assert "password" not in data
        assert "hashed_password" not in data

    def test_create_user_without_full_name(self, client):
        """full_name 是可选的，不传也应注册成功。"""
        response = client.post(
            "/api/v1/users/",
            json={"email": "noname@example.com", "password": "pass123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "noname@example.com"
        assert data["full_name"] is None

    def test_create_user_duplicate_email(self, client, create_user_via_api):
        """重复邮箱注册应返回 400。"""
        create_user_via_api(email="dup@example.com", password="pass123456")
        response = client.post(
            "/api/v1/users/",
            json={"email": "dup@example.com", "password": "anotherpass", "full_name": "Dup"},
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_create_user_missing_email(self, client):
        """缺少 email 字段应返回 422 校验错误。"""
        response = client.post(
            "/api/v1/users/",
            json={"password": "pass123456", "full_name": "No Email"},
        )
        assert response.status_code == 422

    def test_create_user_missing_password(self, client):
        """缺少 password 字段应返回 422 校验错误。"""
        response = client.post(
            "/api/v1/users/",
            json={"email": "nopass@example.com", "full_name": "No Pass"},
        )
        assert response.status_code == 422

    def test_create_user_empty_body(self, client):
        """空请求体应返回 422。"""
        response = client.post("/api/v1/users/", json={})
        assert response.status_code == 422

    def test_create_user_invalid_email_format(self, client):
        """无效邮箱格式（Pydantic v2 不默认校验 email 格式，但服务器应能处理）。
        注意：UserCreate schema 中 email 字段类型是 str 而非 EmailStr，
        所以不会自动校验格式。此测试确认行为一致性。"""
        response = client.post(
            "/api/v1/users/",
            json={"email": "not-an-email", "password": "pass123456"},
        )
        # 当前实现中 email 只是 str 类型，不校验格式，所以应该成功
        assert response.status_code == 200


# ============================================================
# 用户登录测试
# ============================================================

class TestLogin:
    """POST /api/v1/users/login"""

    def test_login_success(self, client, create_user_via_api):
        """正确邮箱密码登录应返回 access_token 和用户信息。"""
        create_user_via_api(email="login@example.com", password="mypassword")
        response = client.post(
            "/api/v1/users/login",
            json={"email": "login@example.com", "password": "mypassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login@example.com"
        assert "id" in data["user"]

    def test_login_wrong_password(self, client, create_user_via_api):
        """错误密码应返回 401。"""
        create_user_via_api(email="wrongpw@example.com", password="correctpass")
        response = client.post(
            "/api/v1/users/login",
            json={"email": "wrongpw@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "错误" in response.json()["detail"] or "error" in response.json()["detail"].lower()

    def test_login_nonexistent_email(self, client):
        """不存在的邮箱登录应返回 401。"""
        response = client.post(
            "/api/v1/users/login",
            json={"email": "noexist@example.com", "password": "whatever"},
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """缺少字段应返回 422。"""
        # 缺少 password
        response = client.post(
            "/api/v1/users/login",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

        # 缺少 email
        response = client.post(
            "/api/v1/users/login",
            json={"password": "test"},
        )
        assert response.status_code == 422

    def test_login_empty_body(self, client):
        """空请求体应返回 422。"""
        response = client.post("/api/v1/users/login", json={})
        assert response.status_code == 422


# ============================================================
# 获取用户列表测试
# ============================================================

class TestReadUsers:
    """GET /api/v1/users/"""

    def test_read_users_empty(self, client):
        """无用户时应返回空列表。"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_read_users_with_data(self, client, create_user_via_api):
        """有用户时应返回列表。"""
        create_user_via_api(email="user1@example.com", password="pass123456")
        create_user_via_api(email="user2@example.com", password="pass123456")
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails

    def test_read_users_pagination_skip(self, client, create_user_via_api):
        """skip 参数应跳过前 N 条记录。"""
        for i in range(5):
            create_user_via_api(email=f"page{i}@example.com", password="pass123456")
        response = client.get("/api/v1/users/?skip=2")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_read_users_pagination_limit(self, client, create_user_via_api):
        """limit 参数应限制返回数量。"""
        for i in range(5):
            create_user_via_api(email=f"limit{i}@example.com", password="pass123456")
        response = client.get("/api/v1/users/?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_read_users_pagination_skip_and_limit(self, client, create_user_via_api):
        """组合 skip 和 limit。"""
        for i in range(5):
            create_user_via_api(email=f"both{i}@example.com", password="pass123456")
        response = client.get("/api/v1/users/?skip=1&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


# ============================================================
# 获取单个用户测试
# ============================================================

class TestReadUser:
    """GET /api/v1/users/{user_id}"""

    def test_read_user_success(self, client, create_user_via_api):
        """按 ID 获取已存在的用户应成功。"""
        create_resp = create_user_via_api(email="single@example.com", password="pass123456", full_name="Single User")
        user_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "single@example.com"
        assert data["full_name"] == "Single User"

    def test_read_user_not_found(self, client):
        """获取不存在的用户应返回 404。"""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_read_user_invalid_id(self, client):
        """无效 ID 格式应返回 422。"""
        response = client.get("/api/v1/users/abc")
        assert response.status_code == 422


# ============================================================
# 更新用户测试
# ============================================================

class TestUpdateUser:
    """PUT /api/v1/users/{user_id}"""

    def test_update_user_full_name(self, client, create_user_via_api):
        """更新 full_name 应成功。"""
        create_resp = create_user_via_api(email="update@example.com", password="pass123456", full_name="Old Name")
        user_id = create_resp.json()["id"]
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "update@example.com", "full_name": "New Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "New Name"
        assert data["email"] == "update@example.com"

    def test_update_user_email(self, client, create_user_via_api):
        """更新 email 应成功。"""
        create_resp = create_user_via_api(email="old@example.com", password="pass123456")
        user_id = create_resp.json()["id"]
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "new@example.com"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"

    def test_update_user_is_active(self, client, create_user_via_api):
        """更新 is_active 应成功。"""
        create_resp = create_user_via_api(email="active@example.com", password="pass123456")
        user_id = create_resp.json()["id"]
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "active@example.com", "is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_update_user_not_found(self, client):
        """更新不存在的用户应返回 404。"""
        response = client.put(
            "/api/v1/users/99999",
            json={"email": "ghost@example.com"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_update_user_partial(self, client, create_user_via_api):
        """部分更新只修改指定字段，其他不变。"""
        create_resp = create_user_via_api(
            email="partial@example.com", password="pass123456", full_name="Partial"
        )
        user_id = create_resp.json()["id"]
        # 只更新 email，不传 full_name
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "changed@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "changed@example.com"
        # full_name 应保持不变
        assert data["full_name"] == "Partial"


# ============================================================
# 删除用户测试
# ============================================================

class TestDeleteUser:
    """DELETE /api/v1/users/{user_id}"""

    def test_delete_user_success(self, client, create_user_via_api):
        """删除已存在的用户应成功并返回被删用户信息。"""
        create_resp = create_user_via_api(email="delete@example.com", password="pass123456")
        user_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == "delete@example.com"

        # 确认已删除：再次获取应返回 404
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        """删除不存在的用户应返回 404。"""
        response = client.delete("/api/v1/users/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_delete_user_idempotency(self, client, create_user_via_api):
        """删除已删除的用户应返回 404（非幂等）。"""
        create_resp = create_user_via_api(email="idemp@example.com", password="pass123456")
        user_id = create_resp.json()["id"]
        # 第一次删除成功
        client.delete(f"/api/v1/users/{user_id}")
        # 第二次删除应返回 404
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 404


# ============================================================
# 完整 CRUD 流程集成测试
# ============================================================

class TestUserCRUDFlow:
    """完整的 CRUD 生命周期测试。"""

    def test_full_crud_lifecycle(self, client):
        """注册 → 查询 → 更新 → 删除 的完整流程。"""
        # 1. 注册
        create_resp = client.post(
            "/api/v1/users/",
            json={"email": "lifecycle@example.com", "password": "pass123456", "full_name": "Lifecycle User"},
        )
        assert create_resp.status_code == 200
        user_id = create_resp.json()["id"]

        # 2. 查询单个
        get_resp = client.get(f"/api/v1/users/{user_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["email"] == "lifecycle@example.com"

        # 3. 登录
        login_resp = client.post(
            "/api/v1/users/login",
            json={"email": "lifecycle@example.com", "password": "pass123456"},
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 4. 更新
        update_resp = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "lifecycle@example.com", "full_name": "Updated Lifecycle"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["full_name"] == "Updated Lifecycle"

        # 5. 确认更新生效
        verify_resp = client.get(f"/api/v1/users/{user_id}")
        assert verify_resp.json()["full_name"] == "Updated Lifecycle"

        # 6. 删除
        delete_resp = client.delete(f"/api/v1/users/{user_id}")
        assert delete_resp.status_code == 200

        # 7. 确认已删除
        gone_resp = client.get(f"/api/v1/users/{user_id}")
        assert gone_resp.status_code == 404

    def test_multiple_users_independent(self, client):
        """多个用户互不影响。"""
        ids = []
        for i in range(3):
            resp = client.post(
                "/api/v1/users/",
                json={"email": f"user{i}@example.com", "password": "pass123456", "full_name": f"User {i}"},
            )
            assert resp.status_code == 200
            ids.append(resp.json()["id"])

        # 删除中间的用户
        client.delete(f"/api/v1/users/{ids[1]}")

        # 其他用户仍然存在
        assert client.get(f"/api/v1/users/{ids[0]}").status_code == 200
        assert client.get(f"/api/v1/users/{ids[2]}").status_code == 200

        # 列表应只剩 2 个
        list_resp = client.get("/api/v1/users/")
        assert len(list_resp.json()) == 2
