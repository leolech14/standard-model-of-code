# File Explorer API - Quick Reference

**Last Audit:** 2026-01-31
**Critical Issues:** 1 | **High:** 5 | **Medium:** 12 | **Low:** 3

---

## Critical Issue Summary

### The Main Problem: All Responses Return HTTP 200

Currently, ALL endpoints return HTTP 200 OK, even when they fail:

```
POST /api/create-folder → 200 OK {"success": false, "error": "..."}
POST /api/delete (access denied) → 200 OK {"success": false, "error": "Access denied"}
GET /api/preview (file not found) → 200 OK {"error": "Not found"}
POST /api/upload (file too large) → 200 OK {"success": false, "error": "..."}
```

**Why it matters:**
- HTTP clients expect 4xx/5xx for failures
- Caching proxies treat all responses as success
- Standard error handling breaks
- Violates REST principles

**The fix:**
```
POST /api/create-folder → 201 Created on success
POST /api/create-folder → 400 Bad Request on validation error
GET /api/preview (not found) → 404 Not Found
POST /api/upload (too large) → 413 Payload Too Large
```

---

## Quick Wins (Priority Fixes)

### 1. Standardize Response Format (ASAP)

All error responses should follow this pattern:

```json
{
  "success": false,
  "error": {
    "code": "error_code_name",
    "message": "Human readable message",
    "details": {}
  }
}
```

Currently, variations exist:
- `{"success": false, "error": "message"}` ← Most common
- `{"error": "message"}` ← No success field
- `{"ok": true}` ← Uses "ok" instead of "success"

**Estimated effort:** 4 hours

---

### 2. Fix HTTP Status Codes (HIGH PRIORITY)

Create unified helper:

```python
def send_api_error(self, code: str, message: str, status: int = 400):
    response = {
        'success': False,
        'error': {'code': code, 'message': message}
    }
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(response).encode())
```

Use in all handlers:

```python
# Before
if file_path is None:
    self.send_json({'error': 'Access denied'})
    return

# After
if file_path is None:
    return self.send_api_error('access_denied', 'Access denied', status=403)
```

**Estimated effort:** 10 hours

---

### 3. Add Input Validation (MEDIUM)

Add bounds checking to prevent abuse:

```python
# Before: No validation
limit = int(qs.get('limit', ['10'])[0])  # Can be -1000000

# After: With bounds
limit = int(qs.get('limit', ['10'])[0])
if limit < 1 or limit > 1000:
    return self.send_api_error('invalid_limit', 'limit must be 1-1000', 400)
```

**Estimated effort:** 6 hours

---

## Endpoint Issues by Severity

### CRITICAL (Fix immediately)

**Issue:** All endpoints return HTTP 200 regardless of failure

| Endpoint | Current | Should Be |
|----------|---------|-----------|
| `/api/create-folder` (validation fail) | 200 | 400 |
| `/api/preview` (not found) | 200 | 404 |
| `/api/preview` (access denied) | 200 | 403 |
| `/api/delete` (access denied) | 200 | 403 |
| `/api/upload` (file too large) | 200 | 413 |

---

### HIGH (Fix in Phase 1)

#### 1. Inconsistent Error Response Structures

**Locations:** All error responses

```python
# Pattern A (most endpoints)
{'success': False, 'error': 'message'}

# Pattern B (undo/redo)
{'success': False, 'error': 'msg', 'canUndo': False, 'canRedo': True}

# Pattern C (preview)
{'error': 'message'}  # No 'success' field!

# Pattern D (open)
{'ok': True}  # Uses 'ok' not 'success'!
```

**Fix:** Use unified format everywhere

---

#### 2. Query Parameter Validation Missing

**Location:** `do_GET` lines 6493-6495

```python
limit = int(qs.get('limit', ['10'])[0])  # ← No bounds!
depth = int(qs.get('depth', ['1'])[0])   # ← No bounds!
```

**Risk:** Memory exhaustion with `limit=999999999`

**Fix:** Add bounds checking
```python
limit = int(qs.get('limit', ['10'])[0])
if not (1 <= limit <= 1000):
    return self.send_json({'success': False, 'error': 'limit must be 1-1000'}, 400)
```

---

#### 3. JSON Parsing Error Not Handled

**Location:** `do_POST` line 6532

```python
data = json.loads(body) if body else {}  # ← Can raise JSONDecodeError!
```

**Fix:**
```python
try:
    data = json.loads(body) if body else {}
except json.JSONDecodeError as e:
    return self.send_json(
        {'success': False, 'error': f'Invalid JSON: {str(e)}'},
        400
    )
```

---

#### 4. No Upload Size Limit

**Location:** `handle_upload` line 7485

```python
body = self.rfile.read(content_length)  # ← No limit!
```

**Risk:** Attacker uploads 1TB file, crashes server

**Note:** `/file/` endpoint HAS this check (line 6753) but upload doesn't!

**Fix:**
```python
MAX_UPLOAD = 500 * 1024 * 1024  # 500MB
if content_length > MAX_UPLOAD:
    return self.send_json(
        {'success': False, 'error': 'File too large'},
        413
    )
```

---

#### 5. No OpenAPI/Swagger Documentation

**Missing:** `/openapi.json`, `/docs`, `/redoc`

**Impact:** Clients must reverse-engineer API from code

**Fix:** Generate OpenAPI 3.1 spec (see `API_REFACTORING_PLAN.md`)

---

### MEDIUM (Fix in Phase 2-3)

