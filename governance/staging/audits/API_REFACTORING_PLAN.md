# File Explorer API Refactoring Plan

**Document:** Implementation guide for standardizing the API
**Target:** `file_explorer.py` (lines 6400-7590)
**Effort:** 40-60 hours
**Testing:** Requires client-side updates + integration tests

---

## Phase 1: Response Standardization (8-10 hours)

### Step 1.1: Create Unified Response Helper

**File:** Add to `file_explorer.py` near line 6400, before RequestHandler class

```python
class APIError(Exception):
    """Standardized API error."""
    def __init__(self, code: str, message: str, status: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def to_dict(self):
        return {
            'success': False,
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details
            }
        }


class APIResponse:
    """Unified response factory."""

    @staticmethod
    def success(data=None, status=200, **kwargs):
        """Build success response."""
        response = {'success': True}
        if data:
            response['data'] = data
        response.update(kwargs)
        return response, status

    @staticmethod
    def error(code: str, message: str, status: int = 400, details: dict = None):
        """Build error response."""
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details or {}
            }
        }, status

    @staticmethod
    def validation_error(field: str, message: str):
        """Build validation error."""
        return APIResponse.error(
            'validation_error',
            f'{field}: {message}',
            status=400,
            details={'field': field}
        )
```

### Step 1.2: Update `send_json()` Method

**Before (line 7580-7584):**
```python
def send_json(self, data):
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

**After:**
```python
def send_json(self, data, status=200):
    """Send JSON response with proper HTTP status.

    Args:
        data: Response dict or tuple of (dict, status_code)
        status: HTTP status code (default 200)
    """
    if isinstance(data, tuple):
        data, status = data

    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    self.end_headers()

    self.wfile.write(json.dumps(data).encode())

    # Log the response
    self._log_api_response(status, data.get('error', {}).get('code') if not data.get('success') else None)

def _log_api_response(self, status, error_code=None):
    """Log API responses for debugging."""
    # TODO: Implement proper logging
    pass
```

### Step 1.3: Update `send_error()` for API Responses

**New method to replace generic HTTP error responses for API:**
```python
def send_api_error(self, code: str, message: str, status: int = 400, details: dict = None):
    """Send standardized API error response."""
    response, http_status = APIResponse.error(code, message, status, details)
    self.send_json(response, http_status)

def send_validation_error(self, field: str, message: str):
    """Send validation error."""
    response, status = APIResponse.validation_error(field, message)
    self.send_json(response, status)
```

---

## Phase 2: HTTP Status Code Implementation (12-15 hours)

### Step 2.1: Fix Authentication Responses

**File:** Update `check_auth()` and auth flow (lines 6410-6475)

**Before:**
```python
def check_auth(self) -> bool:
    # ... returns True/False
    pass

def do_GET(self):
    if not self.check_auth():
        self.send_auth_required()  # ← Returns HTML, inconsistent
        return
```

**After:**
```python
def check_auth(self) -> bool:
    """Returns True if authenticated, False otherwise."""
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

def require_auth(self):
    """Check auth and send 401 if not authenticated."""
    if self.check_auth():
        return True

    # Check Accept header to decide response format
    accept = self.headers.get('Accept', 'application/json')
    if 'text/html' in accept:
        self.send_auth_required()  # HTML page for browser
    else:
        self.send_api_error(
            'authentication_required',
            'Authentication required',
            status=401
        )
    return False

def do_GET(self):
    path = unquote(self.path)

    # Special case: /auth endpoint
    if path == '/auth':
        if request_biometric_auth("File Explorer wants to access your files"):
            AUTH_VERIFIED = True
            AUTH_TOKEN = generate_auth_token()
            self.send_response(302)
            self.send_header('Set-Cookie', f'fe_auth={AUTH_TOKEN}; Path=/; HttpOnly; SameSite=Strict')
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_auth_required()
        return

    # All other endpoints require auth
    if not self.require_auth():
        return

    # ... rest of do_GET
