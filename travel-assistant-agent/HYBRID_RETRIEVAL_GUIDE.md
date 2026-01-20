# Hybrid Retrieval Guide

## Architecture
The hybrid retrieval system combines structured data from the Java MCP data layer with unstructured semantic information from the RAG (Retrieval-Augmented Generation) knowledge base.

### Data Flow
1. **User Input**: The user sends a query (e.g., "Find a luxury hotel in Hangzhou").
2. **Java MCP Query**: The Python Agent calls the Java MCP service (`/mcp/search-hotels`) to get raw structured data from the database.
3. **RAG Retrieval**: Simultaneously, the Python Agent performs a semantic search in the local FAISS vector store.
4. **Hybrid Ranking**: The results from both sources are combined and re-ranked using a multi-factor scoring algorithm.
5. **LLM Generation**: The ranked results are provided to the LLM to generate the final response.

## Ranking Algorithm
We use a weighted scoring formula to rank items:

`Score = (DB_Score * 0.25) + (RAG_Score * 0.35) + (Price_Score * 0.25) + (Rating_Score * 0.15)`

- **DB_Score (0.25)**: Based on the original order returned by the database.
- **RAG_Score (0.35)**: Semantic similarity score from the vector search.
- **Price_Score (0.25)**: How well the item's price matches the user's budget.
- **Rating_Score (0.15)**: Based on the item's star rating (0-5).

## Configuration
Weights and other parameters can be tuned in `src/workflows/subgraphs/hybrid_retrieval.py`.

### Performance Optimization
- **Caching**: Java MCP results are cached in Redis for 1 hour.
- **Concurrency**: Database queries and RAG retrieval can be performed in parallel (planned for future phase).
- **Indexing**: The Java database has indexes on `destination`, `price`, and `rating` for fast lookups.

## RAG Data Synchronization
The Java `mcp-service` includes a `RagSyncService` that periodically (hourly) pushes new and updated data to the Python Agent's `/api/rag/sync` endpoint. This ensures the RAG knowledge base stays up-to-date with the latest database records.

## Troubleshooting
- Check Java MCP logs for database connection issues.
- Verify Redis connectivity for caching.
- Monitor RAG sync logs in the Python Agent for synchronization failures.
