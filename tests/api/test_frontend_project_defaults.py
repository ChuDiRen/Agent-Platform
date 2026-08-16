from pathlib import Path


def test_project_form_defaults_to_multimodal_model():
    project_vue = Path(__file__).resolve().parents[2] / "fronted" / "src" / "views" / "Project.vue"

    source = project_vue.read_text(encoding="utf-8")

    # 默认模型配置留空（不硬编码厂商地址），由用户按需填写
    assert "llm_model: ''" in source
    assert "lvm_model: ''" in source
    assert "llm_key" not in source
    assert "lvm_key" not in source
    assert "sk-..." not in source
