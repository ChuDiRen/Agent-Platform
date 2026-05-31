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

### Requirement: Generate Through deepagents

The backend SHALL use deepagents as the generation path without a local rules fallback.

#### Scenario: deepagents model unavailable

- **WHEN** `DEEPAGENTS_MODEL` is unavailable
- **THEN** the generation API returns `503`
- **AND** it does not synthesize data through hard-coded local rules.

#### Scenario: web request safety

- **WHEN** deepagents is used from the API
- **THEN** it must not expose local shell or unrestricted filesystem tools to user input.
