# lvyou

智能旅游助手平台 - AI-Powered Travel Assistant Platform

This repository is organized as a small monorepo with **three independent sub-projects**:

- `travel-assistant-front/` — React 18 + TypeScript + Vite frontend (用户端)
- `travel-assistant/` — Java Spring Cloud microservices (API) + Python admin-agent (管理后台)
- `travel-assistant-agent/` — Python FastAPI agent service (LangChain/LangGraph) (用户端AI)

## OpenSpec Integration

This project uses **OpenSpec** as the single source of truth for project specifications, change tracking, and AI-human alignment.

### Documentation Structure

```
openspec/
├── project.md              # Project-wide conventions and standards
├── AGENTS.md               # AI agent workflow guidance (auto-generated)
├── OPENSPEC_WORKFLOW.md    # Step-by-step workflow guide
├── specs/
│   ├── frontend/spec.md    # Frontend specifications
│   ├── backend-java/spec.md # Java backend specifications
│   ├── backend-agent/spec.md # Python Agent specifications
│   └── integration/spec.md  # API contracts between services
└── changes/
    └── example-feature/    # Sample change demonstrating the workflow
```

### Key Documents

| Document | Purpose |
|----------|---------|
| [openspec/project.md](openspec/project.md) | Project conventions, naming, architecture |
| [openspec/OPENSPEC_WORKFLOW.md](openspec/OPENSPEC_WORKFLOW.md) | How to use OpenSpec with cto.new |
| [openspec/specs/frontend/spec.md](openspec/specs/frontend/spec.md) | Frontend component architecture, state management |
| [openspec/specs/backend-java/spec.md](openspec/specs/backend-java/spec.md) | Java REST API design, microservices |
| [openspec/specs/backend-agent/spec.md](openspec/specs/backend-agent/spec.md) | Claude Skills, LangGraph workflows |
| [openspec/specs/integration/spec.md](openspec/specs/integration/spec.md) | API contracts, data flow |

### Using OpenSpec with cto.new

1. **Read relevant specifications** before starting work
2. **Reference the change** when creating cto.new tasks
3. **Follow conventions** from `openspec/project.md`
4. **Update specifications** as you implement
5. **Validate changes** with `openspec validate`

See [OPENSPEC_WORKFLOW.md](openspec/OPENSPEC_WORKFLOW.md) for detailed guidance.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Browser                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant-front (React 18 + Vite)                       │
│  Port: 3000 (dev) / 80 (prod)                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant (Spring Cloud Gateway)                        │
│  Port: 8080                                                     │
└───────┬─────────────────┬───────────────────┬───────────────────┘
        │                 │                   │
        ▼                 ▼                   ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────────────┐
│ auth-service  │ │ travel-       │ │ travel-plan-service   │
│ Port: 8081    │ │ request-      │ │ Port: 8083            │
│ JWT Auth      │ │ service       │ │ Plan Generation       │
│               │ │ Port: 8082    │ │ - Calls Agent Service │
│               │ │ Request Mgmt  │ │                       │
└───────────────┘ └───────────────┘ └───────────────────────┘
        │                 │                   │
        └─────────────────┼───────────────────┘
                          │
                          ▼ (Internal API)
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant-agent (FastAPI + LangGraph + Claude)          │
│  Port: 8000                                                      │
│  - AI Travel Planning                                            │
│  - Claude Skills (MCP)                                           │
│  - Destination/Pricing/Weather/Reviews                           │
└─────────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│                    Admin Browser                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant/admin-frontend (Vue3 + TypeScript + Vite)     │
│  Port: 3001 (dev) / 3001 (prod)                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant/admin-service (Spring Boot)                  │
│  Port: 8090                                                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  travel-assistant/admin-agent (FastAPI + LangChain)             │
│  Port: 8091                                                     │
│  - Document Processing (RAG)                                     │
│  - Vector Indexing (FAISS)                                       │
│  - Parent-Child Index                                           │
└─────────────────────────────────────────────────────────────────┘

Data Layer: PostgreSQL (Port 5432)
Service Discovery: Nacos (Port 8848)
Vector Store: FAISS (Shared Storage)
```

## Quick Start

### Frontend (development)

```bash
cd travel-assistant-front
npm install
npm run dev
```

Frontend dev server: http://localhost:3000

### Frontend (Docker, production build)

The repository root `docker-compose.yml` builds and serves the frontend with Nginx:

```bash
# from repository root
docker compose up -d --build
```

Frontend (Nginx): http://localhost:3000

### Backend (Spring Cloud)

```bash
cd travel-assistant
docker compose up --build
```

See `travel-assistant/README.md` for ports and details.

### Agent (FastAPI)

```bash
cd travel-assistant-agent
docker compose up --build
```

See `travel-assistant-agent/README.md` for configuration and details.

### Admin Frontend (Vue3, development)

```bash
cd travel-assistant/admin-frontend
npm install
npm run dev
```

Admin dev server: http://localhost:3001

### Admin Backend (Spring Boot)

```bash
cd travel-assistant/admin-service
docker compose up --build
```

See [ADMIN_SYSTEM_ARCHITECTURE.md](ADMIN_SYSTEM_ARCHITECTURE.md) for details.

### Admin Agent (Python, RAG Processing)

```bash
cd travel-assistant/admin-agent
docker compose up --build
```

See [RAG_DOCUMENT_SYNC_DESIGN.md](RAG_DOCUMENT_SYNC_DESIGN.md) for details.

## Project Structure

### User Frontend (`travel-assistant-front/`)

- React 18 + TypeScript + Vite
- Zustand for state management
- TanStack Query for data fetching
- Tailwind CSS for styling
- Vitest for testing

### Java Backend (`travel-assistant/`)

- Spring Boot 3.2 + Spring Cloud 2023
- Spring Cloud Alibaba Nacos
- Spring Cloud Gateway
- PostgreSQL database

### User Python Agent (`travel-assistant-agent/`)

- FastAPI + Python 3.10+
- LangChain + LangGraph
- Claude 3.5 Sonnet (Anthropic API)
- MCP (Model Context Protocol)

### Admin Frontend (`travel-assistant/admin-frontend/`)

- Vue3 + TypeScript + Vite
- Pinia for state management
- Element Plus UI components
- Vue Router
- Axios HTTP client

### Admin Backend (`travel-assistant/admin-service/`)

- Spring Boot 3.x
- Spring Security (权限控制)
- OpenFeign (服务间调用)
- PostgreSQL database

### Admin Python Agent (`travel-assistant/admin-agent/`)

- FastAPI + Python 3.10+
- LangChain (文档处理)
- FAISS (向量索引)
- Parent-Child Index (RAG优化)

## Contributing

1. Read the [OpenSpec project conventions](openspec/project.md)
2. Review relevant [service specifications](openspec/specs/)
3. Create a change proposal for new features
4. Follow the [workflow guide](openspec/OPENSPEC_WORKFLOW.md)
5. Ensure code passes linting and tests

## License

ISC
