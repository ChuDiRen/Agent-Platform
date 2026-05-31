# Comet Design Handoff

- Change: ai-test-data-generator
- Phase: design
- Mode: compact
- Context hash: 1e11053e45de93dc89acab9d1d9c97fdf1d34ab08feb1e0e8b775ce26298c459

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/ai-test-data-generator/proposal.md

- Source: openspec/changes/ai-test-data-generator/proposal.md
- Lines: 1-36
- SHA256: 46cfb38b82060b9c54064cbc0026db09272850bc8c1ff1c56e83d57bd1c4257d

```md
# AI Test Data Generator

## Background

The agent hub advertises an "AI测试数据生成智能体", but selecting it currently shows a placeholder message instead of a usable tool. The reference image shows a focused data-generation workspace with basic options, extra generation requirements, editable fields, template persistence, and a result preview/export area.

## Goals

- Provide a full AI test-data generation page reachable from the agent hub.
- Allow users to configure output count, format, language, free-form hints, and fields.
- Persist reusable templates in the `test_data_templates` table.
- Generate JSON and CSV payloads through a FastAPI endpoint.
- Integrate `langchain-ai/deepagents` as the AI generation path when dependencies and provider credentials are available, while keeping a deterministic fallback for local development and tests.
- Preserve a reliable test path that does not require external model credentials.

## Scope

- Backend schema/model/CRUD/endpoint support for generation and templates.
- Frontend API module, route, agent-hub navigation, and Vue page matching the reference layout.
- API tests for generation and template CRUD.
- Frontend build verification.

## Non-Goals

- Streaming generation jobs or background queues.
- Public file-system or shell-backed deepagents tools.
- Advanced template sharing, permissions, or multi-user ownership rules.
- Production provider setup for a specific LLM vendor.

## Success Criteria

- Clicking the test-data agent opens the generator page.
- Users can add/remove fields, enter hints, generate data, copy JSON, download output, and save/load templates.
- `/api/v1/test-data/generate` returns stable JSON/CSV content in tests.
- `/api/v1/test-data/templates/` supports create/list/read/update/delete.
- Verification commands pass without requiring an API key.
```

## openspec/changes/ai-test-data-generator/design.md

- Source: openspec/changes/ai-test-data-generator/design.md
- Lines: 1-54
- SHA256: 27489f8b017f3f15489f5d01018c0c45ce28265cd53b7eca72aa6ab5b78688d9

```md
# AI Test Data Generator Design

## Approach

Add a narrow test-data generation feature that follows the repository's existing FastAPI + Vue patterns. The backend owns validation, deterministic fallback generation, optional deepagents execution, and template persistence. The frontend owns the form-driven workspace shown in the reference image and uses the existing Axios wrapper.

## Backend Decisions

- Add `/api/v1/test-data` routes:
  - `POST /generate`
  - `GET /templates/`
  - `POST /templates/`
  - `GET /templates/{id}`
  - `PUT /templates/{id}`
  - `DELETE /templates/{id}`
- Store template field definitions as JSON text in SQLite for compatibility with the current migration style.
- Keep request schemas constrained: count `1..500`, field names required, supported field types are `number`, `string`, `email`, `phone`, `date`, and `boolean`.
- Use deepagents only through a contained service. If the package/provider configuration is missing, return deterministic fallback data so tests and local development remain reliable.
- Avoid `FilesystemBackend` and `LocalShellBackend` in request handling because official deepagents docs warn against exposing them in web/API contexts.

## Frontend Decisions

- Add `TestDataGenerator.vue` under `fronted/src/views`.
- Add `src/api/testData.ts` for typed API calls.
- Add `/test-data-generator` route.
- Change the existing test-data agent card to navigate to this route.
- Match the reference page with top controls, hint textarea, editable field rows, template actions, generation status, and result preview/export controls.

## Data Flow

1. User opens the agent hub and selects the test-data agent.
2. Vue route renders the generator workspace with default fields.
3. User edits count/format/language/hint/fields.
4. Frontend posts to `/api/v1/test-data/generate`.
5. Backend tries deepagents generation when available and configured; otherwise it uses deterministic field rules.
6. Frontend displays content, supports copy/download, and can save/load templates via template endpoints.

## Testing Strategy

- API tests:
  - `pytest tests/api/test_test_data.py -q`
  - Covers deterministic JSON generation, CSV generation, and template CRUD.
- Frontend build:
  - `cd fronted && pnpm build:prod`
  - Catches route, API type, and Vue template errors.
- Backend smoke:
  - `python -m pytest tests/api/test_test_data.py -q`
  - Uses deterministic fallback and does not require external model credentials.

## Risks

- deepagents APIs can evolve quickly. Keep the integration optional and isolated behind lazy imports.
- Browser downloads and clipboard APIs can fail in restricted contexts. The UI must show Element Plus messages for success/failure.
- The existing dirty worktree already contains part of this feature; edits must preserve and complete that work instead of replacing it wholesale.
```

