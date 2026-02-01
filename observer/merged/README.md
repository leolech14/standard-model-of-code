# Control Room

Unified file operations + pipeline monitoring dashboard.

Merged from:
- **Source A**: Refinery Dashboard (React/TypeScript)
- **Source B**: File Explorer (Python)

## Quick Start

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

## Architecture

```
observer/
├── frontend/          # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── hooks/         # React hooks
│   │   ├── contexts/      # React contexts
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utilities
│   └── package.json
│
├── backend/           # FastAPI + Python
│   ├── routes/        # API endpoints
│   │   ├── auth.py        # Touch ID auth
│   │   ├── files.py       # File listing/preview
│   │   ├── operations.py  # CRUD operations
│   │   ├── history.py     # Undo/redo
│   │   └── search.py      # Search/recent
│   ├── websocket/     # Real-time updates
│   ├── middleware/    # Auth, path validation
│   └── main.py
│
└── README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/biometric | Touch ID authentication |
| GET | /auth/verify | Verify session |
| GET | /api/list | List directory |
| GET | /api/preview | File preview |
| POST | /api/upload | Upload file |
| POST | /api/paste | Copy/move files |
| POST | /api/delete | Delete files |
| POST | /api/undo | Undo action |
| GET | /api/search | Search files |
| WS | /ws/{room} | Real-time updates |

## Confidence

| Task | Score |
|------|-------|
| CR-001 Project Setup | 90% |
| CR-002 Shared Types | 92% |
| CR-003 Auth Bridge | 85% |
| CR-004 FastAPI Setup | 80% |
| CR-005 API Endpoints | 88% |
| CR-006 React Integration | 85% |
| CR-007 WebSocket | 90% |
| CR-008 Testing | 85% |
| **Average** | **87%** |

Analysis by Cerebras llama-3.3-70b (4 rounds).
