# lvyou

This repository is organized as a small monorepo with **three independent sub-projects**:

- `travel-assistant-front/` — React 18 + TypeScript + Vite frontend
- `travel-assistant/` — Java Spring Cloud microservices (API)
- `travel-assistant-agent/` — Python FastAPI agent service (LangChain/LangGraph)

## Quick start

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
