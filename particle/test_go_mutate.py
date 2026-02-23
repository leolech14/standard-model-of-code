import json
from src.core.synthesis.compiler import ColliderCompiler

TARGET = "/Users/lech/PROJECTS_all/PROJECT_elements/particle/src/core/synthesis/go_adapter/dummy.go"
MUTATIONS = [
    {
        "action": "replace_function_body",
        "target_node": "hello",
        "new_body": "func hello() {\n\tfmt.Println(\"hello universe\")\n}"
    }
]

print(f"Reading {TARGET}...")
with open(TARGET, "r") as f:
    source_code = f.read()

request_obj = {
    "target_file": TARGET,
    "mutations": MUTATIONS
}

print(f"Applying Go mutations to {TARGET}...")
res = ColliderCompiler.apply_mutations(source_code, request_obj)

print("Result:")
print(res)

with open(TARGET, "w") as f:
    f.write(res)
