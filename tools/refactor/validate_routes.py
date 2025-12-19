#!/usr/bin/env python3
"""
VALIDATE_ROUTES.PY - Validate extracted route handlers

Scans each extracted route file for:
1. Undefined variables/functions
2. Missing imports
3. References to server.js globals that weren't extracted
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# Known globals from server.js that route handlers might reference
SERVER_JS_GLOBALS = {
    # Constants
    'GRID_TOTAL_SLOTS', 'SHORTCUT_TOTAL_SLOTS', 'ENABLE_MOCKS', 'DISABLE_MOCKS',
    'SERVER_START_MS', 'DIAG_MAX_EVENTS', 'VIZ_CACHE_MAX',
    
    # Imported modules (should be fine)
    'fs', 'fsSync', 'path', 'crypto', 'http',
    
    # Helper functions from server.js
    'sendJson', 'sendText', 'sendCsv', 'sendFile', 'sendApiError',
    'parseBodyJson', 'parseBodyBuffer',
    'nowIso', 'pushDiagEvent', 'clampDiagEvents', 'getDiagEvents',
    'loadDb', 'saveDb', 'withDbMutation', 'normalizeDb',
    'getPluggyConfigFromEnv', 'isPluggyConfigured', 'createPluggyClient',
    'syncItemConnectionById', 'upsertConnectorCache', 'mapPluggyTransactionToLocal',
    'normalizeSlotIndex', 'normalizeShortcutIndex', 'normalizeConnectionStatus',
    'computeDefaultSlotIndex', 'computeDefaultTileLayout', 'computeTileBadges',
    'computePopupSummary', 'computeFinanceSummary',
    'maskSensitive', 'maskIdentifier',
    'mapPopupAccount', 'mapPopupIdentity', 'mapPopupInvestment', 'mapPopupLoan',
    'mapPopupTransaction', 'mapPopupBill',
    'buildRecentMonthWindow', 'buildMockTransactionsForAccount',
    'extractConsentExpiresAt', 'extractPluggyBillId', 'extractPluggyBillIdFromTransaction',
    'vizCacheGet', 'vizCacheSet',
    'parseVizQuery', 'buildVizEventsFromDb', 'buildVizGraphFromDb',
    'buildVizSankeyFromDb', 'buildVizStatementsFromDb', 'buildEntityExport',
    'previewCsv', 'commitCsv', 'buildTemplatesResponse', 'createTemplate',
    'buildAssistantContext', 'runAssistantChat',
    'getTraceId', 'apiMeta', 'asApiError', 'missingParamError', 'invalidJsonError',
    'isMockConnection', 'ensureMockTransactions',
    'runSyncInBackground', 'awaitWithTimeout',
    'chunkArray', 'csvCell', 'pad2', 'formatMonthKeyFromMs',
    'truncateString', 'sanitizeDetail', 'roundMoney',
    'computeBillPayments', 'normalizeConnectionLastErrorMessage',
    
    # Built-ins (ignore these)
    'console', 'process', 'Promise', 'JSON', 'Date', 'Buffer', 'Number', 'String',
    'Array', 'Object', 'Math', 'Error', 'Set', 'Map', 'require', 'module', 'exports',
    '__dirname', '__filename', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
}

# What each extracted route file already imports
ROUTE_FILE_IMPORTS = {
    'sendJson', 'sendText', 'sendCsv', 'sendFile', 'parseBodyJson',
    'nowIso', 'pushDiagEvent',
    'loadDb', 'withDbMutation',
    'getPluggyConfigFromEnv', 'isPluggyConfigured',
    'fsSync', 'path',
    'WEB_ROOT', 'UI_INDEX_PATH', 'HOST', 'PORT', 'DIAG_MAX_EVENTS',
}


def extract_identifiers(code: str) -> set:
    """Extract all identifiers used in the code."""
    # Remove strings and comments first
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'"[^"]*"', '""', code)
    code = re.sub(r"'[^']*'", "''", code)
    code = re.sub(r'`[^`]*`', '``', code)
    
    # Find all identifiers
    identifiers = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code))
    
    # Remove JS keywords
    keywords = {
        'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue',
        'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends', 'false',
        'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let',
        'new', 'null', 'return', 'static', 'super', 'switch', 'this', 'throw',
        'true', 'try', 'typeof', 'undefined', 'var', 'void', 'while', 'with', 'yield',
    }
    
    return identifiers - keywords


def extract_defined_identifiers(code: str) -> set:
    """Extract identifiers that are DEFINED in this file."""
    defined = set()
    
    # const/let/var declarations
    defined.update(re.findall(r'(?:const|let|var)\s+\{([^}]+)\}', code))  # destructuring
    defined.update(re.findall(r'(?:const|let|var)\s+(\w+)\s*=', code))
    
    # Function declarations
    defined.update(re.findall(r'function\s+(\w+)\s*\(', code))
    defined.update(re.findall(r'async\s+function\s+(\w+)\s*\(', code))
    
    # Function parameters
    for match in re.findall(r'function\s+\w+\s*\(([^)]*)\)', code):
        params = [p.strip().split('=')[0].strip() for p in match.split(',')]
        defined.update(p for p in params if p and not p.startswith('{'))
    
    # Arrow function params (simplified)
    defined.update(re.findall(r'\((\w+)(?:,\s*\w+)*\)\s*=>', code))
    
    return defined


def analyze_route_file(filepath: Path) -> dict:
    """Analyze a single route file for missing dependencies."""
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    used = extract_identifiers(code)
    defined = extract_defined_identifiers(code)
    
    # Identifiers that are used but not defined locally and not imported
    potentially_missing = used - defined - ROUTE_FILE_IMPORTS - {'req', 'res', 'url', 'db', 'ctx'}
    
    # Filter to only things that look like they came from server.js
    missing_from_server = potentially_missing & SERVER_JS_GLOBALS
    truly_unknown = potentially_missing - SERVER_JS_GLOBALS - {'true', 'false', 'null', 'undefined'}
    
    return {
        'file': filepath.name,
        'used_count': len(used),
        'defined_count': len(defined),
        'missing_from_server': sorted(missing_from_server),
        'unknown': sorted(truly_unknown)[:10],  # Limit to avoid noise
    }


def main():
    routes_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/lech/PROJECTS_all/PROJECT_atman/ATMAN/refactored/routes")
    
    if not routes_dir.exists():
        print(f"❌ Routes directory not found: {routes_dir}")
        sys.exit(1)
    
    print(f"🔍 Validating routes in: {routes_dir}\n")
    
    all_missing = defaultdict(int)
    files_with_issues = []
    
    for filepath in sorted(routes_dir.glob("*.js")):
        result = analyze_route_file(filepath)
        
        if result['missing_from_server'] or result['unknown']:
            files_with_issues.append(result)
        
        for dep in result['missing_from_server']:
            all_missing[dep] += 1
    
    # Summary
    print("=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\n📁 Files analyzed: {len(list(routes_dir.glob('*.js')))}")
    print(f"⚠️  Files with issues: {len(files_with_issues)}")
    
    print(f"\n🔗 Most commonly missing dependencies:")
    for dep, count in sorted(all_missing.items(), key=lambda x: -x[1])[:15]:
        print(f"   {dep}: used in {count} files")
    
    print(f"\n📋 Files needing attention:")
    for result in files_with_issues[:10]:
        missing = result['missing_from_server'][:5]
        print(f"   {result['file']}: needs {missing}...")
    
    # Generate fix recommendations
    print(f"\n" + "=" * 60)
    print("🔧 RECOMMENDED FIXES")
    print("=" * 60)
    
    top_missing = [dep for dep, _ in sorted(all_missing.items(), key=lambda x: -x[1])[:10]]
    
    print("\nAdd these imports to ALL route files:")
    print("-" * 40)
    
    # Group by likely source module
    by_module = {
        'httpUtils': ['sendApiError'],
        'diagnostics': [],
        'dbSchema': ['normalizeDb'],
        'layoutUtils': ['normalizeSlotIndex', 'normalizeShortcutIndex', 'computeDefaultSlotIndex'],
        'financeUtils': ['maskSensitive', 'maskIdentifier', 'computePopupSummary', 'computeFinanceSummary'],
        'mappers': ['mapPopupAccount', 'mapPopupIdentity', 'mapPopupInvestment', 'mapPopupLoan', 'mapPopupTransaction', 'mapPopupBill'],
        'builders': ['buildRecentMonthWindow', 'buildMockTransactionsForAccount', 'buildAssistantContext'],
        'extractors': ['extractConsentExpiresAt', 'extractPluggyBillId'],
    }
    
    for module, funcs in by_module.items():
        needed = [f for f in funcs if f in top_missing]
        if needed:
            print(f'const {{ {", ".join(needed)} }} = require("../lib/{module}");')


if __name__ == "__main__":
    main()
