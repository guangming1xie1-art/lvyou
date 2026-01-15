# LLM 统一接口重构 - 架构改造文档

## 概述

本文档描述了 travel-assistant-agent 从**单一 Claude 依赖**到**统一 ChatOpenAI 接口 + LLMFactory 工厂模式**的架构改造。

## 改造背景

### 原有架构问题

1. **单一依赖**: 仅支持 Anthropic Claude，缺少模型选择的灵活性
2. **成本高昂**: Claude 3.5 Sonnet 成本约为 $3/M tokens，长期运行成本高
3. **扩展困难**: 新增模型需要修改多处代码
4. **缺乏分层**: 所有任务使用同一模型，无法进行成本优化

### 改造目标

1. ✅ 统一接口 - 所有模型通过 ChatOpenAI 兼容接口访问
2. ✅ 分层调用 - 便宜/标准/强力三层模型架构
3. ✅ 配置驱动 - 环境变量控制模型选择
4. ✅ 成本优化 - 预计成本降低 90%+

## 新架构

### 分层模型设计

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application)                       │
├─────────────────────────────────────────────────────────────┤
│                    工作流层 (Workflow)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ info_agent  │  │  search_deep │  │  booking_agent      │  │
│  │ (cheap_llm) │  │    agent     │  │   (cheap_llm)       │  │
│  └─────────────┘  │(standard_llm)│  └─────────────────────┘  │
│                   └─────────────┘                            │
├─────────────────────────────────────────────────────────────┤
│                    工厂层 (LLMFactory)                        │
│                                                             │
│  create_llm(provider, tier, **kwargs) → ChatOpenAI         │
│  get_default_llm(tier) → ChatOpenAI                        │
│  is_provider_available(provider) → bool                    │
│  get_cost_estimate(provider, input_tokens, output_tokens)   │
├─────────────────────────────────────────────────────────────┤
│                    配置层 (Configuration)                     │
│                                                             │
│  ModelTier (CHEAP/STANDARD/POWER)                          │
│  LLMProvider (DEEPSEEK/DASHSCOPE/ZHIPU/OPENAI/ANTHROPIC)  │
│  MODEL_CONFIGS (9+ 模型配置)                                │
└─────────────────────────────────────────────────────────────┘
```

### 模型层级

| 层级 | 用途 | 模型示例 | 成本 |
|------|------|----------|------|
| **CHEAP** | 简单任务（信息提取、格式化） | DeepSeek Chat, Qwen Plus, GPT-4o mini | ~$0.0002-0.15/1M |
| **STANDARD** | 中等复杂（搜索、推荐） | Qwen Turbo, GLM-4, GPT-4o | ~$0.008-5/1M |
| **POWER** | 复杂推理（深度分析、决策） | Claude 3.5, Qwen Max, DeepSeek Reasoner | ~$0.0028-3/1M |

### 成本对比

| 方案 | 月成本估算 | 相对节省 |
|------|------------|----------|
| 原方案 (Claude Only) | $600 | - |
| 新方案 (DeepSeek 主力) | ~$7 | **99%** |
| 新方案 (混合分层) | ~$15-30 | **95-97%** |

## 核心组件

### 1. LLMFactory (`src/config/llm_config.py`)

```python
from config.llm_config import LLMFactory, ModelTier

# 创建指定层级的 LLM
cheap_llm = LLMFactory.create_llm("deepseek", ModelTier.CHEAP)
standard_llm = LLMFactory.create_llm("qwen-turbo", ModelTier.STANDARD)
power_llm = LLMFactory.create_llm("claude", ModelTier.POWER)

# 获取默认 LLM
default_llm = LLMFactory.get_default_llm(ModelTier.STANDARD)

# 检查 provider 可用性
if LLMFactory.is_provider_available("deepseek"):
    llm = LLMFactory.create_llm("deepseek", ModelTier.CHEAP)

# 成本估算
cost = LLMFactory.get_cost_estimate("deepseek", 1000, 500)
```

### 2. 配置 (`src/config.py`)

```python
# LLM Provider API Keys
DEEPSEEK_API_KEY=sk-xxx
DASHSCOPE_API_KEY=sk-xxx
ZHIPU_API_KEY=xxx
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx

# LLM Strategy
LLM_CHEAP_PROVIDER=deepseek
LLM_STANDARD_PROVIDER=qwen-turbo
LLM_POWER_PROVIDER=claude
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

### 3. 工作流集成 (`src/workflows/hybrid_workflow.py`)

```python
class HybridTravelWorkflow:
    def __init__(self):
        # 使用工厂创建三层 LLM
        self.cheap_llm = LLMFactory.create_llm(
            settings.llm_cheap_provider, 
            ModelTier.CHEAP
        )
        self.standard_llm = LLMFactory.create_llm(
            settings.llm_standard_provider, 
            ModelTier.STANDARD
        )
        self.power_llm = LLMFactory.create_llm(
            settings.llm_power_provider, 
            ModelTier.POWER
        )
    
    async def _collect_info(self, state):
        # 使用便宜层 LLM 进行简单信息提取
        info_agent = create_agent(
            model=self.cheap_llm,
            system_prompt=INFO_COLLECTION_PROMPT
        )
```

