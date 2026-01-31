# API Audit: File Explorer (file_explorer.py)

**Date:** 2026-01-31
**File:** `/Users/lech/PROJECTS_all/PROJECT_elements/tools/file_explorer.py`
**Scope:** HTTP endpoint design, request/response formats, error handling, authentication

---

## Executive Summary

The File Explorer exposes 20 HTTP endpoints through a SimpleHTTPRequestHandler. While the implementation is functional, there are significant **API design inconsistencies**, **error handling gaps**, and **missing documentation** that violate REST principles and create maintenance/debugging challenges.

**Critical Issues:**
- All endpoints return HTTP 200 with success/error in JSON body (breaks HTTP semantics)
- Inconsistent error response structures across endpoints
- No OpenAPI/Swagger documentation
- Weak query parameter validation
- Inconsistent naming conventions (kebab-case vs snake_case)
- Missing HTTP status codes for specific error conditions
- No request/response schemas validation

---

## API Endpoints Overview

### Authentication
- `GET /auth` - Biometric authentication endpoint

### GET Endpoints (Read-Only, Mostly)
| Endpoint | Method | Purpose | Issues |
|----------|--------|---------|--------|
| `/` | GET | Serve main HTML UI | OK |
| `/api/list` | GET | List directory contents | Weak param validation |
| `/api/folder-preview` | GET | Preview folder structure | Weak param validation |
| `/api/preview` | GET | Get file preview (2KB) | Returns 200 on errors |
| `/api/content` | GET | Get full file content | Returns 200 on errors |
| `/api/open` | GET | Open file with default app | Returns 200 on errors |
| `/file/{path}` | GET | Download/serve file | Proper error codes used |

### POST Endpoints (Mutation)
| Endpoint | Method | Purpose | Issues |
|----------|--------|---------|--------|
| `/api/paste` | POST | Copy/cut/paste files | Returns 200 on errors |
| `/api/delete` | POST | Delete files to trash | Returns 200 on errors |
| `/api/undo` | POST | Undo last action | Returns 200 on errors |
| `/api/redo` | POST | Redo last undone action | Returns 200 on errors |
| `/api/history-status` | POST | Get undo/redo status | Returns 200 on errors |
| `/api/create-folder` | POST | Create new folder | Returns 200 on errors |
| `/api/rename` | POST | Rename file/folder | Returns 200 on errors |
| `/api/duplicate` | POST | Duplicate file/folder | Returns 200 on errors |
| `/api/compress` | POST | Create ZIP archive | Returns 200 on errors |
| `/api/move-items` | POST | Move files to destination | Returns 200 on errors |
| `/api/open-with-app` | POST | Open files with specific app | Returns 200 on errors |
| `/api/create-folder-with-items` | POST | Create folder and move items | Returns 200 on errors |
| `/api/extract-archive` | POST | Extract ZIP/TAR archives | Returns 200 on errors |
| `/api/upload` | POST | Multipart file upload | Returns 200 on errors |

---

## Detailed Findings

### 1. REST API Design Violations

#### Issue 1.1: HTTP Status Code Inconsistency (CRITICAL)

**Problem:** All endpoints return HTTP 200 OK regardless of success or failure. Success/error state is communicated via JSON body only.

**Example - `/api/paste` endpoint:**
```python
# Line 6829-6833
self.send_json({
    'success': len(errors) == 0,
    'count': count,
    'errors': errors
})
```

This returns `200 OK` even when errors occurred.

**Impact:**
- HTTP clients/proxies/CDNs cannot cache properly (all responses are "successful")
- Status monitoring tools cannot detect failures
- Standard HTTP error handling by browsers/clients fails
- Inconsistent with REST principles (RFC 7231, RFC 9110)

**Expected Standard:**
```
GET /api/list?path=/invalid → 404 Not Found
POST /api/create-folder with invalid data → 400 Bad Request
POST /api/delete access denied → 403 Forbidden
POST /api/upload file too large → 413 Payload Too Large
```