```

### Step 2.2: Fix `/api/preview` and `/api/content` Status Codes

**Before (lines 6685-6724):**
```python
def send_preview(self, path_str):
    file_path = validate_path(path_str)
    if file_path is None:
        self.send_json({'error': 'Access denied'})
        return
    if not file_path.exists() or not file_path.is_file():
        self.send_json({'error': 'Not found'})
        return
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(2000)
        self.send_json({'content': content})
    except:
        self.send_json({'error': 'Cannot read'})
```

**After:**
```python
def send_preview(self, path_str):
    """Get file preview (first 2000 chars).

    Returns:
        200: {"success": true, "data": {"content": "..."}}
        400: {"success": false, "error": {...}}
        403: {"success": false, "error": {...}}
        404: {"success": false, "error": {...}}
    """
    # Validate path
    file_path = validate_path(path_str)
    if file_path is None:
        return self.send_api_error(
            'access_denied',
            'Access denied to that path',
            status=403
        )

    # Check existence
    if not file_path.exists():
        return self.send_api_error(
            'not_found',
            'File not found',
            status=404
        )

    if not file_path.is_file():
        return self.send_api_error(
            'not_a_file',
            'Path is not a file',
            status=400
        )

    # Read preview
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(2000)
        response, status = APIResponse.success(data={'content': content})
        return self.send_json(response, status)
    except (IOError, OSError) as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return self.send_api_error(
            'read_error',
            'Could not read file',
            status=400,
            details={'path': str(file_path)}
        )
    except Exception as e:
        logger.exception(f"Unexpected error reading {file_path}")
        return self.send_api_error(
            'internal_error',
            'Server error reading file',
            status=500
        )

def send_content(self, path_str):
    """Get full file content (max 2MB).

    Returns:
        200: {"success": true, "data": {"content": "..."}}
        400: {"success": false, "error": {...}}
        403: {"success": false, "error": {...}}
        404: {"success": false, "error": {...}}
        413: {"success": false, "error": {...}}
    """
    # Validate path
    file_path = validate_path(path_str)
    if file_path is None:
        return self.send_api_error(
            'access_denied',
            'Access denied to that path',
            status=403
        )

    # Check existence
    if not file_path.exists():
        return self.send_api_error(
            'not_found',
            'File not found',
            status=404
        )

    if not file_path.is_file():
        return self.send_api_error(
            'not_a_file',
            'Path is not a file',
            status=400
        )

    # Check file size
    try:
        size = file_path.stat().st_size
        max_size = MAX_CONTENT_SIZE

        if size > max_size:
            return self.send_api_error(
                'file_too_large',
                f'File too large (max {max_size // 1024 // 1024}MB)',
                status=413,
                details={'size': size, 'max': max_size}
            )

        # Read content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        response, status = APIResponse.success(data={'content': content})
        return self.send_json(response, status)

    except (IOError, OSError) as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return self.send_api_error(
            'read_error',
            'Could not read file',
            status=400
        )
    except Exception as e:
        logger.exception(f"Unexpected error reading {file_path}")
        return self.send_api_error(
            'internal_error',
            'Server error reading file',
            status=500
        )
```

### Step 2.3: Fix All POST Handlers

**Pattern for all handle_* methods:**

**Before:**
```python
def handle_create_folder(self, data):
    parent_path = data.get('path', '')
    name = data.get('name', 'New Folder')

    if not name or '/' in name:
        self.send_json({'success': False, 'error': 'Invalid folder name'})
        return
    # ... more code ...
    self.send_json({'success': True, 'path': str(new_folder), 'name': new_folder.name})
