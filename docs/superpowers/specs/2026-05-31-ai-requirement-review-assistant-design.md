---
comet_change: ai-requirement-review-assistant
role: technical-design
canonical_spec: openspec
archived-with: 2026-05-31-ai-requirement-review-assistant
status: final
---

# AI Requirement Review Assistant Technical Design

## Context

The platform already seeds an `AI需求评估助手` card. The change makes that advertised assistant usable by adding a requirement-document workspace, document persistence, and an AI review workflow similar to the provided screenshots.

## Architecture

### Backend

- `backend/app/models/document.py` stores document tree nodes.
- `backend/app/schemas/document.py` defines document CRUD contracts and review request/response contracts.
- `backend/app/crud/document.py` provides project-scoped listing and JSON serialization for `ai_suggest`.
- `backend/app/services/requirement_review.py` analyzes requirement content and returns structured findings.
- `backend/app/api/v1/endpoints/documents.py` exposes document CRUD and review routes.
- `backend/app/main.py` registers `/api/v1/documents`.

### Frontend

- `fronted/src/api/document.ts` provides typed document/review calls.
- `fronted/src/views/RequirementReviewAssistant.vue` implements the workspace.
- `fronted/src/router/index.ts` adds `/requirement-review`.
- `fronted/src/views/AgentHub.vue` routes the `doc` assistant card to the workspace.

## Data Model

`documents` columns:

- `id`
- `project_id`
- `name`
- `parent_id`
- `title`
- `content`
- `created_by`
- `is_directory`
- `created_at`
- `updated_at`
- `ai_suggest`

`ai_suggest` stores adopted review findings as JSON text.

## Review Contract

The review API accepts:

- `document_id`
- `title`
- `content`
- `extra_prompt`

The response returns a list of findings with:

- `id`
- `title`
- `description`
- `severity`
- `category`
- `adopted`

The initial analyzer is deterministic so API behavior can be verified locally. It is isolated in a service module so a model-backed review provider can replace it later without changing the frontend contract.

## UI Behavior

- Left pane shows document tree operations: add root directory, import document, add child, edit, delete.
- Right pane shows current document path, AI review/save buttons, toolbar-like visual chrome, and editable requirement content.
- Review modal shows findings, selected/adopted state, expanded detail text, extra prompt field, and actions for review, adopt, and save.
- Save writes current editor content and adopted suggestions.

## Testing Strategy

### API Tests

Command:

```powershell
python -m pytest tests/api/test_documents.py -q
```

Evidence:

- Create root directory and child document.
- List by project.
- Update content and adopted suggestions.
- Review login content and receive actionable findings.
- Delete document.

### Frontend Build

Command:

```powershell
cd fronted
pnpm build:prod
```

Evidence:

- Route, API module, and Vue page compile.

## Scope Notes

The reference product uses a rich editor. This implementation uses a textarea-backed editor inside a rich-editor-like frame to keep the feature dependency-free and reliable in the current stack.