**Current Behavior:**
```
All → 200 OK with {"success": false, "error": "message"}
```

---

#### Issue 1.2: Inconsistent Error Response Structures (HIGH)

**Problem:** Different endpoints return different error structures.

**Pattern 1 - Most endpoints:**
```json
{"success": false, "error": "message"}
```

**Pattern 2 - Undo/redo endpoints (line 6888):**
```json
{
  "success": false,
  "error": "message",
  "canUndo": false,
  "canRedo": true
}
```

**Pattern 3 - Preview endpoints (line 6689):**
```json
{"error": "Access denied"}
```
No `success` field.

**Pattern 4 - Open file (line 6736):**
```json
{"ok": true}
```
Uses `ok` instead of `success`.

**Problem Examples:**

File `send_preview()` (line 6689):
```python
if file_path is None:
    self.send_json({'error': 'Access denied'})  # No 'success' field
    return
```

File `open_file()` (line 6736):
```python
subprocess.run(['open', str(file_path)], check=True)
self.send_json({'ok': True})  # Uses 'ok' not 'success'
```

**Impact:**
- Clients must handle 4+ different response schemas
- Impossible to standardize error handling
- Testing/validation becomes complex
- Breaking changes if standardized later

**Solution Required:**
Unified error schema:
```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Invalid folder name",
    "details": {}
  }
}
```

---

### 2. Request Validation & Parameter Handling

#### Issue 2.1: Weak Query Parameter Parsing (MEDIUM)

**Problem:** Query parameters have minimal validation.

**Example - `/api/folder-preview` (line 6493-6495):**
```python
qs = parse_qs(path.split('?')[1]) if '?' in path else {}
dir_path = qs.get('path', [''])[0]
limit = int(qs.get('limit', ['10'])[0])  # ← No bounds check
depth = int(qs.get('depth', ['1'])[0])   # ← No bounds check
```

**Risks:**
- `limit=-1000000` causes memory exhaustion
- `depth=999` causes infinite recursion
- No type coercion validation (what if client sends string "abc"?)
- Silent failures with `int()` conversion

**Example Attack:**
```
GET /api/folder-preview?path=/&limit=999999&depth=100
```

**Missing Validation:**
```python
# Should validate:
if not isinstance(limit, int) or limit < 0 or limit > 1000:
    return error_response(400, "limit must be 0-1000")
if not isinstance(depth, int) or depth < 0 or depth > 10:
    return error_response(400, "depth must be 0-10")
```

---

#### Issue 2.2: JSON Body Parsing Lacks Error Handling (MEDIUM)

**Problem:** JSON parsing silently fails at line 6532.

```python
content_length = int(self.headers.get('Content-Length', 0))
body = self.rfile.read(content_length)
data = json.loads(body) if body else {}  # ← Can raise JSONDecodeError
```

**Scenarios:**
- Malformed JSON → `JSONDecodeError` uncaught → 500 error
- No error message returned to client
- Server crashes silently

**Should be:**
```python
try:
    data = json.loads(body) if body else {}
except json.JSONDecodeError as e:
    self.send_json({'success': False, 'error': f'Invalid JSON: {str(e)}'}, 400)
    return
```

---

#### Issue 2.3: Missing Content-Length Limits (MEDIUM)

**Problem:** No validation of `Content-Length` header.

```python
content_length = int(self.headers.get('Content-Length', 0))
body = self.rfile.read(content_length)  # ← Could be 1GB+
data = json.loads(body)  # ← Entire payload in memory
```

**Risk:** OOM attack with large POST body.

**Missing:**
```python
MAX_JSON_PAYLOAD = 10 * 1024 * 1024  # 10MB
if content_length > MAX_JSON_PAYLOAD:
    self.send_response(413)
    self.end_headers()
    return
```

---

### 3. Endpoint-Specific Issues

#### Issue 3.1: `/api/preview` and `/api/content` Return Wrong Status (HIGH)

**Lines 6685-6724:**

