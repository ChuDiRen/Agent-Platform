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
