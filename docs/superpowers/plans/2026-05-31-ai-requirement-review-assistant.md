---
change: ai-requirement-review-assistant
design-doc: docs/superpowers/specs/2026-05-31-ai-requirement-review-assistant-design.md
base-ref: ad64b60f3b431d1a776f9b9fb48e535f6839992c
archived-with: 2026-05-31-ai-requirement-review-assistant
---

# AI Requirement Review Assistant Implementation Plan

## Task 1: API Tests First

1. Add `tests/api/test_documents.py`.
2. Cover document create/list/update/delete.
3. Cover review findings and suggestion persistence.
4. Run `python -m pytest tests/api/test_documents.py -q` and confirm red before backend implementation completes.

## Task 2: Backend Documents and Review

1. Add document model, schema, CRUD, and migration.
2. Import the model into `backend/app/db/base.py`.
3. Add requirement review service.
4. Add `/api/v1/documents` endpoints.
5. Register router in `backend/app/main.py`.
6. Run `python -m pytest tests/api/test_documents.py -q`.

## Task 3: Frontend Workspace

1. Add `fronted/src/api/document.ts`.
2. Add `fronted/src/views/RequirementReviewAssistant.vue`.
3. Add `/requirement-review` route.
4. Route the `AI需求评估助手` card from the agent hub.
5. Run `cd fronted && pnpm build:prod`.

## Task 4: Comet Closure

1. Check off tasks after verification passes.
2. Add `scripts/verify-requirement-review.sh` for Comet guard.
3. Save verification report.
4. Run build, verify, and archive guards.

## Verification Plan

- Backend: `python -m pytest tests/api/test_documents.py -q`
- Frontend: `cd fronted && pnpm build:prod`
- Comet guard wrapper: `bash scripts/verify-requirement-review.sh`
- Scope: `gitnexus_detect_changes(scope=all)`
