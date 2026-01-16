# Agent Skills Registry

## 概述
所有 skills 的元数据索引。LLM prompt 中只包含名称和描述，实现代码按需加载。

## 可用 Skills

### 1. search (搜索技能)
根据用户需求搜索旅游目的地、酒店、航班等
- **输入**: {query: string, filters?: object}
- **输出**: {results: array, total: number}
- **成本**: $0.05/call

### 2. recommend (推荐技能)
生成个性化旅游推荐方案
- **输入**: {user_prefs: object, search_results: array}
- **输出**: {recommendations: array, confidence: number}
- **成本**: $0.08/call

### 3. booking (预订技能)
创建和管理旅游预订
- **输入**: {booking_details: object}
- **输出**: {booking_id: string, status: string}
- **成本**: $0.03/call

### 4. info_collection (信息收集技能)
与用户交互收集旅游需求
- **输入**: {user_message: string}
- **输出**: {collected_info: object}
- **成本**: $0.02/call
