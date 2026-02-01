# Research: Claude API admin tools account tier billing documentation 2026

> **Date:** 2026-01-29 16:28:37
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:c2661cd732aaee897e0f42ba0246d6230d65e8355f93145153231ee169702219`
> **Raw JSON:** `raw/20260129_162837_claude_api_admin_tools_account_tier_billing_docume.json`

---

## Query

Claude API admin tools account tier billing documentation 2026

---

## Response

The **Claude Admin API** provides programmatic management of organization resources like members, workspaces, API keys, and billing (via the **billing** role), but is unavailable for individual accounts and requires special access with an **admin** role and a unique Admin API key (starting with `sk-ant-admin...`). Provision these keys via Claude Console → Settings → Organization, then use them in API calls with the `x-api-key` header and `anthropic-version: 2023-06-01`.[1]

## Key Features and Endpoints
Organization roles determine permissions, including **billing** access for managing billing details:

| Role          | Permissions                                      |
|---------------|--------------------------------------------------|
| **user**     | Use Workbench                                    |
| **claude_code_user** | Use Workbench and Claude Code                    |
| **developer** | Use Workbench and manage API keys                |
| **billing**  | Use Workbench and **manage billing details**     |
| **admin**    | All above, plus manage users                     |[1]

### Manage Members
- List: `GET /v1/organizations/users?limit=10`[1]
- Update role (e.g., to billing): `POST /v1/organizations/users/{user_id}` with `{"role": "billing"}`[1]
- Remove: `DELETE /v1/organizations/users/{user_id}`[1]

### Manage Workspaces
- Create: `POST /v1/organizations/workspaces` with `{"name": "Production"}`[1]
- List: `GET /v1/organizations/workspaces?limit=10&include_archived=false`[1]
- Archive: `POST /v1/organizations/workspaces/{workspace_id}/archive`[1]
- Add/remove members with workspace roles (e.g., `workspace_admin`).[1]

### Manage API Keys
- List: `GET /v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx`[1]

### Organization Info
- Get details: `GET /v1/organizations/me`[1]

## Account Tiers and Billing
No direct Admin API endpoints for tier changes or billing queries are detailed, but the **billing** role enables manual management in Console; usage tracking and quotas are handled via Console dashboards (organization-level only).[1] For 2026 pricing/tiers (individuals vs. organizations), refer to external summaries, as official Admin API docs focus on access control rather than billing APIs.[4]

Admin API lacks explicit 2026-specific updates in available docs; requires organization setup first (not for solo accounts).[1] Standard API keys handle usage billing via Console quotas.[2]

---

## Citations

1. https://platform.claude.com/docs/en/build-with-claude/administration-api
2. https://www.datastudios.org/post/how-to-use-claude-with-the-anthropic-api-for-document-analysis-tool-use-and-data-workflows-full-g
3. https://platform.claude.com/docs/en/release-notes/overview
4. https://www.finout.io/blog/claude-pricing-in-2026-for-individuals-organizations-and-developers
5. https://concentric.ai/claude-security-guide/
6. https://www.jitendrazaa.com/blog/ai/claude-code-complete-guide-2026-from-basics-to-advanced-mcp-2/
7. https://dev.to/chand1012/the-best-way-to-do-agentic-development-in-2026-14mn
8. https://www.youtube.com/watch?v=sy65ARFI9Bg

---

## Usage Stats

- Prompt tokens: 12
- Completion tokens: 566
- Total tokens: 578
