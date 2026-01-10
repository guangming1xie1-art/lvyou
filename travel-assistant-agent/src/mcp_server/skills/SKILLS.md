# Claude Skills - 完整技能文档

**版本**: 1.0.0  
**项目**: lvyou (旅游助手)  
**描述**: Claude Skills是模块化的AI技能系统，按Agent职责组织，用于构建智能旅游助手

---

## 架构概览

Claude Skills采用模块化设计，按Agent职责分为4大类，共19个技能：

### Agent类型

1. **InfoCollection Agent** (信息收集代理)
   - 负责收集和验证用户旅行偏好信息
   - 包含3个技能
   - 📁 [详细文档](info_collection/SKILLS.md)

2. **Search Agent** (搜索代理)
   - 负责搜索和筛选航班、酒店等旅行选项
   - 包含4个技能
   - 📁 [详细文档](search/SKILLS.md)

3. **Recommendation Agent** (推荐代理)
   - 负责提供目的地信息、景点推荐、天气预报和用户评价
   - 包含4个技能
   - 📁 [详细文档](recommendation/SKILLS.md)

4. **Booking Agent** (预订代理)
   - 负责处理完整的预订流程
   - 包含4个技能
   - 📁 [详细文档](booking/SKILLS.md)

### 独立技能

除了按Agent组织的技能外，还有5个独立技能：

- **destination** - 目的地搜索和信息获取
- **planning** - 旅行计划创建
- **pricing** - 价格查询
- **reviews** - 用户评价获取
- **weather** - 天气查询

---

## 技能索引

### InfoCollection Agent (3个技能)

