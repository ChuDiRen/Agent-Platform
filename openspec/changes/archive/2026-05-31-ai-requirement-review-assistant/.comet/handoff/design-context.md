# Comet Design Handoff

- Change: ai-requirement-review-assistant
- Phase: design
- Mode: compact
- Context hash: c8d290662a4314bb8d14ddda1222ce1be0192e386b1e472d8f549e92d2849420

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/ai-requirement-review-assistant/proposal.md

- Source: openspec/changes/ai-requirement-review-assistant/proposal.md
- Lines: 1-40
- SHA256: d9f910d63bc869f0b54062c6e30bfb81efd757567bc2aac32a96d202b839c906

```md
# AI Requirement Review Assistant

## Background

The agent hub already lists "AI需求评估助手", but selecting the card does not open a working review workspace. The reference screenshots show a document-oriented assistant with a directory tree, imported document content, an AI review modal, generated findings, adoption, and save behavior.

## Goals

- Turn the existing "AI需求评估助手" card into a usable workspace.
- Support adding root directories and child document nodes.
- Support importing a document into the editor area.
- Review selected requirement content through an AI-style service endpoint.
- Display review findings with selectable adoption states and detail expansion.
- Save reviewed requirement content and AI suggestions to backend storage.

## Scope

- Backend documents table/model/schema/CRUD/endpoints.
- Backend requirement review endpoint.
- Frontend API module for documents and review.
- Frontend route and page matching the reference UI.
- Agent hub navigation for the requirement assistant card.
- API tests and production frontend build verification.

## Non-Goals

- Real rich-text editor engine parity with the reference product.
- File upload parsing for Word/PDF formats.
- Streaming review progress windows.
- Multi-user document permissions.
- Live LLM provider integration beyond the deterministic review service contract used by this feature.

## Success Criteria

- Clicking "AI需求评估助手" opens the requirement assistant workspace.
- Users can add root directories and child items.
- Users can import sample requirement content and save it.
- Users can run AI review and see issue findings.
- Users can adopt selected findings into the document's saved AI suggestion payload.
- Tests and build pass.
```

## openspec/changes/ai-requirement-review-assistant/design.md

- Source: openspec/changes/ai-requirement-review-assistant/design.md
- Lines: 1-49
- SHA256: 3a0a6378e8abceb6b17ede385bedcc0182e5125eb2c70eab1f85424be18aaf37

```md
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
```

## openspec/changes/ai-requirement-review-assistant/tasks.md

- Source: openspec/changes/ai-requirement-review-assistant/tasks.md
- Lines: 1-11
- SHA256: d1f476b5e6d6b4e4bcb91330427680b5197b611d1fe967807df538c475c6498c

```md
# Tasks

- [ ] Create and verify OpenSpec and Comet lifecycle artifacts.
- [ ] Add failing/targeted API tests for documents and review.
- [ ] Add backend document model, schema, CRUD, migration, and endpoints.
- [ ] Add requirement review service and API endpoint.
- [ ] Add frontend document/review API module.
- [ ] Add requirement review workspace page, route, and agent-hub navigation.
- [ ] Verify with `python -m pytest tests/api/test_documents.py -q`.
- [ ] Verify with `cd fronted && pnpm build:prod`.
- [ ] Run Comet verify and archive.
```

## openspec/changes/ai-requirement-review-assistant/specs/requirement-review-assistant/spec.md

- Source: openspec/changes/ai-requirement-review-assistant/specs/requirement-review-assistant/spec.md
- Lines: 1-58
- SHA256: a405810ea35fdab56077a424909619ccf570c23a9a5ca56b80e00b23438f34b6

```md
# Requirement Review Assistant Capability

## ADDED Requirements

### Requirement: Open Requirement Assistant

The system SHALL open a requirement review workspace from the existing AI需求评估助手 card.

#### Scenario: Navigate from agent hub

- **WHEN** the user clicks the AI需求评估助手 card
- **THEN** the app navigates to the requirement review workspace
- **AND** the workspace shows a document tree, editor area, AI review button, and save button.

### Requirement: Manage Requirement Documents

The system SHALL allow users to create, list, update, and delete requirement document nodes.

#### Scenario: Add root directory

- **WHEN** the user creates a root directory
- **THEN** the document API stores it with `is_directory=true`
- **AND** the left tree displays it.

#### Scenario: Add child document

- **WHEN** the user creates a child under a directory
- **THEN** the document API stores the parent-child relationship
- **AND** selecting the child loads its content into the editor.

### Requirement: Import Requirement Content

The frontend SHALL provide an import action that creates or updates a document with sample requirement content.

#### Scenario: Import document

- **WHEN** the user clicks 导入文档
- **THEN** a document is created or updated with structured requirement text
- **AND** the editor displays that content.

### Requirement: Review Requirement Content

The backend SHALL review requirement content and return actionable findings.

#### Scenario: Generate findings

- **WHEN** content describes a login requirement with missing details
- **THEN** the review API returns findings such as missing post-login routing, username format, password complexity, visibility toggle, and retry handling.

### Requirement: Adopt and Save Suggestions

The workspace SHALL allow users to adopt selected review findings and persist them.

#### Scenario: Adopt findings

- **WHEN** the user selects findings and clicks 采纳
- **THEN** selected findings are written to the document's `ai_suggest`
- **AND** saving the requirement persists the current content.
```

