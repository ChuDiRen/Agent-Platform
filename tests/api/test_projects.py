"""Project 项目 API 测试。

覆盖 CRUD 全流程 + 边界场景 + 密码安全（哈希存储、不回传、服务端校验）。
"""
import pytest


PROJECT_BASE = "/api/v1/projects/"


def _make_project(**overrides):
    """构造 Project 创建数据。"""
    data = {
        "name": "测试项目",
        "description": "测试描述",
        "password": "",
        "llm_url": "https://token-plan-sgp.xiaomimimo.com/v1",
        "llm_model": "mimo-v2.5-pro",
    }
    data.update(overrides)
    return data


@pytest.mark.smoke
class TestProjectCreate:
    """创建项目。"""

    def test_create_project_success(self, client):
        resp = client.post(PROJECT_BASE, json=_make_project())
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert body["name"] == "测试项目"
        assert body["id"] > 0

    def test_create_project_minimal(self, client):
        resp = client.post(PROJECT_BASE, json={"name": "最小项目"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "最小项目"

    def test_create_project_missing_name(self, client):
        resp = client.post(PROJECT_BASE, json={"description": "无名称"})
        assert resp.status_code == 422

    def test_create_project_with_password(self, client):
        resp = client.post(PROJECT_BASE, json=_make_project(password="abc123"))
        assert resp.status_code == 200
        body = resp.json()["data"]
        # 密码绝不明文回传，只暴露 has_password 标记
        assert "password" not in body
        assert body["has_password"] is True

    def test_create_project_with_model_config(self, client):
        resp = client.post(PROJECT_BASE, json=_make_project(
            lvm_url="https://token-plan-sgp.xiaomimimo.com/v1",
            lvm_model="mimo-v2.5",
        ))
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert body["lvm_model"] == "mimo-v2.5"


@pytest.mark.smoke
class TestProjectRead:
    """读取项目。"""

    def test_list_projects_empty(self, client):
        resp = client.get(PROJECT_BASE)
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_list_projects_multiple(self, client):
        client.post(PROJECT_BASE, json=_make_project(name="P1"))
        client.post(PROJECT_BASE, json=_make_project(name="P2"))
        resp = client.get(PROJECT_BASE)
        assert len(resp.json()["data"]) == 2

    def test_get_project_by_id(self, client):
        create_resp = client.post(PROJECT_BASE, json=_make_project())
        pid = create_resp.json()["data"]["id"]
        resp = client.get(f"{PROJECT_BASE}{pid}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == pid

    def test_get_project_not_found(self, client):
        resp = client.get(f"{PROJECT_BASE}99999")
        assert resp.json()["code"] == 404


class TestProjectUpdate:
    """更新项目。"""

    def test_update_project_name(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project()).json()["data"]["id"]
        resp = client.put(f"{PROJECT_BASE}{pid}", json={"name": "新项目名"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "新项目名"

    def test_update_project_model(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project()).json()["data"]["id"]
        resp = client.put(f"{PROJECT_BASE}{pid}", json={"llm_model": "mimo-v2.5-pro"})
        assert resp.status_code == 200
        assert resp.json()["data"]["llm_model"] == "mimo-v2.5-pro"

    def test_update_project_password(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project()).json()["data"]["id"]
        resp = client.put(f"{PROJECT_BASE}{pid}", json={"password": "newpass"})
        assert resp.status_code == 200
        body = resp.json()["data"]
        assert "password" not in body
        assert body["has_password"] is True

    def test_update_project_clear_password(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project(password="abc123")).json()["data"]["id"]
        resp = client.put(f"{PROJECT_BASE}{pid}", json={"password": ""})
        assert resp.status_code == 200
        assert resp.json()["data"]["has_password"] is False

    def test_update_project_not_found(self, client):
        resp = client.put(f"{PROJECT_BASE}99999", json={"name": "x"})
        assert resp.json()["code"] == 404


class TestProjectDelete:
    """删除项目。"""

    def test_delete_project(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project()).json()["data"]["id"]
        resp = client.delete(f"{PROJECT_BASE}{pid}")
        assert resp.status_code == 200
        assert client.get(f"{PROJECT_BASE}{pid}").json()["code"] == 404

    def test_delete_project_not_found(self, client):
        resp = client.delete(f"{PROJECT_BASE}99999")
        assert resp.json()["code"] == 404


class TestProjectPassword:
    """项目密码服务端校验。"""

    def test_verify_password_success(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project(password="secret123")).json()["data"]["id"]
        resp = client.post(f"{PROJECT_BASE}{pid}/verify-password", json={"password": "secret123"})
        assert resp.status_code == 200
        assert resp.json()["data"]["valid"] is True

    def test_verify_password_failure(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project(password="secret123")).json()["data"]["id"]
        resp = client.post(f"{PROJECT_BASE}{pid}/verify-password", json={"password": "wrong"})
        assert resp.status_code == 200
        assert resp.json()["data"]["valid"] is False

    def test_verify_password_no_password_set(self, client):
        pid = client.post(PROJECT_BASE, json=_make_project()).json()["data"]["id"]
        resp = client.post(f"{PROJECT_BASE}{pid}/verify-password", json={"password": "anything"})
        assert resp.status_code == 200
        assert resp.json()["data"]["valid"] is True


class TestProjectIsolation:
    """项目数据隔离：普通用户只能访问自己的项目。"""

    def test_user_cannot_read_others_project(self, client, login_headers, create_user_via_api):
        mine = client.post(PROJECT_BASE, json=_make_project(name="我的项目")).json()["data"]
        other = create_user_via_api(email="other@company.com", password="OtherPass123!")
        other_id = other.json()["data"]["id"]
        other_headers = login_headers("other@company.com", "OtherPass123!")

        # other 看不到我创建的项目
        resp = client.get(f"{PROJECT_BASE}{mine['id']}", headers=other_headers)
        assert resp.json()["code"] == 403

        # other 的列表里没有我的项目
        list_resp = client.get(PROJECT_BASE, headers=other_headers)
        assert list_resp.json()["data"] == []

        # other 不能改/删我的项目
        assert client.put(
            f"{PROJECT_BASE}{mine['id']}", headers=other_headers, json={"name": "hack"}
        ).json()["code"] == 403
        assert client.delete(f"{PROJECT_BASE}{mine['id']}", headers=other_headers).json()["code"] == 403

    def test_owner_can_manage_own_project(self, client):
        mine = client.post(PROJECT_BASE, json=_make_project(name="我的项目")).json()["data"]
        resp = client.put(f"{PROJECT_BASE}{mine['id']}", json={"name": "改名"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "改名"
