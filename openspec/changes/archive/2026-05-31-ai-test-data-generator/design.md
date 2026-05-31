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
- Use deepagents only through a contained service. If the package/provider configuration is missing, return a clear service error instead of generating with local rules.
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
5. Backend calls deepagents generation when configured; missing configuration returns `503`.
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
  - Uses a mocked deepagents module and does not require external model credentials.

## Risks

- deepagents APIs can evolve quickly. Keep the integration isolated behind lazy imports and covered by mock-based tests.
- Browser downloads and clipboard APIs can fail in restricted contexts. The UI must show Element Plus messages for success/failure.
- The existing dirty worktree already contains part of this feature; edits must preserve and complete that work instead of replacing it wholesale.
