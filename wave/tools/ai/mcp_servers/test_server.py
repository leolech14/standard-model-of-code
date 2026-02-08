"""Quick smoke test for the Cerebras Intelligence MCP Server."""

import asyncio
import sys
import os

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastmcp import Client
from cerebras_intelligence_mcp import mcp


async def test():
    results = {"passed": 0, "failed": 0, "errors": []}

    async with Client(mcp) as client:
        # 1. List tools
        tools = await client.list_tools()
        expected = 10
        if len(tools) == expected:
            print(f"[PASS] {len(tools)} tools registered")
            results["passed"] += 1
        else:
            print(f"[FAIL] Expected {expected} tools, got {len(tools)}")
            results["failed"] += 1

        # 2. List resources
        resources = await client.list_resources()
        if len(resources) >= 2:
            print(f"[PASS] {len(resources)} resources registered")
            results["passed"] += 1
        else:
            print(f"[FAIL] Expected 2+ resources, got {len(resources)}")
            results["failed"] += 1

        # 3. estimate_tokens (no API key needed)
        try:
            result = await client.call_tool("estimate_tokens", {
                "file_paths": ["wave/tools/ai/intel.py"],
                "method": "fast",
            })
            text = result.content[0].text
            if '"tokens"' in text:
                print("[PASS] estimate_tokens returns token count")
                results["passed"] += 1
            else:
                print(f"[FAIL] estimate_tokens unexpected: {text[:100]}")
                results["failed"] += 1
        except Exception as e:
            print(f"[FAIL] estimate_tokens error: {e}")
            results["failed"] += 1

        # 4. get_project_health (no API key needed)
        try:
            result = await client.call_tool("get_project_health", {})
            text = result.content[0].text
            if '"health"' in text:
                print("[PASS] get_project_health returns health status")
                results["passed"] += 1
            else:
                print(f"[FAIL] get_project_health unexpected: {text[:100]}")
                results["failed"] += 1
        except Exception as e:
            print(f"[FAIL] get_project_health error: {e}")
            results["failed"] += 1

        # 5. get_project_context (no API key needed)
        try:
            result = await client.call_tool("get_project_context", {
                "context_set": "minimal",
                "output_format": "yaml",
            })
            text = result.content[0].text
            if "health" in text:
                print("[PASS] get_project_context returns formatted context")
                results["passed"] += 1
            else:
                print(f"[FAIL] get_project_context unexpected: {text[:100]}")
                results["failed"] += 1
        except Exception as e:
            print(f"[FAIL] get_project_context error: {e}")
            results["failed"] += 1

        # 6. check_token_budget (no API key needed)
        try:
            result = await client.call_tool("check_token_budget", {
                "file_paths": ["wave/tools/ai/intel.py"],
                "max_budget": 100000,
            })
            text = result.content[0].text
            if '"allowed"' in text:
                print("[PASS] check_token_budget returns budget check")
                results["passed"] += 1
            else:
                print(f"[FAIL] check_token_budget unexpected: {text[:100]}")
                results["failed"] += 1
        except Exception as e:
            print(f"[FAIL] check_token_budget error: {e}")
            results["failed"] += 1

        # 7. cerebras_query (needs API key)
        if os.getenv("CEREBRAS_API_KEY"):
            try:
                result = await client.call_tool("cerebras_query", {
                    "prompt": "Say hello in exactly 3 words.",
                    "max_tokens": 20,
                })
                text = result.content[0].text
                if len(text) > 0 and "error" not in text.lower():
                    print("[PASS] cerebras_query returns LLM response")
                    results["passed"] += 1
                else:
                    print(f"[FAIL] cerebras_query: {text[:100]}")
                    results["failed"] += 1
            except Exception as e:
                print(f"[FAIL] cerebras_query error: {e}")
                results["failed"] += 1
        else:
            print("[SKIP] cerebras_query (no CEREBRAS_API_KEY)")

        # 8. Read resource
        try:
            resource = await client.read_resource("intelligence://architecture-map")
            text = resource[0].text if hasattr(resource[0], "text") else str(resource[0])
            if "Architecture Map" in text:
                print("[PASS] architecture-map resource readable")
                results["passed"] += 1
            else:
                print(f"[FAIL] architecture-map unexpected content")
                results["failed"] += 1
        except Exception as e:
            print(f"[FAIL] architecture-map error: {e}")
            results["failed"] += 1

    print(f"\n{'='*40}")
    print(f"Results: {results['passed']} passed, {results['failed']} failed")
    return results["failed"] == 0


if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
