"""Agent 智能体 API 测试。

覆盖 CRUD 全流程 + 边界场景。
"""
import pytest


AGENT_BASE = "/api/v1/agents/"


def _make_agent(**overrides):
    """构造 Agent 创建数据。"""
    data = {
        "name": "测试智能体",
        "description": "这是一个测试智能体",
        "tags": '["标签A","标签B"]',
        "icon": "doc",
        "gradient": "linear-gradient(135deg, #3b82f6, #6366f1)",
        "sort_order": 1,
        "is_active": True,
        "is_placeholder": False,
    }
    data.update(overrides)
    return data


@pytest.mark.smoke
class TestAgentCreate:
    """创建智能体。"""

    def test_create_agent_success(self, client):
        resp = client.post(AGENT_BASE, json=_make_agent())
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "测试智能体"
        assert body["id"] > 0

    def test_create_placeholder_agent(self, client):
        resp = client.post(AGENT_BASE, json=_make_agent(
            name="占位智能体", is_placeholder=True, tags="[]"
        ))
        assert resp.status_code == 200
        assert resp.json()["is_placeholder"] is True

    def test_create_agent_missing_name(self, client):
        data = _make_agent()
        del data["name"]
        resp = client.post(AGENT_BASE, json=data)
        assert resp.status_code == 422


@pytest.mark.smoke
class TestAgentRead:
    """读取智能体。"""

    def test_list_agents_empty(self, client):
        resp = client.get(AGENT_BASE)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_agents_after_create(self, client):
        client.post(AGENT_BASE, json=_make_agent(name="A", sort_order=1))
        client.post(AGENT_BASE, json=_make_agent(name="B", sort_order=2))
        resp = client.get(AGENT_BASE)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_agent_by_id(self, client):
        create_resp = client.post(AGENT_BASE, json=_make_agent())
        agent_id = create_resp.json()["id"]
        resp = client.get(f"{AGENT_BASE}{agent_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == agent_id

    def test_get_agent_not_found(self, client):
        resp = client.get(f"{AGENT_BASE}99999")
        assert resp.status_code == 404


class TestAgentUpdate:
    """更新智能体。"""

    def test_update_agent_name(self, client):
        create_resp = client.post(AGENT_BASE, json=_make_agent())
        agent_id = create_resp.json()["id"]
        resp = client.put(f"{AGENT_BASE}{agent_id}", json={"name": "新名称"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_update_agent_tags(self, client):
        create_resp = client.post(AGENT_BASE, json=_make_agent())
        agent_id = create_resp.json()["id"]
        new_tags = '["新标签"]'
        resp = client.put(f"{AGENT_BASE}{agent_id}", json={"tags": new_tags})
        assert resp.status_code == 200
        assert resp.json()["tags"] == new_tags

    def test_update_agent_not_found(self, client):
        resp = client.put(f"{AGENT_BASE}99999", json={"name": "x"})
        assert resp.status_code == 404


class TestAgentDelete:
    """删除智能体。"""

    def test_delete_agent(self, client):
        create_resp = client.post(AGENT_BASE, json=_make_agent())
        agent_id = create_resp.json()["id"]
        resp = client.delete(f"{AGENT_BASE}{agent_id}")
        assert resp.status_code == 200
        # verify gone
        assert client.get(f"{AGENT_BASE}{agent_id}").status_code == 404

    def test_delete_agent_not_found(self, client):
        resp = client.delete(f"{AGENT_BASE}99999")
        assert resp.status_code == 404


class TestAgentSeedData:
    """验证种子数据能被正确写入和读取。"""

    SEED_NAMES = [
        "AI需求评估助手", "AI测试用例智能体", "AI界面UI自动化脚本",
        "AI接口文档分析", "AI接口用例设计助手", "AI接口自动化脚本助手",
        "AI测试数据生成智能体", "AI性能数据分析助手", "更多智能体即将上线",
    ]

    def _seed_all(self, client):
        """手动写入 9 条种子数据（模拟 startup 行为）。"""
        for i, name in enumerate(self.SEED_NAMES, 1):
            client.post(AGENT_BASE, json=_make_agent(
                name=name,
                sort_order=i,
                is_placeholder=(name == "更多智能体即将上线"),
                tags="[]" if name == "更多智能体即将上线" else '["标签"]',
            ))

    def test_seed_agents_count(self, client):
        self._seed_all(client)
        resp = client.get(AGENT_BASE)
        assert resp.status_code == 200
        assert len(resp.json()) == 9

    def test_seed_agent_names(self, client):
        self._seed_all(client)
        names = [a["name"] for a in client.get(AGENT_BASE).json()]
        assert "AI需求评估助手" in names
        assert "更多智能体即将上线" in names

    def test_placeholder_agent_flag(self, client):
        self._seed_all(client)
        placeholders = [a for a in client.get(AGENT_BASE).json() if a["is_placeholder"]]
        assert len(placeholders) == 1
        assert placeholders[0]["name"] == "更多智能体即将上线"

    def test_seed_agents_sorted(self, client):
        self._seed_all(client)
        agents = client.get(AGENT_BASE).json()
        orders = [a["sort_order"] for a in agents]
        assert orders == sorted(orders)