| 技能名称 | 功能描述 | 版本 |
|---------|---------|------|
| [get_user_preferences](info_collection/SKILLS.md#get_user_preferences) | 收集用户旅行信息包括目的地、日期、预算、团体规模和个人偏好 | 1.0.0 |
| [validate_user_input](info_collection/SKILLS.md#validate_user_input) | 验证和规范化用户旅行偏好输入数据 | 1.0.0 |
| [suggest_destinations](info_collection/SKILLS.md#suggest_destinations) | 基于用户偏好和约束条件推荐热门目的地 | 1.0.0 |

### Search Agent (4个技能)

| 技能名称 | 功能描述 | 版本 |
|---------|---------|------|
| [search_flights](search/SKILLS.md#search_flights) | 搜索并返回给定路线和日期的可用航班 | 1.0.0 |
| [search_hotels](search/SKILLS.md#search_hotels) | 搜索并返回给定目的地和日期的可用酒店 | 1.0.0 |
| [compare_results](search/SKILLS.md#compare_results) | 比较和排序多个搜索结果基于各种标准 | 1.0.0 |
| [filter_by_budget](search/SKILLS.md#filter_by_budget) | 筛选搜索结果以符合指定预算约束 | 1.0.0 |

### Recommendation Agent (4个技能)

| 技能名称 | 功能描述 | 版本 |
|---------|---------|------|
| [get_destination_info](recommendation/SKILLS.md#get_destination_info) | 获取目的地的一般信息包括描述、货币、语言和签证要求 | 1.0.0 |
| [get_attractions](recommendation/SKILLS.md#get_attractions) | 获取目的地的热门景点、活动和体验 | 1.0.0 |
| [get_weather_forecast](recommendation/SKILLS.md#get_weather_forecast) | 获取目的地和旅行日期的天气预报以及打包建议 | 1.0.0 |
| [get_destination_reviews](recommendation/SKILLS.md#get_destination_reviews) | 获取旅行目的地的用户评价、评分和情感分析 | 1.0.0 |

### Booking Agent (4个技能)

| 技能名称 | 功能描述 | 版本 |
|---------|---------|------|
| [create_booking](booking/SKILLS.md#create_booking) | 为选定的旅行选项创建新的预订订单 | 1.0.0 |
| [process_payment](booking/SKILLS.md#process_payment) | 处理预订的支付包括验证、授权和交易确认 | 1.0.0 |
| [confirm_booking](booking/SKILLS.md#confirm_booking) | 在成功支付后确认预订并生成确认详情 | 1.0.0 |
| [get_booking_status](booking/SKILLS.md#get_booking_status) | 使用预订ID或确认号查询现有预订的当前状态 | 1.0.0 |

### 独立技能 (5个技能)

| 技能名称 | 功能描述 | 版本 |
|---------|---------|------|
| [search_destination](#search_destination) | 搜索目的地信息包括景点、文化、最佳旅行时间和当地建议 | 1.0.0 |
| [create_travel_plan](#create_travel_plan) | 基于目的地、预算和偏好创建详细的旅行行程 | 1.0.0 |
| [query_prices](#query_prices) | 查询酒店和航班价格帮助旅行者规划预算 | 1.0.0 |
| [get_destination_reviews](#get_destination_reviews) | 获取旅行目的地的用户评价、评分和情感分析 | 1.0.0 |
| [get_weather](#get_weather) | 获取旅行目的地的当前天气和预报帮助打包和规划 | 1.0.0 |

---

## 独立技能详细文档

### search_destination

**描述**: 搜索目的地信息包括景点、文化、最佳旅行时间和当地建议

**版本**: 1.0.0  
**分类**: destination  

**输入参数**:
- `destination` (string): 目的地名称(城市、国家或地区) [必须]
- `language` (string): 信息首选语言 [可选] [默认: en]
- `include_tips` (boolean): 是否包含旅行建议和推荐 [可选] [默认: true]

**输出格式**:
- `destination` (string): 目的地名称 [必须]
- `country` (string): 国家 [必须]
- `region` (string): 地区 [必须]
- `description` (string): 描述 [必须]
- `highlights` (array): 亮点列表 [必须]
- `best_time_to_visit` (string): 最佳旅行时间 [必须]
- `average_duration` (string): 平均停留时间 [必须]
- `local_tips` (array): 当地建议 [必须]
- `currency` (string): 货币 [必须]
- `language` (string): 语言 [必须]
- `visa_info` (string): 签证信息 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "language": "en",
  "include_tips": true
}

// 响应示例
{
  "destination": "Tokyo",
  "country": "Japan",
  "region": "Asia",
  "description": "东京是一个充满活力的都市，融合了超现代与传统文化的城市",
  "highlights": [
    "浅草寺",
    "涩谷十字路口",
    "东京塔和天空树",
    "皇居",
    "筑地场外市场",
    "秋叶原电器街"
  ],
  "best_time_to_visit": "3-5月(樱花季)或9-11月(秋季)",
  "average_duration": "5-7天",
  "local_tips": [
    "购买Suica或Pasmo卡方便交通",
    "下载离线地图-东京地铁可能很复杂",
    "日本不流行小费",
    "携带现金-许多小商店不接受卡"
  ],
  "currency": "Japanese Yen (JPY)",
  "language": "Japanese",
  "visa_info": "许多国家免签最多30天"
}
```

**错误处理**: 抛出ValueError当destination为空时

---

### create_travel_plan

**描述**: 基于目的地、预算和偏好创建详细的旅行行程

**版本**: 1.0.0  
**分类**: planning  

**输入参数**:
- `destination` (string): 旅行目的地 [必须]
- `duration_days` (integer): 旅行天数 [可选] [默认: 5]
- `budget` (number): 总预算(美元) [可选]
- `travel_dates` (object): 旅行日期 [可选]
  - `start` (string): 开始日期
  - `end` (string): 结束日期
- `interests` (array): 旅行者兴趣和偏好 [可选]
- `accommodation_type` (string): 首选住宿风格 [可选] [默认: mid-range]
- `pace` (string): 旅行节奏 [可选] [默认: moderate] (enum: ["relaxed", "moderate", "packed"])

**输出格式**:
- `destination` (string): 目的地 [必须]
- `title` (string): 行程标题 [必须]
- `overview` (string): 概述 [必须]
- `itinerary` (array): 行程安排 [必须]
  - `day` (integer): 天数
  - `date` (string): 日期
  - `theme` (string): 主题
  - `activities` (array): 活动列表
  - `meals` (array): 餐饮安排
  - `accommodation` (string): 住宿
  - `transport` (string): 交通
- `budget_breakdown` (object): 预算明细 [必须]
  - `flights` (number): 航班费用
  - `accommodation` (number): 住宿费用
  - `food` (number): 餐饮费用
  - `activities` (number): 活动费用
  - `transport` (number): 交通费用
  - `buffer` (number): 缓冲费用
  - `total` (number): 总计
- `packing_list` (array): 打包清单 [必须]
- `tips` (array): 建议 [必须]
- `booking_recommendations` (array): 预订建议 [必须]

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "duration_days": 5,
  "budget": 3000,
  "interests": ["culture", "food", "technology"],
  "accommodation_type": "mid-range",
  "pace": "moderate"
}

// 响应示例
{
  "destination": "Tokyo",
  "title": "东京探险",
  "overview": "在日本的充满活力的首都体验尖端技术与古老传统的完美融合",
  "itinerary": [
    {
      "day": 1,
      "date": "Day 1",
      "theme": "抵达与传统东京",
      "activities": ["抵达成田/羽田机场", "新宿酒店入住", "探索涩谷十字路口", "当地居酒屋晚餐"],
      "meals": ["飞机上早餐", "涩谷咖啡厅午餐", "居酒屋晚餐"],
      "accommodation": "新宿酒店",
      "transport": "机场快线+地铁"
    }
  ],
  "budget_breakdown": {
    "flights": 900,
    "accommodation": 750,
    "food": 600,
    "activities": 450,
    "transport": 150,
    "buffer": 150,
    "total": 3000
  },
  "packing_list": [
    "舒适的步行鞋",
    "Suica/Pasmo交通卡",
    "便携式WiFi或SIM卡",
    "电源适配器(Type A/B)",
    "轻便雨衣",
    "现金(许多地方不接受卡)"
  ],
  "tips": [
    "购买IC卡(Suica/Pasmo/ICOCA)方便交通",
    "下载Google Maps离线地图",
    "JR Pass对于一日游可能值得",
    "地铁高峰时段非常拥挤",
    "大多数博物馆周一关闭"
  ],
  "booking_recommendations": [
    "提前预订新干线车票进行一日游",
    "高端餐厅预订座位",
    "考虑包含早餐的酒店",
    "在线预订TeamLab门票避免排队"
  ]
}
```

**错误处理**: 抛出ValueError当destination为空时

---

### query_prices

**描述**: 查询酒店和航班价格帮助旅行者规划预算

**版本**: 1.0.0  
**分类**: pricing  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `check_in` (string): 入住日期(YYYY-MM-DD) [可选]
- `check_out` (string): 退房日期(YYYY-MM-DD) [可选]
- `guests` (integer): 客人数量 [可选] [默认: 2]
- `rooms` (integer): 所需房间数量 [可选] [默认: 1]
- `flight_class` (string): 航班舱位 [可选] [默认: economy] (enum: ["economy", "business", "first"])

**输出格式**:
- `destination` (string): 目的地 [必须]
- `dates` (object): 日期信息 [必须]
  - `check_in` (string): 入住日期
  - `check_out` (string): 退房日期
  - `nights` (integer): 夜数
- `hotels` (array): 酒店列表 [必须]
  - `name` (string): 酒店名称
  - `rating` (number): 评级
  - `price_per_night` (number): 每晚价格
  - `total_price` (number): 总价格
  - `amenities` (array): 设施列表
  - `location` (string): 位置
- `flights` (array): 航班列表 [必须]
  - `airline` (string): 航空公司
  - `price` (number): 价格
  - `duration` (string): 时长
  - `stops` (number): 经停次数
  - `class` (string): 舱位
- `total_budget_estimate` (object): 总预算估计 [必须]
  - `budget` (string): 预算类型
  - `hotel_total` (number): 酒店总计
  - `flight_total` (number): 航班总计
  - `daily_budget` (number): 日均预算

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "check_in": "2026-03-15",
  "check_out": "2026-03-20",
  "guests": 2,
  "rooms": 1,
  "flight_class": "economy"
}

// 响应示例
{
  "destination": "Tokyo",
  "dates": {
    "check_in": "2026-03-15",
    "check_out": "2026-03-20",
    "nights": 5
  },
  "hotels": [
    {
      "name": "Grand Plaza Hotel",
      "rating": 4.5,
      "price_per_night": 250,
      "total_price": 1250,
      "amenities": ["WiFi", "游泳池", "健身房", "餐厅", "客房服务"],
      "location": "市中心"
    }
  ],
  "flights": [
    {
      "airline": "主要航空公司",
      "price": 1600,
      "duration": "12-14小时",
      "stops": 0,
      "class": "economy"
    }
  ],
  "total_budget_estimate": {
    "budget": "mid-range",
    "hotel_total": 1250,
    "flight_total": 1600,
    "daily_budget": 570
  }
}
```

**错误处理**: 抛出ValueError当destination为空时

---

### get_destination_reviews

**描述**: 获取旅行目的地的用户评价、评分和情感分析

**版本**: 1.0.0  
**分类**: reviews  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `category` (string): 按类别筛选 [可选] [默认: general] (enum: ["general", "hotels", "attractions", "restaurants"])
- `limit` (integer): 返回的评价数量 [可选] [默认: 5]
- `include_sentiment` (boolean): 是否包含情感分析 [可选] [默认: true]

**输出格式**:
- `destination` (string): 目的地 [必须]
- `overall_rating` (number): 总体评分 [必须]
- `total_reviews` (integer): 总评价数 [必须]
- `sentiment_breakdown` (object): 情感分布 [必须]
  - `positive` (number): 积极评价比例
  - `neutral` (number): 中性评价比例
  - `negative` (number): 消极评价比例
- `rating_breakdown` (object): 评分分布 [必须]
  - `5_star` (number): 5星数量
  - `4_star` (number): 4星数量
  - `3_star` (number): 3星数量
  - `2_star` (number): 2星数量
  - `1_star` (number): 1星数量
- `reviews` (array): 评价列表 [必须]
  - `author` (string): 作者
  - `rating` (number): 评分
  - `date` (string): 日期
  - `title` (string): 标题
  - `content` (string): 内容
  - `sentiment` (string): 情感(可选)
- `pros_cons` (object): 优缺点 [必须]
  - `pros` (array): 优点列表
  - `cons` (array): 缺点列表

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "category": "general",
  "limit": 3,
  "include_sentiment": true
}

// 响应示例
{
  "destination": "Tokyo",
  "overall_rating": 4.7,
  "total_reviews": 15420,
  "sentiment_breakdown": {
    "positive": 85,
    "neutral": 12,
    "negative": 3
  },
  "rating_breakdown": {
    "5_star": 60,
    "4_star": 25,
    "3_star": 10,
    "2_star": 3,
    "1_star": 2
  },
  "reviews": [
    {
      "author": "Traveler_123",
      "rating": 5,
      "date": "2024-03-15",
      "title": "新旧融合的绝佳体验！",
      "content": "东京超出了所有期望。食物、人民、技术——一切都令人难以置信。涩谷十字路口是必看之地！",
      "sentiment": "positive"
    }
  ],
  "pros_cons": {
    "pros": [
      "优秀的公共交通",
      "出色的美食",
      "安全和清洁",
      "丰富的文化和历史",
      "尖端技术"
    ],
    "cons": [
      "可能很昂贵",
      "旅游区外有语言障碍",
      "旺季拥挤",
      "住宿可能较小"
    ]
  }
}
```

**错误处理**: 抛出ValueError当destination为空时

---

### get_weather

**描述**: 获取旅行目的地的当前天气和预报帮助打包和规划

**版本**: 1.0.0  
**分类**: weather  

**输入参数**:
- `destination` (string): 目的地名称 [必须]
- `start_date` (string): 旅行开始日期(YYYY-MM-DD) [可选]
- `end_date` (string): 旅行结束日期(YYYY-MM-DD) [可选]
- `include_forecast` (boolean): 是否包含旅行日期的每日预报 [可选] [默认: true]

**输出格式**:
- `destination` (string): 目的地 [必须]
- `current` (object): 当前天气 [必须]
  - `temperature` (number): 温度
  - `condition` (string): 天气状况
  - `humidity` (number): 湿度
  - `wind_speed` (number): 风速
  - `uv_index` (number): 紫外线指数
- `forecast` (array): 预报列表 [可选]
  - `date` (string): 日期
  - `temperature_high` (number): 最高温度
  - `temperature_low` (number): 最低温度
  - `condition` (string): 天气状况
  - `precipitation_chance` (number): 降雨概率
- `packing_recommendations` (array): 打包建议 [必须]
- `best_activities` (object): 最佳活动 [必须]
  - `indoor` (array): 室内活动
  - `outdoor` (array): 户外活动

**使用示例**:
```json
// 请求示例
{
  "destination": "Tokyo",
  "start_date": "2026-03-15",
  "end_date": "2026-03-20",
  "include_forecast": true
}

// 响应示例
{
  "destination": "Tokyo",
  "current": {
    "temperature": 18,
    "condition": "多云",
    "humidity": 65,
    "wind_speed": 12,
    "uv_index": 5
  },
  "forecast": [
    {
      "date": "2024-03-15",
      "temperature_high": 22,
      "temperature_low": 15,
      "condition": "晴朗",
      "precipitation_chance": 10
    }
  ],
  "packing_recommendations": [
    "轻薄层次穿搭",
    "紧凑雨伞(雨季：6-7月)",
    "舒适的步行鞋",
    "晚上用的轻便外套"
  ],
  "best_activities": {
    "indoor": ["博物馆", "购物中心", "寺庙", "动漫区"],
    "outdoor": ["赏樱(3-4月)", "公园", "屋顶酒吧"]
  }
}
```

**错误处理**: 抛出ValueError当destination为空时

---

## 使用指南

### 技能调用流程

典型的旅游助手工作流程：

1. **信息收集阶段**
   - 使用 `get_user_preferences` 收集用户偏好
   - 使用 `validate_user_input` 验证数据
   - 使用 `suggest_destinations` 提供目的地建议

2. **搜索阶段**
   - 使用 `search_flights` 查找航班
   - 使用 `search_hotels` 查找酒店
   - 使用 `compare_results` 比较选项
   - 使用 `filter_by_budget` 按预算筛选

3. **推荐阶段**
   - 使用 `get_destination_info` 获取目的地信息
   - 使用 `get_attractions` 获取景点推荐
   - 使用 `get_weather_forecast` 查看天气
   - 使用 `get_destination_reviews` 查看评价

4. **预订阶段**
   - 使用 `create_booking` 创建预订
   - 使用 `process_payment` 处理支付
   - 使用 `confirm_booking` 确认预订
   - 使用 `get_booking_status` 查询状态

### API调用示例

每个技能都可以通过MCP协议调用：

```python
# 调用技能示例
result = await mcp_client.call_tool(
    "get_user_preferences",
    {
        "user_message": "我想去东京旅行，预算2500美元，喜欢文化和美食",
        "conversation_history": []
    }
)
```

### 错误处理

所有技能都会在输入验证失败时抛出 `ValueError`。建议在调用前：

1. 检查必需参数
2. 验证参数格式
3. 处理网络异常
4. 记录错误日志

---

## 版本历史

- **v1.0.0** - 初始版本，包含19个技能的完整实现
  - 4个Agent类型的15个技能
  - 5个独立技能
  - 完整的输入/输出schema定义
  - 中文文档支持

---

## 贡献指南

如需添加新技能或修改现有技能，请遵循以下规范：

1. 继承 `BaseSkill` 类
2. 定义 `name`, `description`, `version` 属性
3. 实现 `input_schema` 和 `output_schema`
4. 实现 `execute` 方法
5. 添加中文文档
6. 更新相应的SKILLS.md文件

更多详细信息请参考 [开发文档](../README.md)
