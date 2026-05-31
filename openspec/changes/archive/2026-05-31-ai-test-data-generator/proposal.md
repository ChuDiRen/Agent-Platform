# AI Test Data Generator

## Background

The agent hub advertises an "AI测试数据生成智能体", but selecting it currently shows a placeholder message instead of a usable tool. The reference image shows a focused data-generation workspace with basic options, extra generation requirements, editable fields, template persistence, and a result preview/export area.

## Goals

- Provide a full AI test-data generation page reachable from the agent hub.
- Allow users to configure output count, format, language, free-form hints, and fields.
- Persist reusable templates in the `test_data_templates` table.
- Generate JSON and CSV payloads through a FastAPI endpoint.
- Integrate `langchain-ai/deepagents` as the required AI generation path.
- Preserve a reliable test path by mocking deepagents in automated tests rather than using a rules fallback.

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
- `/api/v1/test-data/generate` calls deepagents and returns stable JSON/CSV content in tests through a mocked deepagents agent.
- `/api/v1/test-data/templates/` supports create/list/read/update/delete.
- Verification commands pass without requiring an API key.
