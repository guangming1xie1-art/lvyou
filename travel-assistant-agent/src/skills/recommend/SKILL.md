# Skill: recommend

## 概述
基于用户偏好和搜索结果生成个性化旅游推荐方案。综合考虑预算、时间、偏好等因素，生成多个可选方案。

## 参数

### 输入参数
- `user_prefs` (object, required): 用户偏好信息
  - `budget` (object): 预算范围 `{min: number, max: number, currency: string}`
  - `dates` (object): 旅行日期 `{departure: string, return: string}`
  - `travelers_count` (integer): 旅行人数
  - `preferences` (array): 偏好标签，如 `["beach", "culture", "food", "adventure"]`
  - `accommodation_type` (string): 住宿类型 `"hotel" | "hostel" | "apartment" | "resort"`
  - `pace` (string): 行程节奏 `"relaxed" | "moderate" | "packed"`
- `search_results` (array, optional): 搜索结果列表（来自 search skill）
- `num_recommendations` (integer, optional): 生成推荐数量，默认 3

## 返回值

```json
{
  "recommendations": [
    {
      "id": "rec_001",
      "title": "经典巴黎 5 日游",
      "description": "包含主要景点和美食体验，适合首次访问",
      "confidence": 0.85,
      "total_cost": {
        "amount": 12000,
        "currency": "CNY",
        "breakdown": {
          "flights": 4000,
          "accommodation": 5000,
          "activities": 2000,
          "meals": 1000
        }
      },
      "itinerary": [
        {
          "day": 1,
          "title": "抵达巴黎",
          "activities": [
            {
              "time": "14:00",
              "activity": "入住酒店",
              "location": "市中心酒店",
              "duration": "1h"
            },
            {
              "time": "16:00",
              "activity": "塞纳河游船",
              "location": "塞纳河",
              "duration": "2h"
            }
          ]
        },
        {
          "day": 2,
          "title": "经典巴黎",
          "activities": [
            {
              "time": "09:00",
              "activity": "参观埃菲尔铁塔",
              "location": "埃菲尔铁塔",
              "duration": "2h"
            }
          ]
        }
      ],
      "highlights": [
        "埃菲尔铁塔登顶体验",
        "卢浮宫深度游览",
        "米其林推荐餐厅"
      ],
      "suitable_for": ["首次访问", "文化爱好者", "美食爱好者"],
      "pros": ["行程经典", "体验丰富", "适合拍照"],
      "cons": ["热门景点人多", "预算偏高"],
      "accommodation": {
        "name": "巴黎市中心酒店",
        "rating": 4.5,
        "location": "距离埃菲尔铁塔 2km"
      },
      "transportation": {
        "flights": "直飞航班",
        "local": "地铁 + 步行"
      }
    }
  ],
  "confidence": 0.82,
  "metadata": {
    "execution_time_ms": 800,
    "model_used": "qwen-turbo",
    "factors_considered": ["budget", "preferences", "season", "popularity"]
  }
}
```

## 使用示例

### 基本推荐
```python
from src.skills.recommend import RecommendSkill

skill = RecommendSkill()
result = await skill.execute({
    "user_prefs": {
        "budget": {"min": 5000, "max": 15000, "currency": "CNY"},
        "dates": {"departure": "2024-06-01", "return": "2024-06-05"},
        "travelers_count": 2,
        "preferences": ["culture", "food"]
    }
})
```

### 基于搜索结果推荐
```python
result = await skill.execute({
    "user_prefs": {
        "budget": {"min": 10000, "max": 20000, "currency": "CNY"},
        "dates": {"departure": "2024-07-01", "return": "2024-07-10"},
        "travelers_count": 4,
        "preferences": ["beach", "relaxation", "family"],
        "accommodation_type": "resort",
        "pace": "relaxed"
    },
    "search_results": search_results,  # 来自 search skill
    "num_recommendations": 5
})
```

## 成本与性能

- **平均执行时间**: 800ms
- **Token 成本估计**: $0.08 per call
- **模型**: qwen-turbo（标准层）
- **缓存策略**: 相同偏好结果缓存 6 小时

## 推荐算法

1. **用户画像分析**: 从偏好中提取关键特征
2. **目的地匹配**: 基于偏好匹配合适的目的地
3. **行程规划**: 生成合理的每日行程
4. **成本优化**: 在预算范围内优化方案
5. **多样性**: 生成风格不同的多个方案供选择

## 依赖

- Java API 后端 `/recommendations/generate` 接口
- LLM（qwen-turbo）用于生成行程描述
- Redis 缓存（可选）

## 错误处理

### 常见错误
- `INVALID_PREFERENCES`: 用户偏好格式不正确
- `NO_SUITABLE_OPTIONS`: 在预算和日期范围内没有合适方案
- `JAVA_API_ERROR`: 后端 API 不可用

### 降级策略
如果 Java API 不可用，使用 LLM 生成基础推荐方案。

## 版本历史

- **v1.0.0** (2024-01): 初始版本，支持基本推荐和行程规划
