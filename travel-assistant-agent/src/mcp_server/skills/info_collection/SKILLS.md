# InfoCollection Agent Skills

**版本**: 1.0.0  
**Agent类型**: info_collection  
**描述**: 信息收集代理负责收集和验证用户旅行偏好信息，为后续搜索和推荐提供基础数据

---

## Skills

### get_user_preferences

**描述**: 收集用户旅行信息包括目的地、日期、预算、团体规模和个人偏好

**版本**: 1.0.0  
**Agent类型**: info_collection  

**输入参数**:
- `user_message` (string): 用户描述旅行需求的输入信息 [必须]
- `conversation_history` (array): 可选的对话历史上下文 [可选] [默认: []]

**输出格式**:
- `destination` (string): 期望的目的地或'unspecified' [必须]
- `departure_date` (string): 出发日期(YYYY-MM-DD格式)或'unspecified' [必须]
- `return_date` (string): 返回日期(YYYY-MM-DD格式)或'unspecified' [必须]
- `duration_days` (integer): 旅行天数，不确定时为null [必须]
- `budget` (object): 预算信息包含amount、currency、range [必须]
- `group_size` (integer): 旅行者人数 [必须]
- `preferences` (array): 旅行偏好(如'culture', 'food', 'nature', 'shopping') [必须]
- `special_requirements` (array): 特殊需求(如'wheelchair accessible', 'vegetarian') [必须]
- `confidence` (string): 提取的置信度(high, medium, low) [必须]
- `missing_info` (array): 仍需收集的信息列表 [必须]

**使用示例**:
```json
// 请求示例
{
  "user_message": "我想去东京旅行，预算2500美元，喜欢文化和美食，3月份去",
  "conversation_history": []
}

// 响应示例
{
  "destination": "Tokyo",
  "departure_date": "2026-03-15",
  "return_date": "unspecified",
  "duration_days": null,
  "budget": {
    "amount": 2500,
    "currency": "USD",
    "range": "moderate"
  },
  "group_size": 1,
  "preferences": ["culture", "food"],
  "special_requirements": [],
  "confidence": "medium",
  "missing_info": ["travel_dates", "duration_days"]
}
```

**错误处理**: InvalidInput - 当user_message为空时抛出

---

### validate_user_input

**描述**: 验证和规范化用户旅行偏好输入数据

**版本**: 1.0.0  
**Agent类型**: info_collection  

**输入参数**:
- `user_preferences` (object): 待验证的原始用户偏好对象 [必须]

**输出格式**:
- `is_valid` (boolean): 输入是否有效 [必须]
- `validated_data` (object): 规范化和验证后的数据 [必须]
- `validation_errors` (array): 验证错误列表 [必须]
- `validation_warnings` (array): 验证警告列表 [必须]
- `suggestions` (array): 不完整或无效字段的改进建议 [必须]

**使用示例**:
```json
// 请求示例
{
  "user_preferences": {
    "destination": "Tokyo",
    "departure_date": "2024-01-15",
    "budget": {"amount": 2500, "currency": "USD", "range": "moderate"},
    "group_size": 2,
    "preferences": ["culture", "food"]
  }
}

// 响应示例
{
  "is_valid": true,
  "validated_data": {
    "destination": "Tokyo",
    "departure_date": "2024-01-15",
    "budget": {"amount": 2500, "currency": "USD", "range": "moderate"},
    "group_size": 2,
    "preferences": ["culture", "food"]
  },
  "validation_errors": [],
  "validation_warnings": [],
  "suggestions": []
}
```

**错误处理**: InvalidInput - 当user_preferences为空时抛出

---

### suggest_destinations

**描述**: 基于用户偏好和约束条件推荐热门目的地

**版本**: 1.0.0  
**Agent类型**: info_collection  

**输入参数**:
- `preferences` (array): 用户旅行偏好列表 [必须]
- `budget_range` (string): 预算范围：'budget'、'moderate'或'luxury' [可选] [默认: moderate]
- `duration_days` (integer): 首选旅行天数 [可选]
- `season` (string): 首选旅行季节 [可选] [默认: any]
- `max_suggestions` (integer): 返回的最大建议数量 [可选] [默认: 5]

**输出格式**:
- `suggestions` (array): 目的地建议列表 [必须]
  - `destination` (string): 目的地名称
  - `country` (string): 国家名称
  - `match_score` (number): 匹配分数
  - `matched_preferences` (array): 匹配的偏好
  - `short_description` (string): 简短描述
  - `estimated_budget` (string): 预估预算
  - `best_season` (string): 最佳旅行季节
  - `highlights` (array): 亮点特色
- `total_matches` (integer): 总匹配数量 [必须]

**使用示例**:
```json
// 请求示例
{
  "preferences": ["culture", "food"],
  "budget_range": "moderate",
  "duration_days": 5,
  "season": "spring",
  "max_suggestions": 3
}

// 响应示例
{
  "suggestions": [
    {
      "destination": "Tokyo",
      "country": "Japan",
      "match_score": 0.9,
      "matched_preferences": ["culture", "food"],
      "short_description": "传统与现代的完美融合",
      "estimated_budget": "$2000-3500",
      "best_season": "spring",
      "highlights": ["寺庙", "寿司", "科技", "樱花"]
    }
  ],
  "total_matches": 1
}
```

**错误处理**: InvalidInput - 当preferences为空时抛出