```

**After:**
```python
def handle_create_folder(self, data):
    """Create a new folder.

    Request:
        {
            "path": "parent/folder/path",
            "name": "New Folder Name"
        }

    Response (201 Created):
        {
            "success": true,
            "data": {
                "path": "/full/path/to/New Folder Name",
                "name": "New Folder Name"
            }
        }

    Errors:
        400: Missing required field, invalid name
        403: Access denied
        404: Parent folder not found
        409: Folder already exists
    """
    # Validate request
    parent_path = data.get('path', '').strip()
    name = data.get('name', '').strip()

    if not parent_path:
        return self.send_validation_error('path', 'Required field missing')

    if not name:
        return self.send_validation_error('name', 'Required field missing')

    if len(name) > 255:
        return self.send_validation_error('name', 'Name too long (max 255 chars)')

    if '/' in name or '\\' in name:
        return self.send_validation_error('name', 'Name cannot contain path separators')

    # Validate path
    parent_dir = validate_path(parent_path)
    if parent_dir is None:
        return self.send_api_error(
            'access_denied',
            'Access denied to parent folder',
            status=403
        )

    if not parent_dir.exists():
        return self.send_api_error(
            'not_found',
            'Parent folder does not exist',
            status=404
        )

    if not parent_dir.is_dir():
        return self.send_api_error(
            'not_a_directory',
            'Parent path is not a directory',
            status=400
        )

    # Handle name conflicts
    new_folder = parent_dir / name
    if new_folder.exists():
        return self.send_api_error(
            'already_exists',
            'Folder already exists',
            status=409,
            details={'path': str(new_folder)}
        )

    # Create folder
    try:
        new_folder.mkdir(parents=False, exist_ok=False)
        ACTION_HISTORY.append({
            'action': 'create_folder',
            'path': str(new_folder)
        })
        REDO_STACK.clear()

        response, status = APIResponse.success(
            data={
                'path': str(new_folder),
                'name': new_folder.name
            },
            status=201
        )
        return self.send_json(response, status)

    except OSError as e:
        logger.error(f"Failed to create folder {new_folder}: {e}")
        return self.send_api_error(
            'creation_failed',
            'Could not create folder',
            status=400,
            details={'reason': str(e)}
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating folder")
        return self.send_api_error(
            'internal_error',
            'Server error creating folder',
            status=500
        )
```

---

## Phase 3: Input Validation (8-10 hours)

### Step 3.1: Validate Query Parameters

**Add before do_GET line 6486:**
```python
def validate_query_params(self, params: dict, schema: dict):
    """Validate query parameters against schema.

    Schema format:
        {
            'path': {'type': 'str', 'required': True},
            'limit': {'type': 'int', 'required': False, 'min': 1, 'max': 1000, 'default': 10},
            'depth': {'type': 'int', 'required': False, 'min': 0, 'max': 10, 'default': 1}
        }

    Returns:
        (validated_dict, error_response) or (validated_dict, None)
    """
    validated = {}

    for field, rules in schema.items():
        value = params.get(field, [None])[0]
        required = rules.get('required', False)
        field_type = rules.get('type', 'str')
        default = rules.get('default')

        # Handle missing required field
        if value is None:
            if required:
                return None, self.send_validation_error(field, 'Required parameter missing')
            if default is not None:
                validated[field] = default
            continue

        # Type conversion and validation
        try:
            if field_type == 'int':
                value = int(value)
                minimum = rules.get('min')
                maximum = rules.get('max')
                if minimum is not None and value < minimum:
                    return None, self.send_validation_error(
                        field,
                        f'Must be >= {minimum}'
                    )
                if maximum is not None and value > maximum:
                    return None, self.send_validation_error(
                        field,
                        f'Must be <= {maximum}'
                    )
            # Add other types as needed
        except (ValueError, TypeError):
            return None, self.send_validation_error(
                field,
                f'Must be of type {field_type}'
            )

        validated[field] = value

    return validated, None
```

**Usage in do_GET (fix line 6490-6495):**
```python
elif path.startswith('/api/folder-preview'):
    qs = parse_qs(path.split('?')[1]) if '?' in path else {}
    validated, error = self.validate_query_params(qs, {
        'path': {'type': 'str', 'required': False, 'default': ''},
        'limit': {'type': 'int', 'required': False, 'min': 1, 'max': 1000, 'default': 10},
        'depth': {'type': 'int', 'required': False, 'min': 0, 'max': 10, 'default': 1}
    })
    if error:
        return error
    self.send_json(self.get_folder_preview(
        validated['path'],
        limit=validated['limit'],
        depth=validated['depth']
    ))
```

### Step 3.2: Validate JSON Request Bodies

**Add validation method:**
```python
def validate_json_body(self, data: dict, schema: dict):
    """Validate JSON request body against schema.

    Returns:
        (validated_dict, None) on success
        (None, error_response) on failure
    """
    validated = {}

    for field, rules in schema.items():
        value = data.get(field)
        required = rules.get('required', False)
        field_type = rules.get('type', 'str')

        if value is None and required:
            return None, self.send_validation_error(
                field,
                'Required field missing'
            )

        if value is None:
            continue

        # Type checking
        if field_type == 'str' and not isinstance(value, str):
            return None, self.send_validation_error(
                field,
                f'Must be a string'
            )

        if field_type == 'list' and not isinstance(value, list):
            return None, self.send_validation_error(
                field,
                f'Must be a list'
            )

        # Length validation
        if 'max_length' in rules and isinstance(value, str):
            if len(value) > rules['max_length']:
                return None, self.send_validation_error(
                    field,
                    f'Too long (max {rules["max_length"]} chars)'
                )

        validated[field] = value

    return validated, None
```

**Usage in do_POST handlers (example for handle_create_folder):**
```python
def handle_create_folder(self, data):
    # Validate request
    validated, error = self.validate_json_body(data, {
        'path': {'type': 'str', 'required': True, 'max_length': 1024},
        'name': {'type': 'str', 'required': True, 'max_length': 255}
    })
    if error:
        return error

    parent_path = validated['path'].strip()
    name = validated['name'].strip()
    # ... rest of logic
```

### Step 3.3: Add Content-Length Limits

**Add to do_POST (line 6530):**
```python
def do_POST(self):
    if not self.require_auth():
        return

    path = unquote(self.path)
    content_type = self.headers.get('Content-Type', '')

    # Handle multipart file uploads
    if path == '/api/upload' and 'multipart/form-data' in content_type:
        self.handle_upload()
        return

    # Validate Content-Length for JSON requests
    content_length = int(self.headers.get('Content-Length', 0))
    MAX_JSON_PAYLOAD = 10 * 1024 * 1024  # 10MB

    if content_length > MAX_JSON_PAYLOAD:
        return self.send_api_error(
            'payload_too_large',
            f'Request body too large (max {MAX_JSON_PAYLOAD // 1024 // 1024}MB)',
            status=413
        )

    # Parse JSON body
    body = self.rfile.read(content_length)
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError as e:
        return self.send_api_error(
            'invalid_json',
            f'Invalid JSON in request body',
            status=400,
            details={'error': str(e)}
        )

    # Route to handler
    if path == '/api/paste':
        self.handle_paste(data)
    # ... etc
```

---

## Phase 4: Documentation (5-7 hours)

### Step 4.1: Create OpenAPI 3.1 Specification

**New file:** `file_explorer_openapi.yaml`

```yaml
openapi: 3.1.0
info:
  title: File Explorer API
  version: 1.0.0
  description: |
    Local file management API with authentication, undo/redo support,
    and archive operations.

servers:
  - url: http://localhost:9000
    description: Local development server

components:
  schemas:
    Error:
      type: object
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          const: false
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Machine-readable error code
              examples:
                - access_denied
                - not_found
                - validation_error
                - already_exists
                - internal_error
            message:
              type: string
              description: Human-readable error message
            details:
              type: object
              description: Additional error details

    FileInfo:
      type: object
      properties:
        path:
          type: string
          description: Full path to file
        name:
          type: string
          description: File name only
        size:
          type: integer
          description: File size in bytes
        type:
          type: string
          enum:
            - file
            - directory
        modified:
          type: string
          format: date-time

    SuccessResponse:
      type: object
      required:
        - success
      properties:
        success:
          type: boolean
          const: true
        data:
          type: object
          description: Response payload

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

    AccessDenied:
      description: Access denied to that path
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

    NotFound:
      description: File or folder not found
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

    Conflict:
      description: Resource already exists
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }

