# Booking Agent Skills

**版本**: 1.0.0  
**Agent类型**: booking  
**描述**: 预订代理负责处理完整的预订流程，包括创建预订、处理支付、确认预订和查询预订状态

---

## Skills

### create_booking

**描述**: 为选定的旅行选项创建新的预订订单

**版本**: 1.0.0  
**Agent类型**: booking  

**输入参数**:
- `customer_info` (object): 客户信息 [必须]
  - `name` (string): 姓名 [必须]
  - `email` (string): 邮箱 [必须]
  - `phone` (string): 电话 [可选]
- `trip_details` (object): 旅行详情 [必须]
  - `destination` (string): 目的地 [必须]
  - `departure_date` (string): 出发日期 [必须]
  - `return_date` (string): 返回日期 [可选]
  - `travelers` (integer): 旅行人数 [必须]
- `selected_flight` (object): 选定的航班详情 [可选]
- `selected_hotel` (object): 选定的酒店详情 [可选]
- `additional_services` (array): 附加服务(保险、游览等) [可选] [默认: []]

**输出格式**:
- `booking_id` (string): 预订ID [必须]
- `status` (string): 状态 [必须]
- `created_at` (string): 创建时间 [必须]
- `expires_at` (string): 过期时间 [必须]
- `customer_info` (object): 客户信息 [必须]
- `trip_summary` (object): 旅行摘要 [必须]
- `price_breakdown` (object): 价格明细 [必须]
  - `flights_total` (number): 航班总计
  - `hotels_total` (number): 酒店总计
  - `services_total` (number): 服务总计
  - `subtotal` (number): 小计
  - `taxes_and_fees` (number): 税费
  - `total` (number): 总计
  - `currency` (string): 货币
- `payment_required` (boolean): 是否需要支付 [必须]
- `next_steps` (array): 下一步操作 [必须]

**使用示例**:
```json
// 请求示例
{
  "customer_info": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "+86 138 0000 0000"
  },
  "trip_details": {
    "destination": "Tokyo",
    "departure_date": "2026-03-15",
    "return_date": "2026-03-22",
    "travelers": 2
  },
  "selected_flight": {
    "flight_id": "FL-SA-001",
    "total_price": 2400.00
  },
  "selected_hotel": {
    "hotel_id": "HTL-001",
    "total_price": 1250.00
  }
}

// 响应示例
{
  "booking_id": "BKG-20250110-ABC123",
  "status": "pending_payment",
  "created_at": "2025-01-10T10:30:00",
  "expires_at": "2025-01-11T10:30:00",
  "customer_info": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "+86 138 0000 0000"
  },
  "trip_summary": {
    "destination": "Tokyo",
    "departure_date": "2026-03-15",
    "return_date": "2026-03-22",
    "travelers": 2,
    "flight_included": true,
    "hotel_included": true,
    "additional_services_count": 0
  },
  "price_breakdown": {
    "flights_total": 2400.00,
    "hotels_total": 1250.00,
    "services_total": 0,
    "subtotal": 3650.00,
    "taxes_and_fees": 438.00,
    "total": 4088.00,
    "currency": "USD"
  },
  "payment_required": true,
  "next_steps": [
    "仔细检查预订详情",
    "进行支付以确认预订",
    "在2025-01-11 10:30前完成支付，否则预订将被释放",
    "支付后您将收到确认邮件"
  ]
}
```

**错误处理**: InvalidInput - 当customer_info或trip_details为空时抛出

---

### process_payment

**描述**: 处理预订的支付包括验证、授权和交易确认

**版本**: 1.0.0  
**Agent类型**: booking  

**输入参数**:
- `booking_id` (string): 要处理支付的预订ID [必须]
- `payment_method` (string): 支付方式 [必须] (enum: ["credit_card", "debit_card", "paypal", "bank_transfer"])
- `payment_details` (object): 支付详情(卡号等) [可选]
  - `cardholder_name` (string): 持卡人姓名
  - `card_number` (string): 卡号
  - `expiry_date` (string): 到期日期
  - `cvv` (string): CVV
  - `billing_address` (object): 账单地址
- `amount` (number): 要收取的金额 [必须]
- `currency` (string): 货币代码 [可选] [默认: USD]

