#!/usr/bin/env python3
"""
Surface Parity Validator
Enforces architectural consistency across DOM (HTML), Handlers (JS), and Tokens (JSON).
"""

import json
import os
import sys
import re

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def validate_viz_surface(surface_def, root_dir):
    print("Validating Viz Surface Parity...")
    
    # Load files
    html_path = os.path.join(root_dir, "src/core/viz/assets/template.html")
    js_path = os.path.join(root_dir, "src/core/viz/assets/app.js")
    tokens_path = os.path.join(root_dir, "schema/viz/tokens/controls.tokens.json")
    
    if not os.path.exists(html_path):
        print(f"FAIL: HTML not found at {html_path}")
        return False
    if not os.path.exists(js_path):
        print(f"FAIL: JS not found at {js_path}")
        return False
    if not os.path.exists(tokens_path):
        print(f"FAIL: Tokens not found at {tokens_path}")
        return False
        
    html_content = read_file(html_path)
    js_content = read_file(js_path)
    tokens_data = load_json(tokens_path)
    
    contracts = surface_def.get("contracts", {})
    all_passed = True
    
    for contract_name, contract in contracts.items():
        print(f"\nChecking contract: {contract_name} ({contract['type']})")
        items = contract.get("items", [])
        reqs = contract.get("requirements", {})
        
        # Determine items to check
        check_list = items if contract['type'] == 'collection' else [None]
        
        for item in check_list:
            item_passed = True
            debug_name = item if item else contract_name
            
            # Check DOM ID
            if "dom_id" in reqs:
                dom_id = reqs["dom_id"].replace("{item}", item) if item else reqs["dom_id"]
                if f'id="{dom_id}"' not in html_content and f"id='{dom_id}'" not in html_content:
                    print(f"  ❌ DOM: Missing id='{dom_id}' for {debug_name}")
                    item_passed = False
                else:
                    # print(f"  ✅ DOM: Found {dom_id}")
                    pass

            # Check Handler
            if "handler_function" in reqs:
                handler = reqs["handler_function"].replace("{Item}", item.capitalize()) if item else reqs["handler_function"]
                # Regex for function definition or assignment
                # matches: function name(), name = function(), name: function()
                handler_regex = re.compile(rf"(function\s+{handler}\s*\(|{handler}\s*[:=]\s*function|const\s+{handler}\s*=\s*)")
                if not handler_regex.search(js_content):
                    print(f"  ❌ JS: Missing handler '{handler}' for {debug_name}")
                    item_passed = False
                else:
                    # print(f"  ✅ JS: Found {handler}")
                    pass

            # Check Token
            if "token_path" in reqs:
                token_path = reqs["token_path"].replace("{item}", item) if item else reqs["token_path"]
                # Resolve path in json
                parts = token_path.split('.')
                current = tokens_data
                path_found = True
                for part in parts:
                    if part in current:
                        current = current[part]
                    else:
                        path_found = False
                        break
                
                if not path_found:
                    print(f"  ❌ Token: Missing path '{token_path}' for {debug_name}")
                    item_passed = False
                else:
                    # print(f"  ✅ Token: Found {token_path}")
                    pass
            
            if not item_passed:
                all_passed = False
    
    return all_passed

def main():
    root_dir = os.getcwd()
    manifest_path = os.path.join(root_dir, "schema/surfaces/surface.manifest.json")
    
    if not os.path.exists(manifest_path):
        print("FAIL: Manifest not found.")
        sys.exit(1)
        
    manifest = load_json(manifest_path)
    overall_pass = True
    
    for zone_name, zone_info in manifest.get("zones", {}).items():
        if zone_name == "viz":
            def_path = os.path.join(root_dir, zone_info["definition"])
            surface_def = load_json(def_path)
            if not validate_viz_surface(surface_def, root_dir):
                overall_pass = False
    
    if overall_pass:
        print("\n✨ SURFACE PARITY VERIFIED: ALL SYSTEMS MATCH")
        sys.exit(0)
    else:
        print("\n💥 SURFACE PARITY FAILED: MISMATCHES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
