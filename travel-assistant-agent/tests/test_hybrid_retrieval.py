import pytest
import asyncio
from unittest.mock import MagicMock, patch
from ...src.workflows.subgraphs.hybrid_retrieval import hybrid_rank, _calc_price_score

def test_calc_price_score():
    budget = {"min": 200, "max": 500}
    
    # Within budget
    assert _calc_price_score(300, budget) == 1.0
    # Below budget
    assert _calc_price_score(150, budget) == 0.8
    # Slightly above budget
    assert _calc_price_score(600, budget) == 0.8
    # Far above budget
    assert _calc_price_score(1500, budget) == 0.0

def test_hybrid_rank():
    raw_hotels = [
        {"id": 1, "name": "Hotel A", "price": 1000, "rating": 4.5},
        {"id": 2, "name": "Hotel B", "price": 300, "rating": 4.0},
        {"id": 3, "name": "Hotel C", "price": 500, "rating": 3.5},
    ]
    
    # Mock RAG docs
    class MockDoc:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata
            
    rag_docs = [
        MockDoc("Hotel B is great", {"id": 2}),
        MockDoc("Hotel C is okay", {"id": 3}),
    ]
    
    criteria = {"price_range": {"min": 200, "max": 600}}
    
    ranked = hybrid_rank(raw_hotels, rag_docs, criteria)
    
    assert len(ranked) == 3
    # Hotel B should be top because it's in budget, has RAG match, and decent rating
    assert ranked[0]['id'] == 2
    assert '_score' in ranked[0]
    assert '_explanation' in ranked[0]

@pytest.mark.asyncio
async def test_mcp_client_call_tool_with_cache():
    from src.agents.mcp_client import MCPClient
    
    with patch('redis.asyncio.Redis') as mock_redis, \
         patch('httpx.AsyncClient.post') as mock_post:
        
        # Setup mock redis
        r = MagicMock()
        r.get.return_value = None # Cache miss
        r.setex = MagicMock()
        mock_redis.return_value = r
        
        # Setup mock httpx
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 0, "data": [{"id": 1}]}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = MCPClient()
        # Mock _get_redis to return our mock
        client._get_redis = asyncio.coroutine(lambda: r)
        
        result = await client.call_tool("search_hotels", destination="Hangzhou")
        
        assert result["code"] == 0
        assert r.setex.called
        assert mock_post.called
