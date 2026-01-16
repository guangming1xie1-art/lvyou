# Skill: search

## 概述
根据用户需求搜索旅游目的地、酒店、航班等信息。支持多种过滤条件（预算、日期、偏好）。

## 参数

### 输入参数
- `query` (string, required): 搜索关键词（目的地名称、城市、国家等）
- `filters` (object, optional): 过滤条件
  - `budget` (object): 预算范围 `{min: number, max: number, currency: string}`
  - `dates` (object): 日期范围 `{check_in: string, check_out: string}` 或 `{departure: string, return: string}`
  - `preferences` (array): 用户偏好，如 `["beach", "culture", "food"]`
  - `travelers_count` (integer): 旅行人数
  - `search_type` (string): 搜索类型 `"destination" | "hotel" | "flight" | "all"`
- `limit` (integer, optional): 返回结果数量，默认 10
- `offset` (integer, optional): 分页偏移量，默认 0

## 返回值

```json
{
  "results": [
    {
      "id": "dest_001",
      "type": "destination",
      "name": "巴黎",
      "country": "法国",
      "description": "浪漫之都，拥有丰富的历史文化和美食",
      "rating": 4.8,
      "reviews_count": 12500,
      "price_range": {
        "min": 1000,
        "max": 5000,
        "currency": "CNY"
      },
      "best_season": ["春季", "秋季"],
      "popular_attractions": ["埃菲尔铁塔", "卢浮宫", "凯旋门"]
    },
    {
      "id": "hotel_001",
      "type": "hotel",
      "name": "巴黎大酒店",
      "rating": 4.5,
      "price": 800,
      "currency": "CNY",
      "amenities": ["WiFi", "Pool", "Gym", "Breakfast"]
    }
  ],
  "total": 42,
  "search_quality": 0.85,
  "filters_applied": {
    "budget": {"min": 1000, "max": 5000},
    "preferences": ["culture", "food"]
  },
  "metadata": {
    "execution_time_ms": 450,
    "data_sources": ["internal_db", "java_api"]
  }
}
```

## 使用示例

### 基本搜索
```python
from src.skills.search import SearchSkill

skill = SearchSkill()
result = await skill.execute({
    "query": "Paris",
    "limit": 5
})
```

### 带过滤条件的搜索
```python
result = await skill.execute({
    "query": "Tokyo",
    "filters": {
        "budget": {"min": 5000, "max": 10000, "currency": "CNY"},
        "dates": {
            "check_in": "2024-06-01",
            "check_out": "2024-06-05"
        },
        "preferences": ["culture", "food", "shopping"],
        "travelers_count": 2
    },
    "limit": 10
})
```

### 搜索特定类型
```python
# 只搜索酒店
result = await skill.execute({
    "query": "Paris",
    "filters": {
        "search_type": "hotel",
        "dates": {
            "check_in": "2024-06-01",
            "check_out": "2024-06-05"
        }
    }
})
```

## 成本与性能

- **平均执行时间**: 500ms
- **Token 成本估计**: $0.05 per call
- **API 调用成本**: 取决于后端 Java API
- **缓存策略**: 相同查询参数结果缓存 1 小时

## 依赖

- Java API 后端 `/search/destinations` 接口
- Redis 缓存（可选）
- RAG 知识库（用于增强搜索结果）

## 错误处理

### 常见错误
- `INVALID_QUERY`: 查询参数为空或格式不正确
- `JAVA_API_ERROR`: 后端 Java API 不可用
- `TIMEOUT`: 搜索超时（超过 30 秒）

### 降级策略
如果 Java API 不可用，返回 mock 数据并标记 `mock: true`。

## 版本历史

- **v1.0.0** (2024-01): 初始版本，支持基本搜索和过滤
