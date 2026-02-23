import pytest
import json
from src.core.synthesis.compiler import ColliderCompiler, MutationOperation, MutationRequest

JS_SOURCE = """\
// A simple JS file
class Greeter {
    constructor(name) {
        this.name = name;
    }

    sayHello() {
        console.log("Hello, " + this.name);
    }
}

const myVar = 10;

function unusedHelper() {
    return false;
}
"""

def test_js_delete_function():
    req = {
        "target_file": "dummy.js",
        "mutations": [
            {
                "action": "delete_node",
                "target_node": "unusedHelper"
            }
        ]
    }

    result = ColliderCompiler.apply_mutations(JS_SOURCE, req)

    assert "unusedHelper" not in result
    assert "class Greeter" in result
    assert "const myVar = 10;" in result

def test_js_replace_method():
    req = {
        "target_file": "dummy.js",
        "mutations": [
            {
                "action": "replace_function_body",
                "target_node": "sayHello",
                "new_body": "sayHello() {\n        console.log(`Hola, ${this.name}`);\n    }"
            }
        ]
    }

    result = ColliderCompiler.apply_mutations(JS_SOURCE, req)

    assert "Hola, ${this.name}" in result
    assert "Hello, " not in result
    assert "class Greeter" in result

def test_js_delete_variable():
    req = {
        "target_file": "dummy.js",
        "mutations": [
            {
                "action": "delete_node",
                "target_node": "myVar"
            }
        ]
    }

    result = ColliderCompiler.apply_mutations(JS_SOURCE, req)

    assert "const myVar =" not in result
    assert "10;" not in result
    assert "class Greeter" in result
