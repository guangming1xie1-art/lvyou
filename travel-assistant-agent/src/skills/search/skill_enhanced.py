"""
Enhanced Search Skill Implementation with Pydantic Support
根据用户需求搜索旅游目的地、酒店、航班等信息
"""
from typing import Dict, Any, Optional, List
import logging
from src.skills.base_enhanced import EnhancedSkill
from src.skills.search.models import SearchInput, SearchOutput, SearchResultItem, SearchMetadata
from src.agents.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class SearchSkill(EnhancedSkill):
    """搜索技能 - 使用 Pydantic 类型安全和完整验证"""
    
    input_model = SearchInput
    output_model = SearchOutput
    
    def __init__(self):
        super().__init__(
            name="search",
            description="根据用户需求搜索旅游目的地、酒店、航班等信息，支持多维度过滤",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.05,
            category="search",
            cost_config={
                "base": 0.01,
                "per_result": 0.001,
                "formula": "base + min(results_count, 100) * per_result",
                "max_cost": 0.15
            }
        )
        self.mcp_client = None
    
    async def _ensure_mcp_client(self):
        """确保 MCP Client 已初始化"""
        if self.mcp_client is None:
            self.mcp_client = get_mcp_client()
            if self.mcp_client and not self.mcp_client.is_connected():
                try:
                    await self.mcp_client.connect()
                    logger.info("MCP client connected successfully")
                except Exception as e:
                    logger.warning(f"Failed to connect MCP client: {e}")
    
    async def execute(self, input_data: SearchInput) -> SearchOutput:
        """
        执行搜索 - 类型安全版本
        
        Args:
            input_data: 已验证的 SearchInput 模型
            
        Returns:
            SearchOutput 模型包含搜索结果
            
        Raises:
            ValueError: 如果搜索参数无效
            RuntimeError: 如果搜索执行失败
        """
        query = input_data.query
        filters_dict = input_data.filters.model_dump(exclude_none=True) if input_data.filters else {}
        limit = input_data.limit
        offset = input_data.offset
        
        logger.info(f"Executing search: query='{query}', limit={limit}, offset={offset}")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # 确保 MCP Client 连接
        await self._ensure_mcp_client()
        
        if not self.mcp_client:
            logger.warning("MCP client not available, returning mock data")
            return self._generate_mock_search_results(query, limit, offset, filters_dict)
        
        # 调用 Java API 的 search_destinations
        try:
            result = await self.mcp_client.call_tool(
                tool_name="search_destinations",
                parameters={
                    "query": query,
                    "filters": filters_dict,
                    "limit": limit,
                    "offset": offset
                }
            )
            
            if result.get("error"):
                error_msg = result["error"]
                logger.warning(f"Java API returned error: {error_msg}")
                
                # If API fails, return mock data as fallback
                if "timeout" in error_msg.lower() or "unavailable" in error_msg.lower():
                    return self._generate_mock_search_results(query, limit, offset, filters_dict)
                else:
                    raise RuntimeError(f"Search API error: {error_msg}")
            
            # 提取结果
            api_result = result.get("result", {})
            destinations = api_result.get("destinations", [])
            
            # Apply pagination
            limited_results = destinations[offset:offset + limit] if destinations else []
            
            # 转换格式为 SearchResultItem 模型
            converted_results = []
            for dest in limited_results:
                try:
                    item = self._convert_destination_to_result_item(dest)
                    converted_results.append(item)
                except Exception as e:
                    logger.warning(f"Failed to convert destination item: {e}, data: {dest}")
                    continue
            
            # 计算搜索质量
            search_quality = self._calculate_search_quality(converted_results, len(destinations))
            
            # 构建元数据
            metadata = SearchMetadata(
                execution_time_ms=self._extract_execution_time(api_result),
                data_sources=self._extract_data_sources(api_result),
                mock=api_result.get("mock", False)
            )
            
            # 返回格式化的 SearchOutput
            total_results = api_result.get("total", len(converted_results))
            if total_results == 0 and len(converted_results) > 0:
                total_results = len(converted_results)
            
            return SearchOutput(
                results=converted_results,
                total=total_results,
                search_quality=search_quality,
                filters_applied=filters_dict if filters_dict else None,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"Error executing search: {str(e)}", exc_info=True)
            # Fallback to mock data on critical errors
            return self._generate_mock_search_results(query, limit, offset, filters_dict)
    
    def calculate_cost(
        self,
        input_data: SearchInput,
        output_data: SearchOutput
    ) -> float:
        """
        动态成本计算 - 基于搜索结果数量
        
        Args:
            input_data: SearchInput model
            output_data: SearchOutput model
            
        Returns:
            Actual cost in USD
        """
        base_cost = 0.01
        per_result_cost = 0.001
        max_cost = 0.15
        
        # Calculate based on actual result count
        results_count = len(output_data.results)
        actual_cost = base_cost + min(results_count, 100) * per_result_cost
        actual_cost = min(actual_cost, max_cost)  # Cap at max_cost
        
        return round(actual_cost, 4)
    
    def _convert_destination_to_result_item(self, dest: Dict[str, Any]) -> SearchResultItem:
        """转换 API 返回的目的地数据为 SearchResultItem"""
        item_data = {
            "id": str(dest.get("id", "")),
            "type": dest.get("type", "destination"),
            "name": str(dest.get("name", "")),
            "description": str(dest.get("description", "")),
            "rating": float(dest.get("rating", 0.0)) if dest.get("rating") else None,
            "reviews_count": int(dest.get("reviews_count", 0)) if dest.get("reviews_count") else None,
            "currency": dest.get("currency", "CNY")
        }
        
        # Add country for destinations
        if item_data["type"] == "destination":
            item_data["country"] = dest.get("country")
        
        # Handle price information based on type
        if "price" in dest and dest["price"] is not None:
            item_data["price"] = float(dest["price"])
        elif "price_range" in dest:
            item_data["price_range"] = dest["price_range"]
        elif item_data["type"] == "destination":
            # Convert min_price/max_price to price_range
            if "min_price" in dest or "max_price" in dest:
                item_data["price_range"] = {
                    "min": float(dest.get("min_price", 0)),
                    "max": float(dest.get("max_price", dest.get("min_price", 0))),
                    "currency": dest.get("currency", "CNY")
                }
        
        # Type-specific fields
        if item_data["type"] == "destination":
            item_data["popular_attractions"] = dest.get("popular_attractions", [])
            item_data["best_season"] = dest.get("best_season", [])
        elif item_data["type"] == "hotel":
            item_data["amenities"] = dest.get("amenities", [])
        
        return SearchResultItem(**item_data)
    
    def _calculate_search_quality(self, results: List[SearchResultItem], total_found: int = 0) -> float:
        """计算搜索质量分数 (0-1)"""
        if not results:
            return 0.0
        
        # Factor 1: Average rating of results
        ratings = [r.rating for r in results if r.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        rating_score = min(avg_rating / 5.0, 1.0)
        
        # Factor 2: Number of results found
        results_score = min(len(results) / 20.0, 1.0)  # Normalize to 20 results
        
        # Factor 3: Total matches in database
        total_score = min(total_found / 50.0, 1.0) if total_found > 0 else 0.7
        
        # Weighted average
        quality = (rating_score * 0.5 + results_score * 0.3 + total_score * 0.2)
        
        return round(quality, 2)
    
    def _generate_mock_search_results(
        self, 
        query: str, 
        limit: int, 
        offset: int, 
        filters: Dict[str, Any]
    ) -> SearchOutput:
        """生成模拟搜索结果作为降级方案"""
        logger.info(f"Generating mock search results for query: {query}")
        
        # Simple mock data based on query
        mock_items = []
        
        # Generate some mock destinations
        for i in range(min(limit, 5)):
            mock_items.append(
                SearchResultItem(
                    id=f"dest_{i+1:03d}",
                    type="destination",
                    name=f"模拟目的地 {i+1}",
                    description=f"与 '{query}' 相关的旅游目的地",
                    rating=4.0 + i * 0.1,
                    reviews_count=1000 + i * 500,
                    currency="CNY",
                    popular_attractions=["景点A", "景点B", "景点C"],
                    best_season=["春季", "秋季"]
                )
            )
        
        metadata = SearchMetadata(
            execution_time_ms=100,
            data_sources=["mock"],
            mock=True
        )
        
        return SearchOutput(
            results=mock_items,
            total=len(mock_items) * 3,  # Simulate more results available
            search_quality=0.6,
            filters_applied=filters if filters else None,
            metadata=metadata
        )
    
    def _extract_execution_time(self, api_result: Dict[str, Any]) -> int:
        """从 API 结果中提取执行时间"""
        try:
            return int(api_result.get("execution_time_ms", 500))
        except:
            return 500
    
    def _extract_data_sources(self, api_result: Dict[str, Any]) -> List[str]:
        """从 API 结果中提取数据来源"""
        sources = api_result.get("data_sources", [])
        if isinstance(sources, list):
            return sources
        elif isinstance(sources, str):
            return [sources]
        return ["java_api"]
    
    def can_execute(self, input_dict: Dict[str, Any]) -> bool:
        """增强的 can_execute 方法，使用实际的模型验证"""
        if not self.enabled:
            return False
        
        try:
            self.input_model.model_validate(input_dict)
            return True
        except:
            return False


__all__ = ["SearchSkill"]