paths:
  /auth:
    get:
      summary: Authenticate with biometric
      description: Initiate biometric authentication (Touch ID/Face ID on macOS)
      responses:
        '302':
          description: Redirect to home after successful auth
          headers:
            Set-Cookie:
              schema:
                type: string
                example: fe_auth=<token>; Path=/; HttpOnly; SameSite=Strict
            Location:
              schema:
                type: string
                example: /
        '200':
          description: Auth page (with button to retry)

  /api/list:
    get:
      summary: List directory contents
      parameters:
        - name: path
          in: query
          schema:
            type: string
            default: ""
          description: Directory path relative to browse root
        - name: sort
          in: query
          schema:
            type: string
            enum:
              - name
              - size
              - modified
            default: name
      responses:
        '200':
          description: Directory listing
          content:
            application/json:
              schema:
                allOf:
                  - { $ref: '#/components/schemas/SuccessResponse' }
                  - type: object
                    properties:
                      data:
                        type: array
                        items: { $ref: '#/components/schemas/FileInfo' }
        '401': { $ref: '#/components/responses/Unauthorized' }
        '403': { $ref: '#/components/responses/AccessDenied' }
        '404': { $ref: '#/components/responses/NotFound' }

  /api/preview:
    get:
      summary: Get file preview (2000 chars)
      parameters:
        - name: path
          in: query
          schema:
            type: string
          required: true
          description: File path
      responses:
        '200':
          description: File preview
          content:
            application/json:
              schema:
                allOf:
                  - { $ref: '#/components/schemas/SuccessResponse' }
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          content:
                            type: string
        '401': { $ref: '#/components/responses/Unauthorized' }
        '403': { $ref: '#/components/responses/AccessDenied' }
        '404': { $ref: '#/components/responses/NotFound' }

  /api/create-folder:
    post:
      summary: Create a new folder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - path
                - name
              properties:
                path:
                  type: string
                  description: Parent directory path
                name:
                  type: string
                  maxLength: 255
                  description: New folder name
      responses:
        '201':
          description: Folder created
          content:
            application/json:
              schema:
                allOf:
                  - { $ref: '#/components/schemas/SuccessResponse' }
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          path:
                            type: string
                          name:
                            type: string
        '400': { $ref: '#/components/responses/BadRequest' }
        '401': { $ref: '#/components/responses/Unauthorized' }
        '403': { $ref: '#/components/responses/AccessDenied' }
        '404': { $ref: '#/components/responses/NotFound' }
        '409': { $ref: '#/components/responses/Conflict' }

  # ... continue for all other endpoints
