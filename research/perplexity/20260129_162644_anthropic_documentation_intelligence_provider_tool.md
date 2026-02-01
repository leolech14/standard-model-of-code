# Research: Anthropic documentation intelligence-provider tools API account management

> **Date:** 2026-01-29 16:26:44
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:a6093425f81011333544b567bae44a7af80668d9faf910797af80dd7af3893bb`
> **Raw JSON:** `raw/20260129_162644_anthropic_documentation_intelligence_provider_tool.json`

---

## Query

Anthropic documentation intelligence-provider tools API account management

---

## Response

Anthropic's official documentation for their API, including **tools**, **intelligence-provider** features (via tool use in the Messages API), and **account management** (primarily API key handling), is hosted at [docs.anthropic.com](https://docs.anthropic.com), with client SDK details on GitHub and the Claude Console.[1][3][6][10]

### Key Documentation Locations
- **Core API Reference**: Full REST API specs, including the Messages endpoint for tool calls (e.g., `tools` parameter with `input_schema`, `name`, and `description`), authentication via `x-api-key` header, and versioning (e.g., `anthropic-version: 2023-06-01` or later).[1][3][4]
- **Python SDK**: Install via `pip install anthropic`; initialize client with `ANTHROPIC_API_KEY` environment variable. Supports synchronous/async tool execution, batch listing, and custom HTTP requests for undocumented endpoints.[1]
- **Account Management**: Generate/manage API keys through the [Claude Console](https://console.anthropic.com) (login required); keys are passed as `api_key` in SDKs or `x-api-key` header in raw requests. No direct API for key creation/revocation documented—handle via console.[3][4]
- **Tools and Intelligence Features**: Tools are defined in `messages.create()` calls; Claude automatically invokes them in iterations if specified. Supports `tool_choice` modes like `auto`, `none`, or `tool`. Full details in Messages API reference.[1][3]
- **Additional Resources**:
  - Client SDKs overview: [platform.claude.com/docs/en/api/client-sdks](https://platform.claude.com/docs/en/api/client-sdks).[10]
  - Tutorials and examples: [Anthropic Academy](https://www.anthropic.com/learn/build-with-claude).[7]
  - Third-party compatibility (e.g., DeepSeek, AWS Bedrock): Maps to Anthropic format but with limitations on fields like images/documents.[2][5]

For complete references, start at [docs.anthropic.com](https://docs.anthropic.com) and [console.anthropic.com/docs](https://console.anthropic.com/docs).[3][6]

---

## Citations

1. https://github.com/anthropics/anthropic-sdk-python
2. https://api-docs.deepseek.com/guides/anthropic_api
3. https://platform.claude.com/docs/en/api/overview
4. https://zapier.com/blog/claude-api/
5. https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
6. https://platform.claude.com/docs/en/home
7. https://www.anthropic.com/learn/build-with-claude
8. https://www.postman.com/postman/anthropic-apis/documentation/dhus72s/claude-api
9. https://www.anthropic.com/claude/sonnet
10. https://platform.claude.com/docs/en/api/client-sdks

---

## Usage Stats

- Prompt tokens: 9
- Completion tokens: 478
- Total tokens: 487
