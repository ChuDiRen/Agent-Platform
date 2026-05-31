---
change: ai-test-data-generator
design-doc: docs/superpowers/specs/2026-05-31-ai-test-data-generator-design.md
base-ref: ad64b60f3b431d1a776f9b9fb48e535f6839992c
archived-with: 2026-05-31-ai-test-data-generator
---

# AI Test Data Generator Implementation Plan

## Task 1: Backend API and Template Persistence

1. Run `python -m pytest tests/api/test_test_data.py -q` and confirm the existing tests fail before route registration is complete.
2. Register `/api/v1/test-data` in `backend/app/main.py`.
3. Ensure `TestDataTemplate` is imported by database metadata.
4. Keep Alembic migration for `test_data_templates`.
5. Re-run `python -m pytest tests/api/test_test_data.py -q`.

## Task 2: deepagents Optional Generation Service

1. Add `backend/app/services/test_data_agent.py`.
2. Implement mock-backed tests as the stable test path.
3. Implement lazy deepagents integration guarded by environment/provider availability, with no rules fallback.
4. Refactor endpoint generation to call the service.
5. Re-run `python -m pytest tests/api/test_test_data.py -q`.

## Task 3: Frontend API and Workspace

1. Add `fronted/src/api/testData.ts`.
2. Add `fronted/src/views/TestDataGenerator.vue`.
3. Add `/test-data-generator` route.
4. Change the data agent card to navigate to the generator page.
5. Run `cd fronted && pnpm build:prod`.

## Task 4: Lifecycle and Verification

1. Check off OpenSpec tasks only after matching verification passes.
2. Run `gitnexus_detect_changes(scope=all)` before completion.
3. Save verification report under `docs/superpowers/reports`.
4. Transition Comet build, verify, and archive phases after guards pass.

## Verification Plan

- Backend: `python -m pytest tests/api/test_test_data.py -q`
- Frontend: `cd fronted && pnpm build:prod`
- Comet guard wrapper: `bash scripts/verify-test-data.sh`
- Scope: `gitnexus_detect_changes(scope=all)`

## Known Constraints

- `superpowers:writing-plans` is listed in Comet instructions but the local skill file is not installed; this plan follows the required plan shape manually.
- External deepagents/provider credentials are not required for tests because deepagents is mocked.