```python
def send_preview(self, path_str):
    file_path = validate_path(path_str)
    if file_path is None:
        self.send_json({'error': 'Access denied'})  # ← Should be 403
        return
    if not file_path.exists() or not file_path.is_file():
        self.send_json({'error': 'Not found'})      # ← Should be 404
        return
```

Both return HTTP 200 OK when they should return:
- `403 Forbidden` for access denied
- `404 Not Found` for missing files

**Contrast with `/file/{path}` (line 6743-6746):**
```python
def serve_file(self, path_str):
    if file_path is None:
        self.send_error(403, "Access denied")  # ✓ Correct
        return
    if not file_path.exists() or not file_path.is_file():
        self.send_error(404)                   # ✓ Correct
        return
```

**This endpoint does it RIGHT.**

---

#### Issue 3.2: Bare `except` Clauses (MEDIUM)

**Line 6699:**
```python
try:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read(2000)
except:  # ← Bare except - catches KeyboardInterrupt, SystemExit, etc.
    self.send_json({'error': 'Cannot read'})
```

**Problems:**
- Hides bugs (catches `SystemExit`, `KeyboardInterrupt`, etc.)
- Generic error "Cannot read" doesn't help debug
- Server-side errors not logged

**Should be:**
```python
except (IOError, OSError) as e:
    logger.error(f"Failed to read {file_path}: {e}")
    self.send_json({'success': False, 'error': 'Cannot read file'}, 400)
```

---

#### Issue 3.3: Multipart Upload Has No Size Validation (HIGH)

**Lines 7466-7572:**

```python
def handle_upload(self):
    content_length = int(self.headers.get('Content-Length', 0))
    # ... no bounds check ...
    body = self.rfile.read(content_length)  # ← Can read 10GB
    # ... save to disk ...
    with open(dest_file, 'wb') as f:
        f.write(content)  # ← Unbounded file write
```

**Risk:** An attacker can upload terabyte-sized files.

**Missing:**
```python
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB limit
if content_length > MAX_UPLOAD_SIZE:
    self.send_json({'success': False, 'error': 'File too large'}, 413)
    return
```

Note: `serve_file()` has this check (line 6753) but `handle_upload()` doesn't.

---

#### Issue 3.4: Unsafe Multipart Parsing (MEDIUM)

**Lines 7485-7530:**

```python
body = self.rfile.read(content_length)
boundary_bytes = ('--' + boundary).encode()
parts = body.split(boundary_bytes)  # ← Simple string split, not RFC 2388 compliant

for part in parts:
    # ... parse manually ...
    header_section, content = part.split(b'\r\n\r\n', 1)  # ← Assumes exactly one split
```

**Problems:**
- Doesn't handle RFC 2388 properly (multipart/form-data standard)
- Assumes specific CRLF line endings
- No handling of nested multipart
- Manual parsing is error-prone

**Should use:**
```python
from email import message_from_bytes
from urllib.parse import parse_qs
```

Or better: use a proper multipart library like `python-multipart`.

---

#### Issue 3.5: Path Traversal Complexity (MEDIUM)

**Lines 82-107:**

The `validate_path()` function is complex:

```python
def validate_path(path_str: str) -> Path | None:
    if BROWSE_ROOT is None:
        return None
    if not path_str:
        return BROWSE_ROOT

    if path_str.startswith('/'):
        resolved = Path(path_str).resolve()  # ← Absolute path from user?
    else:
        resolved = (BROWSE_ROOT / path_str.lstrip('/')).resolve()

    try:
        resolved.relative_to(BROWSE_ROOT)  # ← Security check
        return resolved
    except ValueError:
        return None
```

**Issues:**
- If `path_str` is absolute (`/etc/passwd`), it tries to resolve outside BROWSE_ROOT
- The function rejects it, but the logic is confusing
- Better approach: always assume relative paths

**Should be:**
```python
def validate_path(path_str: str) -> Path | None:
    if not path_str:
        return BROWSE_ROOT

    # Remove leading slashes and resolve relative to root
    safe_path = (BROWSE_ROOT / path_str.lstrip('/')).resolve()

    # Ensure within bounds
    try:
        safe_path.relative_to(BROWSE_ROOT)
        return safe_path
    except ValueError:
        return None  # Outside allowed root
```