| Issue | Location | Impact | Effort |
|-------|----------|--------|--------|
| Bare `except` clauses | Lines 6699, 7461 | Hides bugs | 2h |
| Unsafe multipart parsing | Lines 7485-7530 | RFC 2388 non-compliant | 3h |
| Cookie auth is weak | Lines 6410-6423 | No expiry, global token | 4h |
| POST auth inconsistent | Lines 6515-6520 | Different format than GET | 1h |
| No rate limiting | N/A | DOS possible | 6h |
| No audit logging | N/A | No trail of actions | 4h |
| Inconsistent success responses | Various | Client confusion | 3h |

---

## Testing Checklist

Before and after refactoring, verify:

- [ ] GET endpoints with invalid paths return 404 not 200
- [ ] POST endpoints with validation errors return 400 not 200
- [ ] Access denied returns 403 not 200
- [ ] File too large returns 413 not 200
- [ ] Successful creation returns 201
- [ ] All error responses have `success: false`
- [ ] All error responses have `error.code` and `error.message`
- [ ] Query parameters validated (limit, depth, offset)
- [ ] JSON request bodies validated
- [ ] Content-Length checked before reading
- [ ] Auth works for both GET and POST
- [ ] Multipart upload has size limits
- [ ] All bare `except` replaced with specific exceptions

---

## Code Locations to Update

**Priority order:**

1. **Lines 6400-6447:** Auth methods
   - Add `require_auth()` wrapper
   - Fix inconsistent auth responses

2. **Lines 6449-6512:** `do_GET` method
   - Add param validation
   - Fix status codes

3. **Lines 6513-6562:** `do_POST` method
   - Add Content-Length limits
   - Add JSON validation
   - Fix auth check inconsistency

4. **Lines 6685-6724:** Preview/content methods
   - Return proper status codes
   - Fix error responses

5. **Lines 6768-7572:** All `handle_*` methods
   - Use unified response format
   - Return proper status codes
   - Add input validation

6. **Lines 7574-7584:** Response helpers
   - Update `send_json()` to support status
   - Add `send_api_error()` helper

---

## Error Codes Reference

Use these standardized error codes:

```
access_denied           → 403 Forbidden
not_found              → 404 Not Found
not_a_file             → 400 Bad Request
not_a_directory        → 400 Bad Request
validation_error       → 400 Bad Request
already_exists         → 409 Conflict
invalid_json           → 400 Bad Request
file_too_large         → 413 Payload Too Large
authentication_required → 401 Unauthorized
invalid_limit          → 400 Bad Request
invalid_name           → 400 Bad Request
internal_error         → 500 Internal Server Error
```

---

## Before/After Examples

### Example 1: Create Folder

**Before:**
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -d '{"path": "/", "name": "test"}'

# Response (always 200)
HTTP/1.0 200 OK
{"success": true, "path": "/test", "name": "test"}
```

**After:**
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -d '{"path": "/", "name": "test"}'

# Response (proper status)
HTTP/1.0 201 Created
{"success": true, "data": {"path": "/test", "name": "test"}}
```

### Example 2: Validation Error

**Before:**
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -d '{"path": "/", "name": "bad/name"}'

# Response (wrong status)
HTTP/1.0 200 OK
{"success": false, "error": "Invalid folder name"}
```

**After:**
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -d '{"path": "/", "name": "bad/name"}'

# Response (correct status)
HTTP/1.0 400 Bad Request
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "name: cannot contain path separators",
    "details": {"field": "name"}
  }
}
```

### Example 3: Access Denied

**Before:**
```bash
# Try to access /etc/passwd (outside BROWSE_ROOT)
curl http://localhost:9000/api/preview?path=/etc/passwd

# Response (wrong status)
HTTP/1.0 200 OK
{"error": "Access denied"}
```

**After:**
```bash
curl http://localhost:9000/api/preview?path=/etc/passwd

# Response (correct status)
HTTP/1.0 403 Forbidden
{
  "success": false,
  "error": {
    "code": "access_denied",
    "message": "Access denied to that path",
    "details": {}
  }
}
```

---

## Backward Compatibility Impact

**Breaking changes:**
1. HTTP status codes will change (200 → 4xx/5xx)
2. Error response format standardized (may change error strings)
3. Success response might use 201 instead of 200

**Non-breaking:**
1. Endpoint paths unchanged
2. Request JSON fields unchanged
3. Core response data structure (mostly) unchanged

**Client migration effort:**
- **Good client code:** Works immediately (checks HTTP status)
- **Bad client code:** Breaks (ignores HTTP status, checks `success` field)

**Example bad code that will break:**
```javascript
// This will break because it expects HTTP 200 always
fetch('/api/create-folder', {...})
  .then(r => r.json())  // Won't catch 400/403/etc
  .then(data => console.log(data.success))
```

**Example good code that will work:**
```javascript
// This will work because it checks HTTP status
fetch('/api/create-folder', {...})
  .then(r => {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  })
  .then(data => console.log(data.success))
```

---

## Recommended Reading

1. **API Audit Report:** `API_AUDIT_file_explorer.md` (comprehensive)
2. **Refactoring Plan:** `API_REFACTORING_PLAN.md` (implementation guide)
3. **REST Standards:** RFC 7231, RFC 9110 (HTTP semantics)
4. **OpenAPI:** https://spec.openapis.org/oas/v3.1.0

---

## Key Metrics

**Current State:**
- 20 endpoints
- 1 critical issue (always 200)
- 5 high-priority issues
- 12 medium-priority issues
- 0 integration tests
- 0 API documentation

**Target State:**
- 20 endpoints (same)
- 0 critical issues
- 0 high-priority issues
- Complete fix of medium issues
- 50+ integration tests
- OpenAPI 3.1 spec + Swagger UI

**Timeline:** 1-1.5 weeks full-time work
