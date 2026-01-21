# 三层架构实现文档

## 概述

本文档描述了旅游助手系统的完整三层架构实现，将 Phase 1.2（多模型接口）、Phase 1.3（LangGraph工作流）、Phase 1.4（DeepAgent子智能体）合并为一个统一的核心架构。

---

## 架构层次

### 第一层：多模型统一接口 (Phase 1.2)

**模块路径：** `src/llm/`

**功能：** 提供标准化的 LLM 访问接口，支持多模型切换和成本优化

#### 文件结构

```
src/llm/
├── __init__.py          # 模块初始化，导出主要类
├── models.py            # 模型配置数据类
├── factory.py           # LLM 工厂类
└── base.py             # 基础模块
```

#### 核心类

##### 1. ModelProvider (枚举)

定义支持的 LLM 提供商：

```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    GLM = "glm"
```

##### 2. ModelConfig (数据类)

模型配置信息：

```python
class ModelConfig(BaseModel):
    name: str                              # 模型名称
    provider: ModelProvider                # 服务商
    model_id: str                         # 模型ID
    base_url: str                         # API基础URL
    api_key_env: str                      # API KEY环境变量名
    max_tokens: int = 4096
    temperature: float = 0.7
    input_cost: float                     # 输入成本（$/1M tokens）
    output_cost: float                    # 输出成本
    cache_read_cost: Optional[float]      # 缓存读取成本
```

##### 3. MODELS (字典)

预置的模型配置：

- **GPT 系列：** gpt-4, gpt-4-turbo
- **Claude 系列：** claude-3.5-sonnet, claude-3-opus
- **Qwen：** qwen-max
- **DeepSeek：** deepseek-v3
- **GLM：** glm-4

##### 4. LLMFactory (工厂类)

主要方法：

```python
class LLMFactory:
    @classmethod
    def create_model(name: Optional[str] = None, **kwargs) -> Any:
        """创建 LLM 实例"""

    @classmethod
    def list_available_models() -> List[str]:
        """列出所有可用模型"""

    @classmethod
    def get_model_config(name: str) -> ModelConfig:
        """获取模型配置"""

    @classmethod
    def get_model_cost(name: str, input_tokens: int, output_tokens: int) -> float:
        """计算模型使用成本"""
```

#### 使用示例

```python
from llm import LLMFactory

# 创建模型实例
llm = LLMFactory.create_model("gpt-4")

# 列出可用模型
models = LLMFactory.list_available_models()

# 计算成本
cost = LLMFactory.get_model_cost("gpt-4", 1000, 500)
```

---

### 第二层：LangGraph 工作流 (Phase 1.3)

**模块路径：** `src/workflows/conversation/`

**功能：** 提供对话流程编排功能，使用 LangGraph 构建状态机

#### 文件结构

```
src/workflows/conversation/
├── __init__.py          # 模块初始化
├── conversation.py      # 主工作流文件
├── state.py            # 状态定义
└── nodes/              # 工作流节点
    ├── __init__.py
    ├── entry.py        # 入口节点
    ├── router.py       # 路由节点
    ├── search.py       # 搜索节点
    ├── recommend.py    # 推荐节点
    ├── booking.py      # 预订节点
    └── response.py     # 响应节点
```

#### 核心类

##### 1. ConversationState (TypedDict)

工作流状态定义：

```python
class ConversationState(TypedDict, total=False):
    user_message: str
    conversation_history: List[Dict]
    messages: List[Any]
    intent: str                        # search/recommend/book/general
    user_requirements: Dict
    search_query: Optional[str]
    search_results: Optional[List[Dict]]
    search_executed: bool
    recommend_parameters: Optional[Dict]
    recommendations: Optional[List[Dict]]
    recommend_executed: bool
    booking_details: Optional[Dict]
    booking_confirmed: bool
    booking_result: Optional[Dict]
    response: str
    workflow_status: str               # active/completed/failed
    error_message: Optional[str]
    cost_tokens: Dict
```

##### 2. ConversationWorkflow (类)

对话工作流主类：

```python
class ConversationWorkflow:
    def __init__(self):
        """初始化对话工作流"""

    async def invoke(self, user_message: str) -> ConversationState:
        """执行对话工作流"""

    async def stream(self, user_message: str):
        """流式执行对话工作流"""
```

#### 工作流节点

