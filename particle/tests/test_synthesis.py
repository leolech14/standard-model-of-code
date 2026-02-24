import pytest
pytest.importorskip("libcst")

from src.core.synthesis.compiler import ColliderCompiler, MutationOperation, MutationRequest

SAMPLE_CODE = """
import logging

class UserSession:
    # A class managing user sessions

    def __init__(self, user_id):
        self.user_id = user_id

    def print_greeting(self):
        # This greeter is very polite
        print(f"Hello User {self.user_id}!")

    def unused_helper(self):
        pass
"""

def test_compiler_initializes():
    compiler = ColliderCompiler()
    assert compiler is not None

def test_delete_node_preserves_formatting():
    payload = {
        "target_file": "dummy.py",
        "mutations": [
            {
                "action": "delete_node",
                "target_node": "unused_helper"
            }
        ]
    }

    modified_code = ColliderCompiler.apply_mutations(SAMPLE_CODE, payload)

    # unused_helper should be gone
    assert "unused_helper" not in modified_code

    # but the rest should be intact, including comments
    assert "# A class managing user sessions" in modified_code
    assert "# This greeter is very polite" in modified_code
    assert "def print_greeting" in modified_code


def test_replace_function_body():
    payload = {
        "target_file": "dummy.py",
        "mutations": [
            {
                "action": "replace_function_body",
                "target_node": "print_greeting",
                "new_body": "def print_greeting(self):\n    print('Hello World')\n    return True\n"
            }
        ]
    }

    modified_code = ColliderCompiler.apply_mutations(SAMPLE_CODE, payload)

    # print_greeting's body should be updated.
    assert "print('Hello World')" in modified_code
    assert "return True" in modified_code

    # Old greeting should be gone
    assert "Hello User" not in modified_code

    # other parts of the class and the class comment should be intact.
    assert "# A class managing user sessions" in modified_code
    assert "def unused_helper" in modified_code

def test_replace_class_body():
    payload = {
        "target_file": "dummy.py",
        "mutations": [
            {
                "action": "replace_class_body",
                "target_node": "UserSession",
                "new_body": "class UserSession:\n    pass\n"
            }
        ]
    }

    modified_code = ColliderCompiler.apply_mutations(SAMPLE_CODE, payload)

    assert "def __init__" not in modified_code
    assert "def print_greeting" not in modified_code
    assert "class UserSession:" in modified_code
