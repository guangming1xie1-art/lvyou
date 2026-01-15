# Dependency Specifications

This document outlines the key dependencies for the Lvyou Agent system, the rationale for version selections, and known compatibility considerations.

## Key Dependencies

| Package | Target Version | Use Case | Rationale |
|---------|----------------|----------|-----------|
| `langchain` | `>=1.0.0, <2.0.0` | Core LLM framework | Stability of v1.0 API and new features support. |
| `langgraph` | `>=1.0.0, <2.0.0` | Workflow orchestration | Native support for StateGraph and complex branching. |
| `deepagent` | `>=0.2.7, <0.3.0` | Sub-agent reasoning | Specialized sub-agents for Search and Recommendation. |
| `pydantic` | `>=2.0.0` | Data validation | Performance improvements and V2 features. |
| `python-jose[cryptography]` | `>=3.3.0` | JWT Authentication | Security and stability. |
| `redis` | `>=5.0.0` | Caching layer | Improved performance and async support. |
| `httpx` | `>=0.25.0` | HTTP Client | Support for HTTP/2 and efficient connection pooling. |
| `faiss-cpu` | `>=1.7.4` | Vector Store | Efficient local vector similarity search. |
| `rank-bm25` | `>=0.2.2` | Keyword Search | Support for hybrid search (Vector + BM25). |

## Version Selection Rationale

### LangChain & LangGraph v1.0
We have chosen to align with the v1.0 release track of LangChain and LangGraph to ensure long-term stability. This version introduces a more robust API structure and better support for production-grade agentic workflows.

### DeepAgent v0.2.7
DeepAgent provides the necessary abstraction for sub-agents that significantly reduces token consumption by using structured states instead of full conversation histories. Version 0.2.7 is the stable release supporting the unified model factory.

### Pydantic v2
The transition to Pydantic v2 offers substantial performance gains in data serialization and validation, which is critical for high-concurrency agent applications.

## Hybrid Search Support
Phase 1 introduces hybrid search combining semantic similarity (FAISS) and keyword matching (BM25).
- **FAISS**: Chosen for its high performance and reliability in local environments.
- **BM25**: Implemented via `rank-bm25` for robust keyword-based retrieval.

## Known Compatibility Issues
- **LangChain v1.0 Migrations**: Some legacy `langchain` imports might need updating to `langchain-community` or `langchain-core`.
- **DeepAgent Installation**: Ensure that the appropriate provider keys are set as DeepAgent depends on model availability for initialization.
- **Python 3.10+**: All dependencies are optimized for Python 3.10 and above.