## openspec/changes/ai-test-data-generator/tasks.md

- Source: openspec/changes/ai-test-data-generator/tasks.md
- Lines: 1-10
- SHA256: 19b45658de60aa8e8598b4d6cd9ac5348af0a44516b1ce5f82a3129bbeaf1154

```md
# Tasks

- [ ] Create and verify OpenSpec and Comet lifecycle artifacts.
- [ ] Add failing/targeted API tests for generation and template CRUD, then make them pass with backend routes.
- [ ] Add optional deepagents service integration with deterministic fallback and no web-exposed shell/filesystem backend.
- [ ] Register backend test-data routes and database model migration.
- [ ] Add frontend typed API module for generation and templates.
- [ ] Add generator page, route, and agent-hub navigation matching the reference UI.
- [ ] Verify with `python -m pytest tests/api/test_test_data.py -q`.
- [ ] Verify with `cd fronted && pnpm build:prod`.
```

## openspec/changes/ai-test-data-generator/specs/test-data-generation/spec.md

- Source: openspec/changes/ai-test-data-generator/specs/test-data-generation/spec.md
- Lines: 1-67
- SHA256: 9e12beeb0973e22ccf021d75836b818107461ad9cec214005285989b25b69adc

```md
# Test Data Generation Capability

## ADDED Requirements

### Requirement: Generate Configured Test Data

The system SHALL generate tabular test data from field definitions, count, format, language, and an optional hint.

#### Scenario: Generate JSON with Chinese defaults

- **WHEN** the user requests 3 JSON rows with fields `id`, `username`, and `pass`
- **THEN** the API returns 3 rows
- **AND** `id` increments from 1
- **AND** Chinese string defaults include values such as `用户1` and `密码1`
- **AND** the response includes formatted JSON content.

#### Scenario: Generate CSV

- **WHEN** the user requests CSV rows for an email field
- **THEN** the API returns CSV content with a header row
- **AND** generated email rows follow the configured rule prefix.

### Requirement: Manage Test Data Templates

The system SHALL allow users to persist and reuse generation templates.

#### Scenario: Create and list templates by project

- **WHEN** a template is created with a project id and field definitions
- **THEN** the API stores the template
- **AND** listing templates for that project returns the created template.

#### Scenario: Update and delete templates

- **WHEN** an existing template is updated
- **THEN** the changed values are returned
- **AND** deleting the template removes it from later reads.

### Requirement: Provide Generator Workspace UI

The frontend SHALL provide a workspace equivalent to the reference image.

#### Scenario: Open from agent hub

- **WHEN** the user clicks the AI test data generation agent
- **THEN** the app navigates to the generator page.

#### Scenario: Operate generator controls

- **WHEN** the user changes count, format, language, hint, and fields
- **THEN** the page sends those values to the generation API
- **AND** displays generation status, output preview, copy action, and download action.

### Requirement: Integrate deepagents Safely

The backend SHALL use deepagents as an optional AI generation path without making tests or local development depend on external provider credentials.

#### Scenario: deepagents unavailable

- **WHEN** `deepagents` or provider credentials are unavailable
- **THEN** generation falls back to deterministic local rules
- **AND** the API response still satisfies the requested schema.

#### Scenario: web request safety

- **WHEN** deepagents is used from the API
- **THEN** it must not expose local shell or unrestricted filesystem tools to user input.
```

