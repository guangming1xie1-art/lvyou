# Search Agent Skills

**版本**: 1.0.0  
**Agent类型**: search  
**描述**: 搜索代理负责搜索和筛选航班、酒店等旅行选项，并进行结果比较和排序

---

## Skills

### search_flights

**描述**: 搜索并返回给定路线和日期的可用航班

**版本**: 1.0.0  
**Agent类型**: search  

**输入参数**:
- `origin` (string): 出发城市或机场代码 [必须]
- `destination` (string): 到达城市或机场代码 [必须]
- `departure_date` (string): 出发日期(YYYY-MM-DD) [必须]
- `return_date` (string): 返回日期(YYYY-MM-DD)用于往返 [可选]
- `passengers` (integer): 乘客数量 [必须] [默认: 1]
- `cabin_class` (string): 舱位等级偏好 [可选] [默认: economy] (enum: ["economy", "premium_economy", "business", "first"])
- `max_results` (integer): 返回的最大结果数量 [可选] [默认: 10]

**输出格式**:
- `outbound_flights` (array): 出发航班列表 [必须]
  - `flight_id` (string): 航班ID
  - `airline` (string): 航空公司
  - `flight_number` (string): 航班号
  - `departure_time` (string): 出发时间
  - `arrival_time` (string): 到达时间
  - `duration_minutes` (integer): 飞行时长(分钟)
  - `stops` (integer): 经停次数
  - `price_per_person` (number): 每人价格
  - `total_price` (number): 总价格
  - `currency` (string): 货币
  - `available_seats` (integer): 可用座位数
  - `cabin_class` (string): 舱位等级
- `return_flights` (array): 如果是往返航班则返回航班列表 [必须]
- `search_metadata` (object): 搜索元数据 [必须]
  - `origin` (string): 出发地
  - `destination` (string): 目的地
  - `departure_date` (string): 出发日期
  - `return_date` (string): 返回日期
  - `passengers` (integer): 乘客数
  - `results_count` (integer): 结果数量

**使用示例**:
```json
// 请求示例
{
  "origin": "NYC",
  "destination": "Tokyo",
  "departure_date": "2026-03-15",
  "return_date": "2026-03-22",
  "passengers": 2,
  "cabin_class": "economy",
  "max_results": 5
}

// 响应示例
{
  "outbound_flights": [
    {
      "flight_id": "FL-SA-001",
      "airline": "SkyAir",
      "flight_number": "SA101",
      "departure_time": "08:00",
      "arrival_time": "14:30",
      "duration_minutes": 810,
      "stops": 0,
      "price_per_person": 1200.00,
      "total_price": 2400.00,
      "currency": "USD",
      "available_seats": 15,
      "cabin_class": "economy"
    }
  ],
  "return_flights": [...],
  "search_metadata": {
    "origin": "NYC",
    "destination": "Tokyo",
    "departure_date": "2026-03-15",
    "return_date": "2026-03-22",
    "passengers": 2,
    "results_count": 5
  }
}
```

**错误处理**: InvalidInput - 当origin、destination、departure_date或passengers为空时抛出

---

### search_hotels

**描述**: 搜索并返回给定目的地和日期的可用酒店

**版本**: 1.0.0  
**Agent类型**: search  

**输入参数**:
- `destination` (string): 目的地城市或地区 [必须]
- `check_in_date` (string): 入住日期(YYYY-MM-DD) [必须]
- `check_out_date` (string): 退房日期(YYYY-MM-DD) [必须]
- `guests` (integer): 客人数量 [可选] [默认: 2]
- `rooms` (integer): 房间数量 [可选] [默认: 1]
- `min_rating` (number): 最低酒店评级(1-5星) [可选] [默认: 0]
- `max_results` (integer): 返回的最大结果数量 [可选] [默认: 10]

**输出格式**:
- `hotels` (array): 酒店列表 [必须]
  - `hotel_id` (string): 酒店ID
  - `name` (string): 酒店名称
  - `rating` (number): 星级评级
  - `review_count` (integer): 评论数量
  - `review_score` (number): 评论分数
  - `address` (string): 地址
  - `distance_to_center` (string): 到市中心的距离
  - `amenities` (array): 设施列表
  - `room_type` (string): 房间类型
  - `price_per_night` (number): 每晚价格
  - `total_price` (number): 总价格
  - `currency` (string): 货币
  - `cancellation_policy` (string): 取消政策
  - `breakfast_included` (boolean): 是否包含早餐
- `search_metadata` (object): 搜索元数据 [必须]
  - `destination` (string): 目的地
  - `check_in` (string): 入住日期
  - `check_out` (string): 退房日期
  - `nights` (integer): 夜数
  - `guests` (integer): 客人数
  - `results_count` (integer): 结果数量

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "check_in_date": "2026-03-15",
  "check_out_date": "2026-03-20",
  "guests": 2,
  "rooms": 1,
  "min_rating": 4,
  "max_results": 5
}

