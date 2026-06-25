from pathlib import Path


def test_project_form_defaults_to_multimodal_model():
    project_vue = Path(__file__).resolve().parents[2] / "fronted" / "src" / "views" / "Project.vue"

    source = project_vue.read_text(encoding="utf-8")

    assert "llm_model: 'mimo-v2.5-pro'" in source
    assert "lvm_model: 'mimo-v2.5'" in source
    assert 'placeholder="mimo-v2.5-pro"' in source
    assert 'placeholder="mimo-v2.5"' in source