## 文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `src/config/llm_config.py` | LLMFactory 和 ModelTier 实现 |
| `src/config/__init__.py` | 配置模块初始化 |
| `tests/test_llm_factory.py` | LLMFactory 单元测试 |
| `tests/test_multi_model_workflow.py` | 工作流集成测试 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/config.py` | 新增 LLM tier 和 API Key 配置 |
| `src/workflows/hybrid_workflow.py` | 集成 LLMFactory |
| `src/agents/deep_subagents.py` | 支持通用 LLM 类型 |
| `src/agents/info_collection.py` | 移除 claude_client 依赖 |
| `src/agents/recommendation.py` | 移除 claude_client 依赖 |
| `src/utils/claude.py` | 标记为遗留代码 |
| `.env.example` | 添加新配置项 |

## 使用指南

### 快速开始

1. **配置 API Keys**

```bash
# 编辑 .env 文件
DEEPSEEK_API_KEY=sk-your-deepseek-key
DASHSCOPE_API_KEY=sk-your-dashscope-key
```

2. **选择模型策略**

```bash
# 成本优先（推荐）
LLM_CHEAP_PROVIDER=deepseek
LLM_STANDARD_PROVIDER=qwen-turbo
LLM_POWER_PROVIDER=deepseek-reasoner

# 质量优先
LLM_CHEAP_PROVIDER=qwen-plus
LLM_STANDARD_PROVIDER=claude
LLM_POWER_PROVIDER=claude
```

3. **运行测试**

```bash
pytest tests/test_llm_factory.py -v
pytest tests/test_multi_model_workflow.py -v
```

### 切换模型示例

```python
from config.llm_config import LLMFactory, ModelTier

# 从 Claude 切换到 DeepSeek
llm = LLMFactory.create_llm("deepseek", ModelTier.STANDARD)

# 从 DeepSeek 切换到 Qwen
llm = LLMFactory.create_llm("qwen-turbo", ModelTier.STANDARD)
```

## 错误处理

### 自动降级

当指定 provider 的 API Key 未配置时，LLMFactory 会自动降级到备选 provider：

```python
# 如果 deepseek 未配置，自动尝试 qwen-plus
llm = LLMFactory.create_llm("deepseek", ModelTier.CHEAP)
```

### 降级链

| 层级 | 降级顺序 |
|------|----------|
| CHEAP | deepseek → qwen-plus → gpt-4o-mini → qwen-turbo |
| STANDARD | qwen-turbo → glm-4 → gpt-4o → qwen-max |
| POWER | claude → deepseek-reasoner → qwen-max → gpt-4o |

## 性能优化建议

1. **使用 Prompt Cache** - 静态系统提示词可被缓存
2. **批量请求** - 减少 API 调用次数
3. **选择合适层级** - 简单任务使用便宜层
4. **监控成本** - 使用 `get_cost_estimate()` 追踪消耗

## 迁移指南

### 从旧版本迁移

1. **移除 Claude 直接调用**

```python
# 旧代码
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(api_key=..., model=...)

# 新代码
from config.llm_config import LLMFactory
llm = LLMFactory.create_llm("claude", ModelTier.POWER)
```

2. **更新 Agent 初始化**

```python
# 旧代码
agent = InfoCollectionAgent()  # 内部使用 claude_client

# 新代码
from config.llm_config import LLMFactory
llm = LLMFactory.create_llm("deepseek", ModelTier.CHEAP)
agent = InfoCollectionAgent(llm=llm)
```

## 测试覆盖

- ✅ LLMFactory 工厂方法测试
- ✅ 模型配置查找测试
- ✅ 成本估算测试
- ✅ 降级机制测试
- ✅ Provider 可用性测试
- ✅ 工作流 LLM 初始化测试
- ✅ Agent LLM 兼容性测试

## 未来扩展

### 支持新模型

在 `MODEL_CONFIGS` 字典中添加配置：

```python
"new-model": ModelConfig(
    name="new-model",
    display_name="New Model",
    provider=LLMProvider.NEW_PROVIDER,
    tier=ModelTier.STANDARD,
    base_url="https://api.new.com/v1",
    cost_per_1k_tokens=0.01
)
```

### 添加新 Provider

1. 在 `LLMProvider` 枚举中添加新 provider
2. 更新 `get_api_key()` 方法
3. 在 `MODEL_CONFIGS` 中添加模型配置

## 总结

本次改造实现了：

1. **架构解耦** - 从单一 Claude 依赖到统一接口
2. **成本优化** - 预计降低 90%+ 运营成本
3. **灵活扩展** - 支持快速添加新模型
4. **配置驱动** - 通过环境变量控制模型策略
5. **向后兼容** - 保留 ClaudeClient 作为遗留实现

改造后，系统可以在不同场景下选择最适合的模型，在保证服务质量的同时显著降低成本。
