from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SRC = ROOT / "fronted" / "src"
AGENT_VIEW_FILES = [
    FRONTEND_SRC / "views" / "AITestCaseAgent.vue",
    FRONTEND_SRC / "views" / "ApiDocumentAnalysis.vue",
    FRONTEND_SRC / "views" / "RequirementReviewAssistant.vue",
    FRONTEND_SRC / "views" / "UiAutomationAgent.vue",
    FRONTEND_SRC / "views" / "ApiAutomationAgent.vue",
    FRONTEND_SRC / "views" / "PerformanceAnalysisAssistant.vue",
]


def test_agent_views_use_project_context_helper():
    for path in AGENT_VIEW_FILES:
        source = path.read_text(encoding="utf-8")

        assert "useProjectContext" in source, path
        assert "requireProjectId()" in source, path
        assert "const projectId = 1" not in source, path
        assert "projectId: 1" not in source, path
        assert "project_id: 1" not in source, path


def test_project_context_reads_query_project_id():
    source = (FRONTEND_SRC / "composables" / "useProjectContext.ts").read_text(encoding="utf-8")

    assert "route.query.projectId" in source
    assert "Number.isInteger(projectId)" in source
    assert "router.replace('/projects')" in source


def test_http_auth_boundary_uses_bearer_and_resets_on_401():
    source = (FRONTEND_SRC / "api" / "http.ts").read_text(encoding="utf-8")

    assert "`Bearer ${token}`" in source
    assert "handleUnauthorized()" in source
    assert "removeToken()" in source
    assert "useUserStore().resetUser()" in source
    assert "status === 403" in source


def test_project_entry_preserves_project_context_query():
    source = (FRONTEND_SRC / "views" / "Project.vue").read_text(encoding="utf-8")

    assert "router.push({ path: '/agent-hub', query: { projectId: String(projectId) } })" in source
    assert "enterProject(fresh.id)" in source
    assert "router.push('/agent-hub')" not in source


def test_e2e_helpers_unwrap_real_api_envelope():
    source = (ROOT / "tests" / "e2e" / "helpers.ts").read_text(encoding="utf-8")

    assert "type ApiEnvelope" in source
    assert "return body.data" in source
    assert "login.access_token" in source
    assert "return body.access_token" not in source
