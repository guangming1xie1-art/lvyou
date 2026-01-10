# Recommendation Agent Skills

**版本**: 1.0.0  
**Agent类型**: recommendation  
**描述**: 推荐代理负责提供目的地信息、景点推荐、天气预报和用户评价，帮助用户做出更好的旅行决策

---

## Skills

### get_destination_info

**描述**: 获取目的地的一般信息包括描述、货币、语言和签证要求

**版本**: 1.0.0  
**Agent类型**: recommendation  

**输入参数**:
- `destination` (string): 目的地名称(城市、国家或地区) [必须]
- `language` (string): 信息首选语言 [可选] [默认: en]

**输出格式**:
- `destination` (string): 目的地名称 [必须]
- `country` (string): 国家 [必须]
- `region` (string): 地区 [必须]
- `description` (string): 描述 [必须]
- `best_time_to_visit` (string): 最佳旅行时间 [必须]
- `average_duration` (string): 平均停留时间 [必须]
- `currency` (string): 货币 [必须]
- `language` (string): 语言 [必须]
- `visa_info` (string): 签证信息 [必须]
- `local_tips` (array): 当地建议 [必须]
- `timezone` (string): 时区 [必须]
- `emergency_number` (string): 紧急联系电话 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "language": "en"
}

// 响应示例
{
  "destination": "Tokyo",
  "country": "Japan",
  "region": "Asia",
  "description": "东京是一个充满活力的都市，融合了超现代与传统文化的城市",
  "best_time_to_visit": "3-5月(樱花季)或9-11月(秋季)",
  "average_duration": "5-7天",
  "currency": "Japanese Yen (JPY)",
  "language": "Japanese",
  "visa_info": "许多国家免签最多90天",
  "local_tips": [
    "购买Suica或Pasmo卡方便交通",
    "下载离线地图-东京地铁可能很复杂",
    "日本不流行小费",
    "携带现金-许多小商店不接受卡"
  ],
  "timezone": "JST (UTC+9)",
  "emergency_number": "110 (警察), 119 (急救/消防)"
}
```

**错误处理**: InvalidInput - 当destination为空时抛出

---

### get_attractions

**描述**: 获取目的地的热门景点、活动和体验

**版本**: 1.0.0  
**Agent类型**: recommendation  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `category` (string): 按类别筛选 [可选] [默认: all] (enum: ["all", "culture", "nature", "food", "entertainment", "adventure"])
- `max_results` (integer): 返回的最大结果数量 [可选] [默认: 10]

**输出格式**:
- `destination` (string): 目的地名称 [必须]
- `attractions` (array): 景点列表 [必须]
  - `name` (string): 景点名称
  - `category` (string): 类别
  - `description` (string): 描述
  - `rating` (number): 评分
  - `estimated_duration` (string): 预计游览时间
  - `best_time_to_visit` (string): 最佳游览时间
  - `entrance_fee` (string): 门票费用
  - `must_see` (boolean): 是否必看
- `total_count` (integer): 总数量 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "category": "culture",
  "max_results": 3
}

// 响应示例
{
  "destination": "Tokyo",
  "attractions": [
    {
      "name": "浅草寺",
      "category": "culture",
      "description": "东京最古老的寺庙，气氛活跃",
      "rating": 4.5,
      "estimated_duration": "1-2小时",
      "best_time_to_visit": "清晨以避开人群",
      "entrance_fee": "免费",
      "must_see": true
    },
    {
      "name": "明治神宫",
      "category": "culture",
      "description": "森林中的宁静神社",
      "rating": 4.5,
      "estimated_duration": "1小时",
      "best_time_to_visit": "早上",
      "entrance_fee": "免费",
      "must_see": true
    }
  ],
  "total_count": 2
}
```

**错误处理**: InvalidInput - 当destination为空时抛出

---

### get_weather_forecast

**描述**: 获取目的地和旅行日期的天气预报以及打包建议

**版本**: 1.0.0  
**Agent类型**: recommendation  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `start_date` (string): 旅行开始日期(YYYY-MM-DD) [必须]
- `end_date` (string): 旅行结束日期(YYYY-MM-DD) [可选]

**输出格式**:
- `destination` (string): 目的地名称 [必须]
- `forecast_period` (object): 预报时间段 [必须]
  - `start_date` (string): 开始日期
  - `end_date` (string): 结束日期
  - `days` (integer): 天数