---

### 4. Response Format Inconsistencies

#### Issue 4.1: Success Response Structures Vary (MEDIUM)

Some endpoints return minimal data:
```json
{"success": true}
```

Others return detailed data:
```json
{
  "success": true,
  "path": "/Users/.../NewFile.txt",
  "name": "NewFile.txt",
  "moved": 5,
  "errors": []
}
```

**Example Variations:**

`/api/create-folder` (line 7057-7060):
```json
{
  "success": true,
  "path": "...",
  "name": "..."
}
```

`/api/paste` (line 6829-6833):
```json
{
  "success": true,
  "count": 3,
  "errors": []
}
```

`/api/open-with-app` (line 7307):
```json
{"success": true}
```

**Impact:** Clients cannot standardize response parsing.

---

#### Issue 4.2: Error Array Format Inconsistent (MEDIUM)

**Pattern A - `/api/paste` (line 6832):**
```json
{"errors": ["file.txt: access denied", "other.txt: not found"]}
```

**Pattern B - `/api/move-items` (line 7276):**
```json
{"errors": ["Access denied: /path/to/file", "Not found: /path/to/file"]}
```

**Pattern C - `/api/upload` (line 7571):**
```json
{"errors": ["Invalid target directory for file.txt", "Failed to save file.zip: ..."]}
```

Same field name, different message formats.

**Should be:**
```json
{
  "errors": [
    {
      "code": "access_denied",
      "message": "Access denied",
      "path": "/path/to/file"
    }
  ]
}
```

---

### 5. Missing API Documentation

#### Issue 5.1: No OpenAPI/Swagger Spec (HIGH)

**Missing:**
- OpenAPI 3.0 or 3.1 specification
- No endpoint documentation
- No request/response schemas
- No authentication documentation
- No error code documentation

**Required OpenAPI endpoints:**
```yaml
GET /openapi.json or /api-docs/openapi.json
GET /docs  # Swagger UI
GET /redoc  # ReDoc UI
```

---

#### Issue 5.2: No Inline Documentation (MEDIUM)

Most handlers lack docstrings with request/response specs:

```python
def handle_paste(self, data):
    """Handle copy/cut paste operation with undo support."""
    # ↑ No request/response schema documented
```

**Should be:**

```python
def handle_paste(self, data):
    """Handle copy/cut paste operation with undo support.

    Request:
        {
            "files": ["path/to/file1", "path/to/file2"],
            "target": "destination/folder",
            "operation": "copy" | "cut"
        }

    Response (success):
        {
            "success": true,
            "count": 2,
            "errors": []
        }

    Response (error):
        {
            "success": false,
            "error": "message",
            "count": 0,
            "errors": [...]
        }

    HTTP Status Codes:
        200: Operation attempted (check 'success' field)
        400: Invalid request
        401: Not authenticated
        403: Access denied
        500: Server error
    """
```

---

### 6. Authentication & Authorization

#### Issue 6.1: Cookie-Based Auth is Weak (MEDIUM)

**Lines 6410-6423:**

```python
def check_auth(self) -> bool:
    global AUTH_TOKEN, AUTH_VERIFIED
    if not AUTH_VERIFIED:
        return False

    cookies = self.headers.get('Cookie', '')
    for cookie in cookies.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            if name == 'fe_auth' and value == AUTH_TOKEN:
                return True
    return False
```

**Problems:**
1. Token stored in global variable (lost on server restart)
2. No token expiration
3. No CSRF protection (token not verified against request origin)
4. All users share same token (global `AUTH_TOKEN`)
5. No logging of auth attempts

---

#### Issue 6.2: POST Auth Check Different from GET (MEDIUM)

**GET handler (line 6478):**
```python
if not self.check_auth():
    self.send_auth_required()  # Returns HTML page
    return
```

