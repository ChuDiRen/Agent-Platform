from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_frontend_api_base_url_is_code_defined():
    source = (ROOT / "fronted" / "src" / "api" / "baseUrl.ts").read_text(encoding="utf-8")

    assert "import.meta.env" not in source
    assert "VITE_" not in source
    assert "export const baseUrl = ''" in source


def test_vite_config_does_not_load_env_files():
    source = (ROOT / "fronted" / "vite.config.ts").read_text(encoding="utf-8")

    assert "loadEnv" not in source
    assert "VITE_" not in source
    assert "target: 'http://localhost:8000'" in source
    assert "outDir: 'dist'" in source