**输出格式**:
- `payment_status` (string): 支付状态 [必须] (enum: ["success", "failed", "pending", "requires_action"])
- `transaction_id` (string): 交易ID [必须]
- `booking_id` (string): 预订ID [必须]
- `amount_charged` (number): 收取的金额 [必须]
- `currency` (string): 货币 [必须]
- `payment_method` (string): 支付方式 [必须]
- `processed_at` (string): 处理时间 [必须]
- `receipt` (object): 收据 [可选]
  - `receipt_number` (string): 收据号
  - `receipt_url` (string): 收据链接
- `message` (string): 消息 [必须]
- `next_steps` (array): 下一步操作 [必须]

**使用示例**:
```json
// 请求示例
{
  "booking_id": "BKG-20250110-ABC123",
  "payment_method": "credit_card",
  "payment_details": {
    "cardholder_name": "张三",
    "card_number": "**** **** **** 1234",
    "expiry_date": "12/25",
    "cvv": "***"
  },
  "amount": 4088.00,
  "currency": "USD"
}

// 响应示例
{
  "payment_status": "success",
  "transaction_id": "TXN-20250110-123456",
  "booking_id": "BKG-20250110-ABC123",
  "amount_charged": 4088.00,
  "currency": "USD",
  "payment_method": "credit_card",
  "processed_at": "2025-01-10T10:35:00",
  "receipt": {
    "receipt_number": "RCP-123456",
    "receipt_url": "https://bookings.example.com/receipts/RCP-123456"
  },
  "message": "支付处理成功！",
  "next_steps": [
    "预订现已确认",
    "确认邮件已发送到注册邮箱",
    "从上述链接下载收据",
    "随时使用预订ID查询预订状态"
  ]
}
```

**错误处理**: InvalidInput - 当booking_id、payment_method或amount为空时抛出

---

### confirm_booking

**描述**: 在成功支付后确认预订并生成确认详情

**版本**: 1.0.0  
**Agent类型**: booking  

**输入参数**:
- `booking_id` (string): 要确认的预订ID [必须]
- `transaction_id` (string): 支付交易ID [必须]
- `customer_email` (string): 发送确认邮件的邮箱 [可选]

**输出格式**:
- `confirmation_status` (string): 确认状态 [必须] (enum: ["confirmed", "failed", "pending"])
- `booking_id` (string): 预订ID [必须]
- `confirmation_number` (string): 确认号 [必须]
- `confirmed_at` (string): 确认时间 [必须]
- `booking_details` (object): 预订详情 [必须]
  - `destination` (string): 目的地
  - `dates` (string): 日期
  - `travelers` (integer): 旅行人数
  - `total_paid` (number): 已付金额
- `confirmation_email_sent` (boolean): 确认邮件是否已发送 [必须]
- `documents` (object): 文档 [必须]
  - `eticket_url` (string): 电子票链接
  - `hotel_voucher_url` (string): 酒店凭证链接
  - `itinerary_url` (string): 行程链接
- `important_info` (array): 重要信息 [必须]
- `next_steps` (array): 下一步操作 [必须]

**使用示例**:
```json
// 请求示例
{
  "booking_id": "BKG-20250110-ABC123",
  "transaction_id": "TXN-20250110-123456",
  "customer_email": "zhangsan@example.com"
}

// 响应示例
{
  "confirmation_status": "confirmed",
  "booking_id": "BKG-20250110-ABC123",
  "confirmation_number": "CONF-ABC123",
  "confirmed_at": "2025-01-10T10:36:00",
  "booking_details": {
    "destination": "Tokyo, Japan",
    "dates": "2026-03-15 to 2026-03-22",
    "travelers": 2,
    "total_paid": 4088.00
  },
  "confirmation_email_sent": true,
  "documents": {
    "eticket_url": "https://bookings.example.com/documents/eticket/BKG-20250110-ABC123.pdf",
    "hotel_voucher_url": "https://bookings.example.com/documents/voucher/BKG-20250110-ABC123.pdf",
    "itinerary_url": "https://bookings.example.com/documents/itinerary/BKG-20250110-ABC123.pdf"
  },
  "important_info": [
    "国际航班请在起飞前3小时到达机场",
    "国际旅行需要有效护照",
    "酒店入住时间：下午3:00，退房：上午11:00",
    "保留确认号以便查询",
    "下载并打印所有旅行文档"
  ],
  "next_steps": [
    "下载并保存您的旅行文档",
    "检查护照有效期（必须超过旅行日期6个月）",
    "查看目的地的签证要求",
    "如尚未购买，考虑旅行保险",
    "查看航空公司行李政策",
    "将行程添加到您的日历",
    "起飞前24小时在线办理登机手续"
  ]
}
```