**POST handler (line 6515-6520):**
```python
if not self.check_auth():
    self.send_response(401)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(b'{"error": "Authentication required"}')
    return
```

**Problems:**
- Inconsistent response formats
- POST returns raw `{"error": ...}` not `{"success": false, "error": ...}`
- Hard-coded response in do_POST instead of using `send_json()`

**Should be:**
```python
def send_unauthorized(self, accept_type='application/json'):
    if 'text/html' in accept_type:
        self.send_auth_required()
    else:
        self.send_json({'success': False, 'error': 'Authentication required'}, 401)
```

---

### 7. Naming Convention Inconsistencies

#### Issue 7.1: Mixed Naming (MEDIUM)

**Endpoint paths:**
- `/api/list` (verb-noun)
- `/api/preview` (verb-noun)
- `/api/create-folder` (kebab-case)
- `/api/move-items` (kebab-case)
- `/api/open-with-app` (kebab-case)
- `/api/create-folder-with-items` (kebab-case)

**JSON response fields:**
- `success` (camelCase)
- `count` (camelCase)
- `moved` (camelCase)
- `errors` (camelCase)
- But also:
  - `canUndo`, `canRedo` (camelCase, OK)
  - `archivePath` (camelCase, OK)

**JSON request fields:**
- `files` (snake_case in comments, camelCase in code)
- `parentPath` (camelCase)
- `itemPaths` (camelCase)
- `folderName` (camelCase)
- `targetDir` (camelCase)

**Recommendation:**
- Endpoints: Use `/api/v1/files/list` (REST noun-based)
- JSON: Consistent camelCase (already mostly done)

---

### 8. Missing Functionality/Gaps

#### Issue 8.1: No Rate Limiting (MEDIUM)

**Risk:** Attackers can:
- Brute-force file operations
- Crash server with rapid requests
- DOS with large operations

**Missing:**
```python
# Per-endpoint rate limiting
# Per-IP rate limiting
# Per-action rate limiting (e.g., 10 deletes/minute)
```

---

#### Issue 8.2: No Audit Logging (MEDIUM)

**Missing:**
- No logging of file operations
- No audit trail of who deleted what
- No tracking of failed auth attempts
- No API request logging (except: line 7586 suppresses it)

**Line 7586:**
```python
def log_message(self, format: str, *args):
    """Suppress HTTP request logging."""
    pass
```

This intentionally suppresses all HTTP request logging!

---

#### Issue 8.3: No Pagination for `/api/list` (MEDIUM)

**Problem:** If directory has 10,000 files, all returned in one response.

**Missing:**
```
GET /api/list?path=/&offset=0&limit=100
```

Instead of returning all files.

---

#### Issue 8.4: No Batch Operations (MEDIUM)

All delete/move/copy operations are per-request, no batch endpoints.

**Missing:**
```
POST /api/batch
{
  "operations": [
    {"op": "delete", "path": "file1.txt"},
    {"op": "move", "from": "file2.txt", "to": "dest/"},
    {"op": "copy", "from": "file3.txt", "to": "file3_copy.txt"}
  ]
}
```

---

### 9. Security Concerns

#### Issue 9.1: Exception Messages Leak Information (LOW)

**Lines throughout:**
```python
except Exception as e:
    self.send_json({'success': False, 'error': str(e)})
```

Full exception strings returned to client. Examples:
- Permission denied: `/Users/secret/.ssh` → reveals directory structure
- File already exists: reveals filename of existing files
- Symbolic link info: reveals OS structure

**Should be:**
```python
except (IOError, OSError) as e:
    logger.error(f"Operation failed: {e}")
    self.send_json({'success': False, 'error': 'Operation failed'}, 400)
```

---

#### Issue 9.2: No CORS Headers (MEDIUM)

If UI and API hosted separately, no CORS headers set.

**Missing:**
```python
self.send_header('Access-Control-Allow-Origin', 'https://trusted-domain.com')
self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
```

---

#### Issue 9.3: No HTTPS Enforcement (MEDIUM)

Server runs on HTTP only. Auth tokens sent in plaintext.

