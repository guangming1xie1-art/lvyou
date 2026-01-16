# Skill: booking

## 概述
创建旅游预订、获取预订状态。支持酒店、航班、景点门票等多种预订类型。

## 参数

### 创建预订
- `booking_details` (object, required): 预订详情
  - `type` (string): 预订类型 `"hotel" | "flight" | "package" | "activity"`
  - `destination` (string): 目的地
  - `dates` (object): 日期信息
    - `check_in` (string): 入住日期（酒店）
    - `check_out` (string): 退房日期（酒店）
    - `departure` (string): 出发日期（航班）
    - `return` (string): 返回日期（航班）
  - `travelers` (array): 旅客信息
    - `name` (string): 姓名
    - `age` (integer): 年龄
    - `document_type` (string): 证件类型
    - `document_number` (string): 证件号码
  - `contact` (object): 联系信息
    - `email` (string)
    - `phone` (string)
  - `payment` (object): 支付信息
    - `method` (string): 支付方式
    - `amount` (number): 金额

### 查询预订状态
- `booking_id` (string, required): 预订 ID

## 返回值

### 创建预订响应
```json
{
  "booking_id": "BK20240601001",
  "status": "confirmed",
  "details": {
    "type": "hotel",
    "destination": "巴黎",
    "hotel": {
      "name": "巴黎大酒店",
      "address": "1 Rue Example, Paris",
      "check_in": "2024-06-01",
      "check_out": "2024-06-05",
      "room_type": "Deluxe Double",
      "nights": 4
    },
    "travelers": [
      {
        "name": "张三",
        "age": 30
      }
    ],
    "total_cost": {
      "amount": 5000,
      "currency": "CNY",
      "breakdown": {
        "room": 4000,
        "tax": 500,
        "service_fee": 500
      }
    }
  },
  "payment": {
    "status": "completed",
    "method": "credit_card",
    "transaction_id": "TXN123456"
  },
  "confirmation": {
    "number": "CONF789012",
    "qr_code": "https://example.com/qr/CONF789012"
  },
  "cancellation_policy": {
    "refundable": true,
    "free_cancellation_until": "2024-05-25",
    "penalty_after": "50% of total"
  }
}
```

### 查询状态响应
```json
{
  "booking_id": "BK20240601001",
  "status": "confirmed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "timeline": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "event": "booking_created",
      "description": "预订已创建"
    },
    {
      "timestamp": "2024-01-15T10:35:00Z",
      "event": "payment_confirmed",
      "description": "支付已确认"
    }
  ]
}
```

## 使用示例

### 创建酒店预订
```python
from src.skills.booking import BookingSkill

skill = BookingSkill()
result = await skill.execute({
    "booking_details": {
        "type": "hotel",
        "destination": "Paris",
        "dates": {
            "check_in": "2024-06-01",
            "check_out": "2024-06-05"
        },
        "travelers": [
            {
                "name": "Zhang San",
                "age": 30,
                "document_type": "passport",
                "document_number": "P123456"
            }
        ],
        "contact": {
            "email": "zhangsan@example.com",
            "phone": "+86 138 0000 0000"
        },
        "payment": {
            "method": "credit_card",
            "amount": 5000
        }
    }
})
```

### 查询预订状态
```python
result = await skill.execute({
    "booking_id": "BK20240601001"
})
```

## 成本与性能

- **平均执行时间**: 300ms
- **Token 成本估计**: $0.03 per call
- **API 调用成本**: 取决于后端 Java API
- **缓存策略**: 预订状态缓存 30 分钟

## 预订流程

1. **验证输入**: 检查必填字段和数据格式
2. **可用性检查**: 调用 Java API 检查可用性
3. **创建预订**: 生成预订 ID 并锁定资源
4. **处理支付**: 调用支付网关
5. **发送确认**: 发送确认邮件和短信
6. **返回结果**: 返回预订详情

## 依赖

- Java API 后端 `/bookings/create` 和 `/bookings/{id}/status` 接口
- 支付网关集成
- 邮件/短信服务

## 错误处理

### 常见错误
- `INVALID_BOOKING_DETAILS`: 预订详情格式不正确
- `NOT_AVAILABLE`: 所选资源不可用
- `PAYMENT_FAILED`: 支付失败
- `BOOKING_NOT_FOUND`: 预订 ID 不存在

### 降级策略
如果 Java API 不可用，返回 mock 预订 ID 并标记为待确认。

## 版本历史

- **v1.0.0** (2024-01): 初始版本，支持酒店和航班预订
