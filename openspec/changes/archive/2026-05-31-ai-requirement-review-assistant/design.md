# AI Requirement Review Assistant Design

## Approach

Implement a focused requirement-document workspace that follows the repository's FastAPI + Vue patterns. The backend stores documents in a `documents` table and exposes a review endpoint. The frontend renders the left tree, content editor, review modal, and adoption controls from the screenshots.

## Backend Decisions

- Add `Document` model with `project_id`, `name`, `parent_id`, `title`, `content`, `created_by`, `is_directory`, and `ai_suggest`.
- Store `ai_suggest` as JSON text to match the current SQLite-friendly style.
- Add CRUD helpers for listing by project, creating, updating, and deleting.
- Add `/api/v1/documents` endpoints for document tree operations.
- Add `POST /api/v1/documents/review` that analyzes submitted content and returns findings.
- Keep review deterministic and local for now so it is testable without external credentials, while preserving the API shape needed to swap in an AI provider later.

## Frontend Decisions

- Add `RequirementReviewAssistant.vue` under `fronted/src/views`.
- Add `src/api/document.ts` with typed document and review calls.
- Add `/requirement-review` route.
- Change the existing `doc` agent card to navigate to `/requirement-review`.
- Use Element Plus dialog/input controls and a textarea-backed document editor for reliable build compatibility.

## Data Flow

1. User opens the agent hub and clicks "AI需求评估助手".
2. Vue loads `/requirement-review` and fetches document nodes.
3. User adds root/child nodes or imports a sample document.
4. User selects a document and edits content.
5. User clicks `AI需求评审`, frontend posts selected document content and optional note.
6. Backend returns review findings.
7. User selects findings and clicks `采纳`; frontend writes selected findings to `ai_suggest`.
8. User clicks `保存需求`; frontend persists current document content.

## Testing Strategy

- API tests:
  - `python -m pytest tests/api/test_documents.py -q`
  - Covers document CRUD, tree listing, review findings, and suggestion persistence.
- Frontend build:
  - `cd fronted && pnpm build:prod`
  - Catches route, API type, and Vue page errors.
- Comet guard wrapper:
  - `bash scripts/verify-requirement-review.sh`

## Risks

- The reference UI uses a rich editor; this implementation uses a textarea-backed editor to keep scope focused and dependency-free.
- Existing uncommitted changes from the previous feature remain in the worktree; this change must avoid reverting them.
