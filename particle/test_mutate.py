import json
from src.core.rag.mcp_server import collider_mutate

TARGET = "/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/rag/test_dummy.py"
MUTATIONS = json.dumps([
    {
        "action": "replace_function_body",
        "target_node": "hello",
        "new_body": "def hello():\n    print('hello universe')\n    return 42"
    }
])

print(f"Applying mutations to {TARGET}...")
res = collider_mutate(TARGET, MUTATIONS)
print(f"Result: {res}")