```

### Step 4.2: Update Docstrings

Add full docstring to every handler with:
- Request format (JSON fields)
- Response format (success and error cases)
- HTTP status codes
- Permission requirements

Example already shown above in "Step 2.3" for `handle_create_folder`.

### Step 4.3: Create Developer Guide

**New file:** `API_DEVELOPMENT_GUIDE.md`

```markdown
# File Explorer API Development Guide

## Response Format

All responses follow this structure:

### Success Response (HTTP 200, 201, etc.)
```json
{
  "success": true,
  "data": {
    // Endpoint-specific data
  }
  // Optional: additional fields like "count", "moved", etc.
}
```

### Error Response (HTTP 400, 403, 404, 500, etc.)
```json
{
  "success": false,
  "error": {
    "code": "error_code_name",
    "message": "Human readable message",
    "details": {
      // Optional: additional error context
    }
  }
}
```

## HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|------------|
| 200 | OK | Successful read or state query |
| 201 | Created | Resource successfully created |
| 400 | Bad Request | Validation error, invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied to resource |
| 404 | Not Found | File/folder doesn't exist |
| 409 | Conflict | Resource already exists |
| 413 | Payload Too Large | File/request too large |
| 500 | Server Error | Unexpected server error |

## Error Codes

Common error codes used across endpoints:

- `access_denied` - Path outside allowed root
- `not_found` - File/folder doesn't exist
- `not_a_file` - Path is a directory, expected file
- `not_a_directory` - Path is a file, expected directory
- `validation_error` - Request validation failed
- `already_exists` - Resource already exists
- `invalid_json` - Malformed JSON request
- `file_too_large` - File exceeds size limit
- `authentication_required` - Not authenticated
- `internal_error` - Unexpected server error
- `creation_failed` - Failed to create resource
- `read_error` - Failed to read file

## Authentication

All endpoints except `/auth` require authentication via cookie:

```
Cookie: fe_auth=<token>
```

Missing or invalid token returns `401 Unauthorized`.

## Request Validation

