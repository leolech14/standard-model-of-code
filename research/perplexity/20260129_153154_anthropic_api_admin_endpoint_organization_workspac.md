# Research: Anthropic API admin endpoint organization workspace billing info account details 2026

> **Date:** 2026-01-29 15:31:54
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:5f3191e33397d7f2c4ec2c13e5cfd13f60d55c4bb60ad2a6bac36056a29891a6`
> **Raw JSON:** `raw/20260129_153154_anthropic_api_admin_endpoint_organization_workspac.json`

---

## Query

Anthropic API admin endpoint organization workspace billing info account details 2026

---

## Response

Anthropic's Admin API provides endpoints for managing organizations and workspaces (e.g., creating, listing, archiving workspaces, and handling members), but search results do not document specific admin endpoints for retrieving **organization workspace billing info or account details**.[3]

## Available Admin API Endpoints for Organizations/Workspaces[3]
These require an **Admin API key** (starting with `sk-ant-admin-`):
- **Create workspace**: `POST /v1/organizations/workspaces`
  ```
  curl --request POST "https://api.anthropic.com/v1/organizations/workspaces" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"name": "Production"}'
  ```
- **List workspaces**: `GET /v1/organizations/workspaces?limit=10&include_archived=false`
- **Archive workspace**: `POST /v1/organizations/workspaces/{workspace_id}/archive`
- **Manage members**: `POST/POST/DELETE /v1/organizations/workspaces/{workspace_id}/members/{user_id}` (add, update role, remove)

**Usage tracking** is available via endpoints like those grouping by `workspace_id` (default workspace shows `null` for `workspace_id`), but no billing/account details are specified.[3]

## Related Features (Not Admin/Billing Endpoints)
- **Compliance API**: Provides real-time programmatic access to Claude **usage data**, customer content, MCP servers, local data storage, and agent activity for enterprises (requires integration; enables monitoring but not billing).[1]
- **Pricing info**: Claude 4.5 API ranges from $1–$75 per million tokens with tiered rate limits; no admin retrieval endpoint documented.[5]
- **Organization ID**: Available via `anthropic-organization-id` response header on all API calls.[4]

No 2026-specific admin billing endpoints appear in results; check Anthropic's official docs at platform.claude.com for updates, as console redirects there post-January 12, 2026.[3][4]

---

## Citations

1. https://www.token.security/blog/why-anthropics-new-compliance-api-is-a-game-changer-for-secure-agentic-ai-access
2. https://ai-consciousness.org/anthropics-claude-opus-4-5-system-prompt-as-of-january-2026/
3. https://platform.claude.com/docs/en/build-with-claude/workspaces
4. https://platform.claude.com/docs/en/release-notes/overview
5. https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration
6. https://github.com/danny-avila/LibreChat/issues/10655
7. https://www.anthropic.com/research/anthropic-economic-index-january-2026-report
8. https://www.youtube.com/watch?v=2w75E9cQPUM

---

## Usage Stats

- Prompt tokens: 14
- Completion tokens: 449
- Total tokens: 463