- `daily_forecast` (array): 每日预报 [必须]
  - `date` (string): 日期
  - `day_of_week` (string): 星期几
  - `temperature_high` (number): 最高温度
  - `temperature_low` (number): 最低温度
  - `condition` (string): 天气状况
  - `precipitation_chance` (number): 降雨概率
  - `humidity` (number): 湿度
  - `wind_speed` (number): 风速
- `summary` (object): 摘要 [必须]
  - `average_high` (number): 平均最高温
  - `average_low` (number): 平均最低温
  - `most_common_condition` (string): 最常见天气状况
  - `rainy_days` (integer): 雨天数
- `packing_recommendations` (array): 打包建议 [必须]
- `weather_alerts` (array): 天气警报 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "start_date": "2026-03-15",
  "end_date": "2026-03-20"
}

// 响应示例
{
  "destination": "Tokyo",
  "forecast_period": {
    "start_date": "2026-03-15",
    "end_date": "2026-03-20",
    "days": 6
  },
  "daily_forecast": [
    {
      "date": "2026-03-15",
      "day_of_week": "Monday",
      "temperature_high": 22,
      "temperature_low": 15,
      "condition": "Sunny",
      "precipitation_chance": 30,
      "humidity": 65,
      "wind_speed": 12
    }
  ],
  "summary": {
    "average_high": 21.5,
    "average_low": 14.8,
    "most_common_condition": "Sunny",
    "rainy_days": 1
  },
  "packing_recommendations": [
    "轻薄透气衣物",
    "防晒霜",
    "帽子",
    "太阳镜",
    "轻便雨衣"
  ],
  "weather_alerts": []
}
```

**错误处理**: InvalidInput - 当destination或start_date为空时抛出

---

### get_destination_reviews

**描述**: 获取旅行目的地的用户评价、评分和情感分析

**版本**: 1.0.0  
**Agent类型**: recommendation  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `category` (string): 评价类别筛选 [可选] [默认: general] (enum: ["general", "hotels", "attractions", "restaurants", "transportation"])
- `limit` (integer): 返回的评价数量 [可选] [默认: 5]

**输出格式**:
- `destination` (string): 目的地名称 [必须]
- `overall_rating` (number): 总体评分 [必须]
- `total_reviews` (integer): 总评价数 [必须]
- `rating_breakdown` (object): 评分分布 [必须]
  - `5_star` (integer): 5星数量
  - `4_star` (integer): 4星数量
  - `3_star` (integer): 3星数量
  - `2_star` (integer): 2星数量
  - `1_star` (integer): 1星数量
- `sentiment_breakdown` (object): 情感分布 [必须]
  - `positive` (number): 积极评价比例
  - `neutral` (number): 中性评价比例
  - `negative` (number): 消极评价比例
- `reviews` (array): 评价列表 [必须]
  - `author` (string): 作者
  - `rating` (number): 评分
  - `date` (string): 日期
  - `title` (string): 标题
  - `content` (string): 内容
  - `helpful_count` (integer): 有用计数
  - `verified_traveler` (boolean): 是否已验证旅行者
- `pros_cons` (object): 优缺点 [必须]
  - `pros` (array): 优点列表
  - `cons` (array): 缺点列表
- `recommended_by` (number): 推荐百分比 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "category": "general",
  "limit": 3
}

// 响应示例
{
  "destination": "Tokyo",
  "overall_rating": 4.6,
  "total_reviews": 12580,
  "rating_breakdown": {
    "5_star": 7800,
    "4_star": 3200,
    "3_star": 1100,
    "2_star": 350,
    "1_star": 130
  },
  "sentiment_breakdown": {
    "positive": 0.82,
    "neutral": 0.13,
    "negative": 0.05
  },
  "reviews": [
    {
      "author": "Sarah M.",
      "rating": 5.0,
      "date": "2024-01-15",
      "title": "传统与现代的完美融合",
      "content": "东京超出所有期望！公共交通非常高效，食物很棒，能看的东西很多。早上参观寺庙，晚上探索充满活力的社区。",
      "helpful_count": 245,
      "verified_traveler": true
    }
  ],
  "pros_cons": {
    "pros": [
      "优秀的公共交通",
      "安全且干净",
      "出色的美食",
      "高效且有序",
      "丰富的文化和历史"
    ],
    "cons": [
      "可能很贵",
      "语言障碍",
      "高峰时段拥挤",
      "地铁系统最初令人困惑"
    ]
  },
  "recommended_by": 92
}
```

**错误处理**: InvalidInput - 当destination为空时抛出