All JSON request bodies are validated. Validation errors return `400 Bad Request`:

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "path: Required field missing",
    "details": {
      "field": "path"
    }
  }
}
```

## Examples

### Create a folder
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -H "Cookie: fe_auth=<token>" \
  -d '{
    "path": "/home/user/projects",
    "name": "new-project"
  }'

# Response (201 Created):
{
  "success": true,
  "data": {
    "path": "/home/user/projects/new-project",
    "name": "new-project"
  }
}
```

### Error case: folder already exists
```bash
curl -X POST http://localhost:9000/api/create-folder \
  -H "Content-Type: application/json" \
  -H "Cookie: fe_auth=<token>" \
  -d '{
    "path": "/home/user/projects",
    "name": "existing-folder"
  }'

# Response (409 Conflict):
{
  "success": false,
  "error": {
    "code": "already_exists",
    "message": "Folder already exists",
    "details": {
      "path": "/home/user/projects/existing-folder"
    }
  }
}
```

## Logging

All API requests and errors are logged. Check server logs for debugging.
```

---

## Phase 5: Testing & Validation (10-15 hours)

### Step 5.1: Create Integration Tests

**New file:** `test_api.py`

```python
import unittest
import json
import requests
from pathlib import Path

class TestFileExplorerAPI(unittest.TestCase):
    BASE_URL = "http://localhost:9000"

    def setUp(self):
        """Authenticate before each test."""
        self.session = requests.Session()
        # TODO: Get auth token from /auth endpoint

    def test_create_folder_success(self):
        """Test successful folder creation."""
        response = self.session.post(
            f"{self.BASE_URL}/api/create-folder",
            json={"path": "/", "name": "test-folder"}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('path', data['data'])

    def test_create_folder_invalid_name(self):
        """Test validation error for invalid name."""
        response = self.session.post(
            f"{self.BASE_URL}/api/create-folder",
            json={"path": "/", "name": "bad/name"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'validation_error')

    def test_create_folder_access_denied(self):
        """Test access denied for path outside root."""
        response = self.session.post(
            f"{self.BASE_URL}/api/create-folder",
            json={"path": "/etc/passwd", "name": "bad"}
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error']['code'], 'access_denied')

    # ... more tests
```

---

## Rollout Plan

1. **Week 1:**
   - Phase 1: Response standardization
   - Phase 2: HTTP status codes
   - Testing: Manual testing with curl/Postman

2. **Week 2:**
   - Phase 3: Input validation
   - Phase 4: Documentation
   - Testing: Integration tests

3. **Week 3:**
   - Deployment to staging
   - Client-side updates
   - Regression testing

4. **Week 4:**
   - Production deployment
   - Monitor error rates
   - Post-launch support

---

## Breaking Changes

This refactoring introduces breaking changes:

1. Error responses now use HTTP 4xx/5xx status codes instead of always 200
2. Success responses may use 201 for creation endpoints
3. Error response format is standardized (different schema)

**Migration path for clients:**
```javascript
// Old code
fetch('/api/create-folder', {...})
  .then(r => r.json())
  .then(data => {
    if (data.success) { ... }
    else { console.error(data.error); }
  })

// New code - leverage HTTP status
fetch('/api/create-folder', {...})
  .then(r => {
    if (r.ok) return r.json();
    else return r.json().then(e => Promise.reject(e));
  })
  .then(data => { ... })
  .catch(error => console.error(error.error.code));
```

---

## Success Criteria

After refactoring, the API should:

1. Use correct HTTP status codes for all responses
2. Have consistent error response format
3. Validate all inputs
4. Have complete OpenAPI documentation
5. Have passing integration tests
6. Have proper logging
7. Follow REST principles
8. Have < 5% breaking changes in client code

---

## Effort Estimation Summary

| Phase | Hours | Notes |
|-------|-------|-------|
| 1: Response helpers | 8-10 | Test thoroughly |
| 2: HTTP status codes | 12-15 | Most time intensive |
| 3: Input validation | 8-10 | Straightforward |
| 4: Documentation | 5-7 | Use tools to generate |
| 5: Testing | 10-15 | Comprehensive coverage |
| **Total** | **43-57** | Roughly 1-1.5 weeks full-time |
