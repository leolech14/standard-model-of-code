"""
Core AST Re-compiler using LibCST.
Transforms source code based on AI-generated JSON mutations while preserving exact formatting.
"""
import ast
import json
from typing import List, Dict, Any, Optional
import libcst as cst
from libcst._nodes.expression import Name
from libcst._nodes.statement import FunctionDef, ClassDef
from dataclasses import dataclass, field


@dataclass
class MutationOperation:
    action: str  # "replace_function_body", "delete_node", "replace_class_body"
    target_node: str  # name of the function/class to target
    new_body: Optional[str] = None  # python string containing the new body or entire replacement

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MutationOperation":
        return cls(
            action=data["action"],
            target_node=data["target_node"],
            new_body=data.get("new_body")
        )

@dataclass
class MutationRequest:
    target_file: str
    mutations: List[MutationOperation]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MutationRequest":
        return cls(
            target_file=data["target_file"],
            mutations=[MutationOperation.from_dict(m) for m in data.get("mutations", [])]
        )


class MutationTransformer(cst.CSTTransformer):
    """
    Applies a list of mutations to a libcst.Module.
    """
    def __init__(self, mutations: List[MutationOperation]):
        self.mutations = mutations
        self.applied_count = 0

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.CSTNode | cst.RemovalSentinel:
        func_name = updated_node.name.value

        # Check if there is a mutation targeting this function
        for mut in self.mutations:
            if mut.target_node == func_name:
                if mut.action == "delete_node":
                    self.applied_count += 1
                    return cst.RemoveFromParent()

                elif mut.action == "replace_function_body":
                    if not mut.new_body:
                        continue

                    # Parse the new body snippet into a CST
                    try:
                        # Parse the snippet as a module and get the first statement's body
                        # Since it's provided as `def func():\n ...`, we parse the whole thing
                        parsed_module = cst.parse_module(mut.new_body)
                        new_func_def = parsed_module.body[0]
                        if isinstance(new_func_def, cst.FunctionDef):
                            self.applied_count += 1
                            # Preserve original decorators and whitespace if possible, or fully replace
                            # A cleaner approach is to just extract the new body and apply it to the updated node
                            return updated_node.with_changes(body=new_func_def.body)
                    except Exception as e:
                        print(f"Failed to parse new body for {func_name}: {e}")

        return updated_node

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.CSTNode | cst.RemovalSentinel:
        cls_name = updated_node.name.value

        for mut in self.mutations:
            if mut.target_node == cls_name:
                if mut.action == "delete_node":
                    self.applied_count += 1
                    return cst.RemoveFromParent()

                elif mut.action == "replace_class_body":
                    if not mut.new_body:
                        continue
                    try:
                        parsed_module = cst.parse_module(mut.new_body)
                        new_class_def = parsed_module.body[0]
                        if isinstance(new_class_def, cst.ClassDef):
                            self.applied_count += 1
                            return updated_node.with_changes(body=new_class_def.body)
                    except Exception as e:
                        print(f"Failed to parse new body for {cls_name}: {e}")

        return updated_node

    # You could add generic assign/variable replacements here easily.


class ColliderCompiler:
    """
    Main entry point for AST Re-compilation.
    """

    @staticmethod
    def apply_mutations(source_code: str, request_json: str | dict) -> str:
        """
        Parses source, applies JSON mutations via LibCST, and returns the modified source string.
        """
        if isinstance(request_json, str):
            data = json.loads(request_json)
        else:
            data = request_json

        request = MutationRequest.from_dict(data)

        # JS/TS Dispatcher
        if request.target_file.endswith(('.js', '.ts', '.jsx', '.tsx')):
            import subprocess
            import os
            adapter_path = os.path.join(os.path.dirname(__file__), 'js_adapter', 'index.js')
            data["source_code"] = source_code # Inject into JSON for the node script

            try:
                result = subprocess.run(
                    ['node', adapter_path],
                    input=json.dumps(data).encode('utf-8'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                return result.stdout.decode('utf-8')
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"JS/TS adapter failed: {e.stderr.decode('utf-8')}")

        # Python Dispatcher (LibCST)
        # 1. Parse into LibCST tree
        tree = cst.parse_module(source_code)

        # 2. Apply Transformer
        transformer = MutationTransformer(request.mutations)
        modified_tree = tree.visit(transformer)

        # 3. Regenerate Code String
        return modified_tree.code