**Missing:**
```python
# Should enforce HTTPS or at least warn
if not self.request.is_secure():
    logger.warning("Auth token sent over HTTP!")
```

---

## Summary of Issues by Severity

### Critical (1)
1. HTTP status codes always 200 (breaks REST semantics)

### High (5)
1. Inconsistent error response structures
2. Query parameter validation gaps
3. `/api/preview` and `/api/content` wrong status codes
4. Multipart upload unbounded size
5. No OpenAPI documentation

### Medium (12)
1. JSON parsing lacks error handling
2. Missing Content-Length limits for JSON
3. Bare `except` clauses
4. Unsafe multipart parsing
5. Path validation logic confusing
6. Success response structures inconsistent
7. Error array format inconsistent
8. Cookie auth is weak
9. POST auth check different from GET
10. Mixed naming conventions
11. No rate limiting
12. No audit logging

### Low (3)
1. Exception messages leak information
2. No CORS headers
3. No HTTPS enforcement

---

## Recommendations Priority

### Phase 1: Critical Fixes (Blocking)
```
1. Implement proper HTTP status codes
   - 400 Bad Request for validation errors
   - 401 Unauthorized for auth failures
   - 403 Forbidden for access denied
   - 404 Not Found for missing resources
   - 409 Conflict for name collisions
   - 413 Payload Too Large for oversized uploads
   - 500 Internal Server Error for server errors

2. Standardize error response format
   {
     "success": false,
     "error": {
       "code": "error_code",
       "message": "human readable message"
     }
   }

3. Create OpenAPI 3.1 specification
   - Document all 20 endpoints
   - Define request/response schemas
   - Include error responses
   - Auto-generate Swagger UI
```

### Phase 2: High Priority (Weeks 1-2)
```
1. Add input validation
   - Query parameter bounds
   - JSON schema validation
   - File size limits

2. Fix multipart handling
   - Use proper multipart library
   - Validate upload sizes

3. Unified response handlers
   - send_json(data, status_code)
   - send_error(code, message, status_code)
```

### Phase 3: Medium Priority (Weeks 3-4)
```
1. Authentication improvements
   - Token expiration
   - Per-user tokens
   - CSRF protection

2. Logging
   - Request logging
   - Audit trail
   - Error tracking

3. Rate limiting
   - Per-IP rate limiting
   - Per-endpoint limiting
```

### Phase 4: Polish (Optional)
```
1. CORS headers
2. Pagination for large results
3. Batch operations API
4. Better error messages
```

---

## Recommended API Design Pattern

Here's the pattern to apply consistently:

```python
class APIResponse:
    """Unified response format."""

    def success(data=None, **kwargs):
        return {
            'success': True,
            'data': data or {},
            **kwargs
        }

    def error(code, message, status=400, details=None):
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details or {}
            }
        }, status

# Usage:
if not validate_path(path):
    return self.send_json(*APIResponse.error(
        'access_denied',
        'Access denied to that path',
        status=403
    ))

if success:
    return self.send_json(APIResponse.success(
        data={'path': str(new_path), 'name': new_path.name},
        count=1
    ), status=201)
```

---

## Files Needing Updates

1. **file_explorer.py** - Main implementation
   - Lines 6449-7585 (do_GET, do_POST, handlers)
   - Lines 6410-6447 (auth methods)
   - Lines 7574-7584 (response helpers)

2. **New file: openapi.yaml** - API specification
   - 20 endpoints documented
   - Request/response schemas
   - Error responses

3. **New file: API_DESIGN.md** - Developer guide
   - Best practices
   - Response format standard
   - Error handling
   - Examples

---

## Conclusion

The File Explorer API works functionally but violates REST principles and creates technical debt. The primary issue is **HTTP 200 for all responses**, which breaks HTTP semantics and standard error handling.

Fixing the critical and high-priority issues (Phase 1-2) would make this a production-ready API. Current state is suitable only for internal tools.

**Estimated effort:** 40-60 hours for comprehensive remediation.
