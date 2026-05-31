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
