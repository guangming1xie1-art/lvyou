# Skill: info_collection

## 概述
与用户交互收集旅游需求信息。智能提取目的地、日期、预算、偏好等关键信息，并识别缺失字段。

## 参数

### 输入参数
- `user_message` (string, required): 用户消息
- `context` (object, optional): 上下文信息
  - `conversation_history` (array): 对话历史
  - `previous_collected_info` (object): 之前收集到的信息

## 返回值

```json
{
  "collected_info": {
    "destination": "巴黎",
    "dates": {
      "departure": "2024-06-01",
      "return": "2024-06-05"
    },
    "budget": {
      "min": 10000,
      "max": 15000,
      "currency": "CNY"
    },
    "travelers_count": 2,
    "preferences": ["culture", "food", "shopping"],
    "accommodation_type": "hotel",
    "special_requirements": ["无障碍设施", "早餐包含"]
  },
  "missing_fields": [
    {
      "field": "travelers_details",
      "description": "需要提供旅客的详细信息（姓名、证件号）",
      "required_for": "booking"
    }
  ],
  "confidence": 0.85,
  "suggestions": [
    "建议考虑购买旅游保险",
    "6月是巴黎旅游旺季，建议提前预订"
  ],
  "metadata": {
    "extraction_method": "llm",
    "execution_time_ms": 200
  }
}
```

## 使用示例

### 基本信息收集
```python
from src.skills.info_collection import InfoCollectionSkill

skill = InfoCollectionSkill()
result = await skill.execute({
    "user_message": "我想6月初去巴黎玩5天，预算1-1.5万，两个人，喜欢文化和美食"
})
```

### 带上下文的信息收集
```python
result = await skill.execute({
    "user_message": "改成从6月1号出发吧",
    "context": {
        "previous_collected_info": {
            "destination": "巴黎",
            "duration": 5,
            "travelers_count": 2
        }
    }
})
# 结果会合并之前的信息，只更新日期
```

### 多轮对话收集
```python
# 第一轮
result1 = await skill.execute({
    "user_message": "我想去法国旅游"
})
# collected_info: {"destination": "法国"}
# missing_fields: ["dates", "budget", "travelers_count", ...]

# 第二轮
result2 = await skill.execute({
    "user_message": "6月去，两个人，预算1万5",
    "context": {
        "previous_collected_info": result1["collected_info"]
    }
})
# collected_info: {"destination": "法国", "dates": {...}, "budget": {...}, "travelers_count": 2}
```

## 成本与性能

- **平均执行时间**: 200ms
- **Token 成本估计**: $0.02 per call
- **模型**: deepseek-chat（便宜层）
- **缓存策略**: 对话上下文缓存在 session 中

## 信息提取逻辑

### 目的地识别
- 国家名、城市名、景点名
- 处理模糊表达（"海边"、"欧洲"等）

### 日期解析
- 绝对日期："6月1号"、"2024-06-01"
- 相对日期："下个月"、"明年春节"
- 持续时间："5天"、"一周"

### 预算提取
- 总预算："1万"、"$2000"
- 每日预算："每天300"
- 范围："1-2万"

### 偏好识别
- 关键词匹配：海滩、文化、美食、冒险、购物、自然、历史
- 情感分析：喜欢/不喜欢

### 特殊需求
- 无障碍设施
- 饮食限制（素食、清真等）
- 语言偏好

## 依赖

- LLM（deepseek-chat）用于信息提取
- NER（命名实体识别）用于目的地识别
- 日期解析库（dateparser）

## 错误处理

### 常见错误
- `INVALID_MESSAGE`: 消息为空或格式不正确
- `EXTRACTION_FAILED`: 无法提取任何有效信息
- `AMBIGUOUS_INPUT`: 输入模糊不清

### 降级策略
如果 LLM 提取失败，使用规则引擎进行基础提取。

## 版本历史

- **v1.0.0** (2024-01): 初始版本，支持基本信息提取和缺失字段识别