**错误处理**: InvalidInput - 当booking_id或transaction_id为空时抛出

---

### get_booking_status

**描述**: 使用预订ID或确认号查询现有预订的当前状态

**版本**: 1.0.0  
**Agent类型**: booking  

**输入参数**:
- `booking_id` (string): 预订ID或确认号 [必须]
- `customer_email` (string): 用于验证的客户邮箱 [可选]
- `include_details` (boolean): 是否包含完整预订详情 [可选] [默认: true]

**输出格式**:
- `booking_id` (string): 预订ID [必须]
- `status` (string): 状态 [必须] (enum: ["confirmed", "pending_payment", "cancelled", "completed", "in_progress"])
- `booking_date` (string): 预订日期 [必须]
- `last_updated` (string): 最后更新时间 [必须]
- `customer_info` (object): 客户信息 [必须]
  - `name` (string): 姓名
  - `email` (string): 邮箱
- `trip_details` (object): 旅行详情 [必须]
  - `destination` (string): 目的地
  - `departure_date` (string): 出发日期
  - `return_date` (string): 返回日期
  - `travelers` (integer): 旅行人数
  - `days_until_trip` (integer): 距离旅行的天数
- `payment_info` (object): 支付信息 [必须]
  - `amount_paid` (number): 已付金额
  - `currency` (string): 货币
  - `payment_status` (string): 支付状态
  - `transaction_id` (string): 交易ID
- `flight_details` (object): 航班详情 [可选]
- `hotel_details` (object): 酒店详情 [可选]
- `updates` (array): 更新列表 [必须]
  - `timestamp` (string): 时间戳
  - `type` (string): 类型
  - `message` (string): 消息
- `available_actions` (array): 可用操作 [必须]

**使用示例**:
```json
// 请求示例
{
  "booking_id": "BKG-20250110-ABC123",
  "customer_email": "zhangsan@example.com",
  "include_details": true
}

// 响应示例
{
  "booking_id": "BKG-20250110-ABC123",
  "status": "confirmed",
  "booking_date": "2025-01-05T10:30:00",
  "last_updated": "2025-01-10T10:36:00",
  "customer_info": {
    "name": "张三",
    "email": "zhangsan@example.com"
  },
  "trip_details": {
    "destination": "Tokyo, Japan",
    "departure_date": "2026-03-15",
    "return_date": "2026-03-22",
    "travelers": 2,
    "days_until_trip": 30
  },
  "payment_info": {
    "amount_paid": 4088.00,
    "currency": "USD",
    "payment_status": "completed",
    "transaction_id": "TXN-20250110-123456"
  },
  "flight_details": {
    "outbound": {
      "airline": "SkyAir",
      "flight_number": "SA101",
      "departure": "10:00 AM",
      "arrival": "2:30 PM",
      "date": "2026-03-15"
    },
    "return": {
      "airline": "SkyAir",
      "flight_number": "SA202",
      "departure": "3:00 PM",
      "arrival": "9:30 PM",
      "date": "2026-03-22"
    }
  },
  "hotel_details": {
    "name": "Grand Plaza Hotel",
    "check_in": "2026-03-15",
    "check_out": "2026-03-22",
    "room_type": "Deluxe King Room",
    "nights": 7
  },
  "updates": [
    {
      "timestamp": "2025-01-05T10:30:00",
      "type": "booking_created",
      "message": "预订创建成功"
    },
    {
      "timestamp": "2025-01-10T10:35:00",
      "type": "payment_received",
      "message": "支付处理成功"
    },
    {
      "timestamp": "2025-01-10T10:36:00",
      "type": "booking_confirmed",
      "message": "预订已确认 - 确认邮件已发送"
    }
  ],
  "available_actions": [
    "modify_booking",
    "cancel_booking",
    "add_services"
  ]
}
```

**错误处理**: InvalidInput - 当booking_id为空时抛出