| 节点 | 函数 | 功能 |
|------|------|------|
| 入口 | `process_entry` | 验证输入，初始化对话上下文 |
| 路由 | `route_intent`, `should_route` | 识别用户意图，路由到相应流程 |
| 搜索规划 | `plan_search` | 规划搜索任务 |
| 搜索执行 | `execute_search` | 执行搜索 |
| 推荐规划 | `plan_recommend` | 规划推荐任务 |
| 推荐执行 | `execute_recommend` | 执行推荐 |
| 预订规划 | `plan_booking` | 规划预订任务 |
| 预订执行 | `execute_booking` | 执行预订 |
| 响应 | `generate_response` | 生成最终回复 |

#### 工作流流程

```
┌─────────┐
│  Entry  │
└────┬────┘
     │
     ▼
┌─────────────────┐
│  Intent Router │
└────┬────┬──────┘
     │    │
     ├────┴──┐
     ▼       ▼       ▼
  Search  Recommend  Booking
     │       │       │
     ▼       ▼       ▼
  ┌───────────────┐
  │   Response    │
  └───────────────┘
```

#### 使用示例

```python
from workflows.conversation import ConversationWorkflow

# 创建工作流
workflow = ConversationWorkflow()

# 执行工作流
result = await workflow.invoke("搜索北京的景点")

# 获取回复
print(result["response"])
```

---

### 第三层：DeepAgent 子智能体 (Phase 1.4)

**模块路径：** `src/agents/subagents/`

**功能：** 提供专业的子智能体实现，支持旅游领域的特定任务

#### 文件结构

```
src/agents/subagents/
├── __init__.py          # 模块初始化
├── base.py             # 子智能体基类
├── search_agent.py     # 搜索智能体
├── recommend_agent.py  # 推荐智能体
├── booking_agent.py     # 预订智能体
└── tools/              # 工具模块
    ├── __init__.py
    ├── search_tools.py    # 搜索工具
    ├── recommend_tools.py # 推荐工具
    └── booking_tools.py   # 预订工具
```

#### 核心类

##### 1. BaseAgent (抽象基类)

所有子智能体的基类：

```python
class BaseAgent(ABC):
    name: str
    description: str
    tools: List[Any]

    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        """执行智能体"""

    @abstractmethod
    async def stream(self, input_data: Dict):
        """流式执行"""
```

##### 2. SearchAgent (搜索智能体)

搜索航班、酒店、景点：

```python
class SearchAgent(BaseAgent):
    async def execute(self, input_data: Dict) -> Dict:
        """执行搜索任务"""

    async def stream(self, input_data: Dict):
        """流式执行搜索"""
```

##### 3. RecommendationAgent (推荐智能体)

生成行程规划、预算建议、特色体验：

```python
class RecommendationAgent(BaseAgent):
    async def execute(self, input_data: Dict) -> Dict:
        """执行推荐任务"""

    async def stream(self, input_data: Dict):
        """流式执行推荐"""
```

##### 4. BookingAgent (预订智能体)

预订航班、酒店、门票：

```python
class BookingAgent(BaseAgent):
    async def execute(self, input_data: Dict) -> Dict:
        """执行预订任务"""

    async def stream(self, input_data: Dict):
        """流式执行预订"""
```

#### 工具列表

##### 搜索工具

```python
@tool
async def search_flights(destination: str, departure_date: str) -> List[Dict]:
    """搜索航班信息"""

@tool
async def search_hotels(destination: str, check_in: str, check_out: str) -> List[Dict]:
    """搜索酒店信息"""

@tool
async def search_attractions(destination: str) -> List[Dict]:
    """搜索景点信息"""
```

##### 推荐工具

```python
@tool
async def generate_itinerary(destination: str, duration_days: int, preferences: Dict) -> Dict:
    """生成旅游行程规划"""

@tool
async def calculate_budget(destination: str, duration_days: int, budget: float) -> Dict:
    """计算旅游预算"""

@tool
async def recommend_experiences(destination: str, interests: List[str]) -> List[Dict]:
    """推荐特色体验"""
```

##### 预订工具

```python
@tool
async def book_flight(destination: str, departure_date: str, passengers: int) -> Dict:
    """预订航班"""

@tool
async def book_hotel(destination: str, check_in: str, check_out: str, rooms: int) -> Dict:
    """预订酒店"""

@tool
async def book_ticket(attraction: str, visit_date: str, visitors: int) -> Dict:
    """预订景点门票"""
```

#### 使用示例

```python
from agents.subagents import SearchAgent, RecommendationAgent, BookingAgent

# 创建智能体
search_agent = SearchAgent(llm=None)
recommend_agent = RecommendationAgent(llm=None)
booking_agent = BookingAgent(llm=None)

# 执行搜索
search_result = await search_agent.execute({
    "user_requirements": {"destination": "北京"},
    "user_message": "搜索北京的景点"
})

# 执行推荐
recommend_result = await recommend_agent.execute({
    "user_requirements": {"destination": "北京", "duration_days": 5},
    "search_results": search_result["search_results"]
})

# 执行预订
booking_result = await booking_agent.execute({
    "booking_details": {"destination": "北京", "travel_date": "2024-06-01"},
    "recommendations": recommend_result["recommendations"]
})
```

