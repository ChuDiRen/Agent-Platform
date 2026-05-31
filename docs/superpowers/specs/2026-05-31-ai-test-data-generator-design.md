---
comet_change: ai-test-data-generator
role: technical-design
canonical_spec: openspec
archived-with: 2026-05-31-ai-test-data-generator
status: final
---

# AI Test Data Generator Technical Design

## Context

The product needs the advertised "AI测试数据生成智能体" to become a real workspace. The reference image defines the user-facing shape: top-level generation options, extra requirement text, editable fields, template actions, and a result preview/export area.

## Architecture

### Backend

- `backend/app/schemas/test_data.py` defines field, template, request, and response contracts.
- `backend/app/models/test_data_template.py` stores reusable templates. The `fields` column is JSON text to stay compatible with SQLite and the existing Alembic style.
- `backend/app/crud/test_data_template.py` serializes/deserializes template field arrays around the generic CRUD base.
- `backend/app/services/test_data_agent.py` owns generation. It requires deepagents model configuration and returns service errors instead of using local rules.
- `backend/app/api/v1/endpoints/test_data.py` exposes generation and template endpoints.
- `backend/app/main.py` registers the router under `/api/v1/test-data`.

### Frontend

- `fronted/src/api/testData.ts` provides typed API functions.
- `fronted/src/views/TestDataGenerator.vue` implements the workspace.
- `fronted/src/router/index.ts` adds `/test-data-generator`.
- `fronted/src/views/AgentHub.vue` routes the data agent to the page.

## deepagents Integration

Use `langchain-ai/deepagents` as the generation engine:

- Lazy import `create_deep_agent` so the app starts without the dependency in local/test environments.
- Do not use `FilesystemBackend` or `LocalShellBackend` in request handling.
- Prefer the default in-memory/state behavior for request-scoped generation.
- Require explicit provider configuration before attempting AI generation.
- Validate the returned data shape; if parsing or validation fails, return a service error.

This keeps the feature aligned with the AI-agent requirement while preserving deterministic tests through mocked deepagents.

## Data Contracts

Supported field types:

- `number`
- `string`
- `email`
- `phone`
- `date`
- `boolean`

Output formats:

- `json`
- `csv`

Languages:

- `zh`
- `en`

Generation response returns both structured `data` rows and rendered `content`, plus `format`, `count`, and elapsed milliseconds.

## Error Handling

- Schema validation rejects empty field names, invalid formats, invalid languages, and out-of-range counts.
- Template reads/updates/deletes return `404` when the template does not exist.
- Frontend API failures surface through `ElMessage`.
- Clipboard/download failures are caught and shown to the user.

## Testing Strategy

### API Tests

Command:

```powershell
python -m pytest tests/api/test_test_data.py -q
```

Evidence:

- JSON generation returns stable Chinese defaults.
- CSV generation renders header and rows.
- Template create/list/update/delete round trip passes.
- The test path mocks deepagents and does not require external model credentials.

### Frontend Build

Command:

```powershell
cd fronted
pnpm build:prod
```

Evidence:

- Vue route/component/API types compile.
- Production Vite build succeeds.

## Acceptance Notes

The implementation is complete when users can open the page from the agent hub, generate data, save/load templates, copy/download results, and the API/build checks pass.