// 响应示例
{
  "hotels": [
    {
      "hotel_id": "HTL-TOK-001",
      "name": "Grand Plaza Hotel",
      "rating": 5,
      "review_count": 1250,
      "review_score": 9.2,
      "address": "100 Main Street, Tokyo",
      "distance_to_center": "0.5 km",
      "amenities": ["Pool", "Spa", "Gym", "Restaurant", "WiFi", "Parking"],
      "room_type": "Deluxe King Room",
      "price_per_night": 250,
      "total_price": 1250,
      "currency": "USD",
      "cancellation_policy": "Free cancellation up to 24 hours before check-in",
      "breakfast_included": true
    }
  ],
  "search_metadata": {
    "destination": "Tokyo",
    "check_in": "2026-03-15",
    "check_out": "2026-03-20",
    "nights": 5,
    "guests": 2,
    "results_count": 5
  }
}
```

**错误处理**: InvalidInput - 当destination、check_in_date或check_out_date为空时抛出

---

### compare_results

**描述**: 比较和排序多个搜索结果基于各种标准

**版本**: 1.0.0  
**Agent类型**: search  

**输入参数**:
- `result_type` (string): 要比较的结果类型 [必须] (enum: ["flights", "hotels", "mixed"])
- `results` (array): 要比较的搜索结果数组 [必须]
- `criteria` (object): 比较标准权重 [可选]
  - `price` (number): 价格权重 [默认: 0.4]
  - `quality` (number): 质量权重 [默认: 0.3]
  - `convenience` (number): 便利性权重 [默认: 0.3]
- `max_recommendations` (integer): 顶部推荐的最大数量 [可选] [默认: 3]

**输出格式**:
- `top_recommendations` (array): 顶部推荐列表 [必须]
  - `rank` (integer): 排名
  - `item` (object): 原始项目
  - `score` (number): 综合得分
  - `strengths` (array): 优势列表
  - `weaknesses` (array): 劣势列表
  - `recommendation_reason` (string): 推荐理由
- `comparison_summary` (object): 比较摘要 [必须]
  - `best_value` (object): 最具性价比
  - `best_quality` (object): 最佳质量
  - `most_convenient` (object): 最便利
  - `price_range` (object): 价格范围

**使用示例**:
```json
// 请求示例
{
  "result_type": "hotels",
  "results": [
    {
      "hotel_id": "HTL-001",
      "name": "Grand Plaza",
      "rating": 5,
      "price_per_night": 250,
      "total_price": 1250,
      "distance_to_center": "0.5 km"
    }
  ],
  "criteria": {
    "price": 0.5,
    "quality": 0.3,
    "convenience": 0.2
  },
  "max_recommendations": 3
}

// 响应示例
{
  "top_recommendations": [
    {
      "rank": 1,
      "item": {...},
      "score": 0.85,
      "strengths": ["Excellent value for money", "High quality option"],
      "weaknesses": [],
      "recommendation_reason": "Best overall choice with a score of 0.85/1.0. Excellent balance of price, quality, and convenience."
    }
  ],
  "comparison_summary": {
    "best_value": {...},
    "best_quality": {...},
    "most_convenient": {...},
    "price_range": {
      "min": 120,
      "max": 400,
      "average": 200
    }
  }
}
```

**错误处理**: InvalidInput - 当result_type或results为空时抛出

---

### filter_by_budget

**描述**: 筛选搜索结果以符合指定预算约束

**版本**: 1.0.0  
**Agent类型**: search  

**输入参数**:
- `options` (array): 要筛选的选项数组(航班、酒店等) [必须]
- `budget` (object): 预算约束 [必须]
  - `max_total` (number): 最大总预算
  - `max_per_person` (number): 每人最大预算
  - `currency` (string): 货币 [默认: USD]
- `option_type` (string): 被筛选的选项类型 [必须] (enum: ["flights", "hotels", "activities", "combined"])
- `sort_by` (string): 如何排序筛选结果 [可选] [默认: "price_low_to_high"] (enum: ["price_low_to_high", "price_high_to_low", "best_value"])

**输出格式**:
- `filtered_options` (array): 符合预算的选项 [必须]
- `excluded_options` (array): 因预算超限而排除的选项 [必须]
- `budget_summary` (object): 预算摘要 [必须]
  - `total_budget` (number): 总预算
  - `cheapest_option` (number): 最便宜选项
  - `most_expensive_option` (number): 最贵选项
  - `average_price` (number): 平均价格
  - `options_within_budget` (integer): 符合预算的选项数
  - `options_over_budget` (integer): 超出预算的选项数
  - `savings_potential` (number): 节省潜力

**使用示例**:
```json
// 请求示例
{
  "options": [
    {
      "hotel_id": "HTL-001",
      "name": "Grand Plaza",
      "price_per_night": 250,
      "total_price": 1250
    }
  ],
  "budget": {
    "max_total": 1000,
    "currency": "USD"
  },
  "option_type": "hotels",
  "sort_by": "price_low_to_high"
}

// 响应示例
{
  "filtered_options": [
    {
      "hotel_id": "HTL-001",
      "name": "Grand Plaza",
      "price_per_night": 250,
      "total_price": 1250,
      "_budget_info": {
        "price": 1250,
        "within_budget": false,
        "over_budget_by": 250
      }
    }
  ],
  "excluded_options": [...],
  "budget_summary": {
    "total_budget": 1000,
    "cheapest_option": 250,
    "most_expensive_option": 400,
    "average_price": 300,
    "options_within_budget": 3,
    "options_over_budget": 2,
    "savings_potential": 100
  }
}
```

**错误处理**: InvalidInput - 当options、budget或option_type为空时抛出
