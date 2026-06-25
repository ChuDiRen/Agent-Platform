"""Project 项目 API 测试。

覆盖 CRUD 全流程 + 边界场景。
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
        "llm_key": "sk-test",
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
        assert resp.json()["data"]["password"] == "abc123"

    def test_create_project_with_model_config(self, client):
        resp = client.post(PROJECT_BASE, json=_make_project(
            lvm_url="https://token-plan-sgp.xiaomimimo.com/v1",
            lvm_key="vk-test",
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
        assert resp.json()["data"]["password"] == "newpass"

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
