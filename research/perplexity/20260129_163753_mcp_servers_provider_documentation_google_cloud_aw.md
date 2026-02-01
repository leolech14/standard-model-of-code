# Research: MCP servers provider documentation Google Cloud AWS Azure Stripe 2026

> **Date:** 2026-01-29 16:37:53
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:6ffe23f5ce7d93b76ee49907e4a6e8182c8d981ff9efe5aeb91b3716556d5290`
> **Raw JSON:** `raw/20260129_163753_mcp_servers_provider_documentation_google_cloud_aw.json`

---

## Query

MCP servers provider documentation Google Cloud AWS Azure Stripe 2026

---

## Response

**AWS provides the primary MCP (Model Context Protocol) server offerings among major cloud providers, with detailed documentation available.** No equivalent MCP server documentation exists for Google Cloud, Azure, or Stripe based on current information[1][2][3][7].

### AWS MCP Server Overview
The **AWS MCP Server** is a managed remote service enabling AI agents and assistants to securely access AWS services via natural language, combining real-time documentation, over 15,000 API calls, and pre-built **Agent SOPs** (standard operating procedures) for multi-step tasks like provisioning EC2 instances, deploying to S3/CloudFront, or troubleshooting Lambda[2][3][4][5]. It consolidates prior servers (AWS API MCP and AWS Knowledge MCP) into a unified interface with IAM authentication, CloudTrail logging, and no additional cost beyond resource usage[1][2][3][6].

### Deployment and Documentation
- **AWS Marketplace**: Deploy the **AWS API MCP Server** as a managed service on Amazon Bedrock AgentCore with step-by-step instructions, SigV4/JWT authentication, IAM policies, and regional support. GitHub repo provides further guides[1].
- **User Guide**: Covers setup (credentials, IAM, client config), testing, Agent SOPs (e.g., VPC setup, CI/CD), security (data protection, compliance), and tools like `aws__search_documentation`[3][5][7].
- **Availability**: Generally available in US East (N. Virginia); preview features like Deployment Agent SOPs in select regions[2][4].
- **GitHub**: Official awslabs/mcp repo for AWS MCP Servers implementation[8].

### Other Providers
- **Google Cloud, Azure, Stripe**: No MCP server providers or documentation mentioned. AWS leads in MCP for AI agent integration with cloud services[1-9].
- Related: AWS Knowledge MCP Server (GA, public access for docs/blogs at no cost)[6].

For setup, start with AWS docs: configure IAM, connect MCP clients over HTTPS, and test with queries like AWS region availability[3][5]. Pricing is pay-for-use AWS resources only[2][3].

---

## Citations

1. https://aws.amazon.com/about-aws/whats-new/2025/11/the-aws-api-mcp-server-aws-marketplace/
2. https://aws.amazon.com/about-aws/whats-new/2025/11/aws-mcp-server/
3. https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html
4. https://aws.amazon.com/about-aws/whats-new/2025/01/aws-announces-deployment-agent-sops-in-aws-mcp-server-preview/
5. https://docs.aws.amazon.com/pdfs/aws-mcp/latest/userguide/mcp-ug.pdf
6. https://aws.amazon.com/about-aws/whats-new/2025/10/aws-knowledge-mcp-server-generally-available/
7. https://docs.aws.amazon.com/aws-mcp/
8. https://github.com/awslabs/mcp
9. https://builder.aws.com/content/37OUn4FLJII9HcNF4q1pJrpbuMa/aws-mcp-servers-part-1-your-ai-assistants-gateway-to-real-time-aws-knowledge

---

## Usage Stats

- Prompt tokens: 13
- Completion tokens: 442
- Total tokens: 455
