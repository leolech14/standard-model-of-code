#!/usr/bin/env python3
"""
AUTO_REFACTOR_ROUTES.PY - Fully Automated Route Extraction

This script automatically:
1. Parses server.js to find the main request handler
2. Identifies all route blocks (if pathname === "/api/...")
3. Extracts each route to a separate handler file
4. Generates a router module
5. Rewrites server.js to use the new router

Usage:
    python3 auto_refactor_routes.py <server.js> <output_dir>
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def extract_routes_from_handler(source_code: str) -> list:
    """
    Extract all route blocks from the request handler.
    Returns a list of {pathname, method, code, start_line, end_line}
    """
    routes = []
    
    # Pattern to match: if (url.pathname === "/api/something" && req.method === "GET")
    # Or variations with method first, or just pathname
    route_pattern = re.compile(
        r'if\s*\(\s*'
        r'(?:'
        r'url\.pathname\s*===\s*["\']([^"\']+)["\']\s*(?:&&\s*req\.method\s*===\s*["\'](\w+)["\'])?' 
        r'|'
        r'req\.method\s*===\s*["\'](\w+)["\']\s*&&\s*url\.pathname\s*===\s*["\']([^"\']+)["\']'
        r')'
        r'\s*\)'
    )
    
    lines = source_code.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        match = route_pattern.search(line)
        
        if match:
            # Extract pathname and method
            if match.group(1):  # pathname first
                pathname = match.group(1)
                method = match.group(2) or 'ANY'
            else:  # method first
                pathname = match.group(4)
                method = match.group(3) or 'ANY'
            
            # Find the matching closing brace
            start_line = i
            brace_count = line.count('{') - line.count('}')
            end_line = i
            
            for j in range(i + 1, len(lines)):
                brace_count += lines[j].count('{') - lines[j].count('}')
                if brace_count <= 0:
                    end_line = j
                    break
            
            # Extract the code block
            code_lines = lines[start_line:end_line + 1]
            
            routes.append({
                'pathname': pathname,
                'method': method,
                'code': '\n'.join(code_lines),
                'start_line': start_line + 1,
                'end_line': end_line + 1,
                'handler_name': pathname_to_handler_name(pathname, method)
            })
            
            i = end_line + 1
        else:
            i += 1
    
    return routes


def pathname_to_handler_name(pathname: str, method: str) -> str:
    """Convert /api/foo/bar to handleApiFooBar"""
    # Remove leading slash and split, sanitize special chars
    clean = re.sub(r'[^a-zA-Z0-9/]', '_', pathname)
    parts = clean.strip('/').split('/')
    # CamelCase each part
    camel = ''.join(p.capitalize() for p in parts if p)
    method_prefix = method.capitalize() if method != 'ANY' else ''
    return f"handle{method_prefix}{camel}"


def pathname_to_filename(pathname: str) -> str:
    """Convert /api/foo/bar to api_foo_bar.js"""
    # Sanitize special characters
    clean = re.sub(r'[^a-zA-Z0-9/]', '_', pathname)
    parts = clean.strip('/').split('/')
    return '_'.join(parts) + '.js'


def generate_route_handler_file(route: dict) -> str:
    """Generate a standalone route handler module."""
    handler_name = route['handler_name']
    
    return f'''/**
 * Route Handler: {route['method']} {route['pathname']}
 * Auto-extracted from server.js
 */

// Shared imports (adjust paths as needed)
const {{ sendJson, sendText, sendCsv, sendFile, parseBodyJson }} = require("../lib/httpUtils");
const {{ nowIso, pushDiagEvent }} = require("../lib/diagnostics");
const {{ loadDb, withDbMutation }} = require("../lib/jsonDb");
const {{ getPluggyConfigFromEnv, isPluggyConfigured }} = require("../pluggy/pluggyClient");
const fsSync = require("fs");
const path = require("path");

// Constants (should be centralized)
const WEB_ROOT = process.env.WEB_ROOT || path.join(__dirname, "..", "..", "ro-finance", "dist");
const UI_INDEX_PATH = path.join(WEB_ROOT, "index.html");
const HOST = process.env.HOST || "127.0.0.1";
const PORT = process.env.PORT || 3001;
const DIAG_MAX_EVENTS = Number(process.env.DIAG_MAX_EVENTS || 200);

async function {handler_name}(req, res, url, db, ctx) {{
  // Original code from server.js lines {route['start_line']}-{route['end_line']}
  
{indent_code(extract_handler_body(route['code']), 2)}
}}

module.exports = {{ {handler_name} }};
'''


def extract_handler_body(code: str) -> str:
    """Extract the body of an if block (remove the if wrapper)."""
    lines = code.split('\n')
    if len(lines) < 2:
        return code
    
    # Remove first line (if statement) and last line (closing brace)
    body_lines = lines[1:-1] if len(lines) > 2 else lines[1:]
    
    # Remove one level of indentation
    dedented = []
    for line in body_lines:
        if line.startswith('    '):
            dedented.append(line[4:])
        elif line.startswith('  '):
            dedented.append(line[2:])
        else:
            dedented.append(line)
    
    return '\n'.join(dedented)


def indent_code(code: str, spaces: int) -> str:
    """Add indentation to code block."""
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line.strip() else line for line in code.split('\n'))


def generate_router_module(routes: list) -> str:
    """Generate the main router module."""
    imports = []
    route_table = []
    
    for route in routes:
        filename = pathname_to_filename(route['pathname'])
        handler = route['handler_name']
        imports.append(f'const {{ {handler} }} = require("./routes/{filename.replace(".js", "")}");')
        route_table.append(f'  ["{route["method"]}", "{route["pathname"]}", {handler}],')
    
    return f'''/**
 * ROUTER - Auto-generated route registry
 * 
 * This module provides a simple router that maps URL patterns to handlers.
 */

// Import all route handlers
{chr(10).join(imports)}

// Route table: [method, pathname, handler]
const ROUTES = [
{chr(10).join(route_table)}
];

/**
 * Find and execute the matching route handler.
 */
async function handleRequest(req, res, url, db, ctx) {{
  const method = req.method;
  const pathname = url.pathname;
  
  for (const [routeMethod, routePathname, handler] of ROUTES) {{
    if ((routeMethod === "ANY" || routeMethod === method) && routePathname === pathname) {{
      return await handler(req, res, url, db, ctx);
    }}
  }}
  
  // No matching route
  return null;
}}

module.exports = {{
  handleRequest,
  ROUTES,
}};
'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_refactor_routes.py <server.js> [output_dir]")
        sys.exit(1)
    
    source_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else source_file.parent / "refactored"
    routes_dir = output_dir / "routes"
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    routes_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔬 Analyzing: {source_file}")
    print(f"📁 Output: {output_dir}")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Extract routes
    print("🛤️  Extracting routes...")
    routes = extract_routes_from_handler(source_code)
    
    print(f"📊 Found {len(routes)} routes:")
    for route in routes:
        print(f"   {route['method']:6} {route['pathname']}")
    
    # Generate individual route files
    print("\n💾 Generating route handler files:")
    for route in routes:
        filename = pathname_to_filename(route['pathname'])
        filepath = routes_dir / filename
        content = generate_route_handler_file(route)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   📄 routes/{filename}")
    
    # Generate router module
    router_path = output_dir / "router.js"
    router_content = generate_router_module(routes)
    
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(router_content)
    
    print(f"   📄 router.js")
    
    # Calculate metrics
    total_lines = sum(route['end_line'] - route['start_line'] + 1 for route in routes)
    
    print(f"\n✅ Extraction Complete!")
    print(f"   📤 Extracted: {len(routes)} routes ({total_lines} lines)")
    print(f"   📦 Generated: {len(routes) + 1} files")
    print(f"\n📋 Next step: Replace the if/else chain in server.js with:")
    print(f'   const {{ handleRequest }} = require("./refactored/router");')
    print(f'   // In request handler: const handled = await handleRequest(req, res, url, db, ctx);')


if __name__ == "__main__":
    main()