---

## 集成使用

### 完整流程示例

```python
from llm import LLMFactory
from workflows.conversation import ConversationWorkflow
from agents.subagents import SearchAgent, RecommendationAgent, BookingAgent

# 第一层：创建 LLM 实例
llm = LLMFactory.create_model("gpt-4")

# 第二层：创建工作流
workflow = ConversationWorkflow()

# 第三层：创建子智能体
search_agent = SearchAgent(llm=llm)
recommend_agent = RecommendationAgent(llm=llm)
booking_agent = BookingAgent(llm=llm)

# 执行完整流程
user_message = "我想去北京旅游5天"

# 1. 通过工作流处理
result = await workflow.invoke(user_message)

# 2. 获取响应
response = result["response"]
print(response)
```

### API 集成示例

```python
from fastapi import APIRouter, HTTPException
from workflows.conversation import ConversationWorkflow

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 创建工作流实例
workflow = ConversationWorkflow()

@router.post("/message")
async def handle_message(request: dict):
    """处理用户消息"""

    user_message = request.get("message")

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    # 执行工作流
    result = await workflow.invoke(user_message)

    return {
        "response": result["response"],
        "status": result["workflow_status"],
        "intent": result["intent"],
        "error": result.get("error_message"),
        "cost_tokens": result["cost_tokens"]
    }
```

---

## 配置说明

### 环境变量

在 `.env` 文件中配置以下变量：

```bash
# LLM API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
DASHSCOPE_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx
ZHIPU_API_KEY=xxx

# 多模型配置
LLM_DEFAULT_MODEL=gpt-4
LLM_MONTHLY_BUDGET=1000
LLM_DAILY_BUDGET=50
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

### 模型选择策略

根据任务复杂度选择合适的模型层级：

| 层级 | 推荐模型 | 用途 | 成本 |
|------|----------|------|------|
| Cheap | DeepSeek Chat | 简单任务（信息收集、验证） | ¥0.0014/1k tokens |
| Standard | Qwen Turbo | 中等复杂任务（搜索、推荐） | ¥0.008/1k tokens |
| Power | Claude 3.5 | 复杂推理任务（深度规划） | $3/1M tokens |

---

## 验证清单

- [x] **Phase 1.2：多模型统一接口**
  - [x] ModelProvider 枚举定义完整
  - [x] ModelConfig 数据类定义完整
  - [x] MODELS 字典包含所有预置模型
  - [x] LLMFactory 实现所有方法
  - [x] 支持多模型切换
  - [x] 成本计算功能完整

- [x] **Phase 1.3：LangGraph 工作流**
  - [x] ConversationState 定义完整
  - [x] ConversationWorkflow 类实现完整
  - [x] 所有节点实现完整
  - [x] 路由逻辑正确
  - [x] 支持异步执行
  - [x] 支持流式执行

- [x] **Phase 1.4：DeepAgent 子智能体**
  - [x] BaseAgent 基类定义完整
  - [x] SearchAgent 实现完整
  - [x] RecommendationAgent 实现完整
  - [x] BookingAgent 实现完整
  - [x] 所有工具实现完整
  - [x] 支持异步执行
  - [x] 支持流式执行

- [x] **集成验证**
  - [x] 文件结构完整
  - [x] 模块导入正常
  - [x] 三层架构可以独立使用
  - [x] 三层架构可以集成使用
  - [x] 配置文件更新完成

---

## 运行验证

### 验证文件结构

```bash
python verify_architecture.py
```

预期输出：

```
================================================================================
验证结果: 53/53 通过
✓ 所有检查通过！三层架构实现完整。
================================================================================
```

### 运行完整测试

```bash
python test_architecture_integration.py
```

---

## 总结

本实现成功地将三个独立的 Phase 合并为一个统一的三层架构：

1. **第一层（LLM 接口层）**：提供标准化的 LLM 访问接口，支持多模型无缝切换
2. **第二层（工作流编排层）**：使用 LangGraph 实现对话流程的状态管理
3. **第三层（智能体执行层）**：提供专业的子智能体，执行具体任务

各层之间通过清晰的接口进行通信，实现了高内聚、低耦合的架构设计。同时保留了足够的灵活性，可以根据需要替换或扩展各层的实现。
