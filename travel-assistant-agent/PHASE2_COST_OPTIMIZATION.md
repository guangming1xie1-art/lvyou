# Phase 2 成本优化体系实现文档

## 📋 概述

本实现整合了三个Phase：
- **Phase 2.1**: RAG知识库（向量检索 + BM25混合检索）
- **Phase 2.2**: Prompt Cache（系统提示、RAG上下文、工具定义缓存）
- **Phase 2.3**: Redis缓存层（Cache-Aside模式、多层缓存策略）

## 🏗️ 文件结构

```
travel-assistant-agent/src/
├── rag/                          # RAG知识库模块
│   ├── __init__.py              # 模块导出
│   ├── embeddings.py            # Embedding工厂
│   ├── vectorstore.py           # 向量存储管理
│   ├── retriever.py             # 混合检索器
│   └── knowledge_base.py        # 知识库管理
│
├── cache/                        # 缓存模块
│   ├── __init__.py              # 模块导出
│   ├── cache_key.py             # 缓存键生成
│   ├── prompt_cache.py          # Prompt缓存管理
│   └── cache_strategy.py        # 缓存策略
│
├── config.py                    # 配置更新
│
└── workflows/conversation/nodes/
    └── search.py                # 搜索节点更新
```

## 🔧 核心组件

### 1. RAG知识库 (rag/)

#### EmbeddingFactory
```python
class EmbeddingFactory:
    @classmethod
    def get_embeddings(cls, model=None, api_key=None, base_url=None) -> Embeddings:
        """获取Embedding模型单例"""
        
    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """嵌入单个文本"""
        
    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        """嵌入多个文本"""
```

#### VectorStoreManager
```python
class VectorStoreManager:
    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量存储"""
        
    def search(self, query: str, k: int = 5, filter=None) -> List[Document]:
        """向量相似度搜索"""
        
    def save(self):
        """保存向量存储"""
```

#### HybridRetriever
```python
class HybridRetriever:
    def __init__(self, vectorstore=None, vector_weight=0.6, bm25_weight=0.4):
        """初始化混合检索器（向量权重 + BM25权重 = 1）"""
        
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """混合检索：结合向量和BM25结果"""
```

#### KnowledgeBase
```python
class KnowledgeBase:
    def add_knowledge(self, texts: List[str], metadatas=None) -> List[str]:
        """添加知识到知识库"""
        
    def search(self, query: str, k: int = 5, filters=None) -> List[Document]:
        """搜索知识库"""
        
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """获取相关上下文（用于Prompt）"""
```

### 2. 缓存模块 (cache/)

#### CacheKeyGenerator
```python
class CacheKeyGenerator:
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """生成缓存键（MD5哈希）"""
        
    @staticmethod
    def generate_search_key(query, origin=None, destination=None, date=None) -> str:
        """搜索结果缓存键"""
        
    @staticmethod
    def generate_rag_context_key(query: str) -> str:
        """RAG上下文缓存键"""
```

#### PromptCacheManager
```python
class PromptCacheManager:
    def cache_system_prompt(self, prompt: str) -> Dict:
        """缓存系统提示词"""
        
    def cache_rag_context(self, context: str, query: str) -> Dict:
        """缓存RAG上下文"""
        
    def build_cached_messages(self, system_prompt, rag_context=None, user_message="") -> List[Dict]:
        """构建带缓存标记的消息（支持Claude Prompt Cache）"""
        
    def calculate_token_savings(self, cache_hits, cached_tokens) -> Dict:
        """计算Token节省（Claude缓存读取成本25%，节省75%）"""
```

#### CacheStrategy
```python
class CacheStrategy:
    TTL_CONFIG = {
        "search_results": 3600,      # 1小时
        "recommendations": 21600,   # 6小时
        "rag_context": 3600,        # 1小时
        "booking_info": 1800,       # 30分钟
        "user_preferences": 86400,  # 24小时
    }
    
    def get_or_compute(self, key: str, compute_fn, cache_type="default") -> Any:
        """Cache-Aside模式：获取或计算"""
        
    def cache_search_results(self, query: str, results: Dict, **kwargs) -> bool:
        """缓存搜索结果"""
        
    def get_rag_context(self, query: str) -> Optional[str]:
        """获取RAG上下文"""
```

## ⚙️ 配置更新

### 环境变量
```bash
# Vector Store
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_PATH=./data/vector_store
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=

# Hybrid Search (RAG)
HYBRID_SEARCH_ENABLED=true
HYBRID_SEARCH_VECTOR_WEIGHT=0.6
HYBRID_SEARCH_BM25_WEIGHT=0.4

# Prompt Cache
PROMPT_CACHE_ENABLED=true
PROMPT_CACHE_DIR=.prompt_cache
SYSTEM_PROMPT_CACHE_TTL=86400
TOOL_DEFINITIONS_CACHE_TTL=86400
RAG_CONTEXT_CACHE_TTL=3600

# Cache TTL Configuration (seconds)
CACHE_TTL_SEARCH=3600
CACHE_TTL_RECOMMEND=21600
CACHE_TTL_RAG=3600
CACHE_TTL_BOOKING=1800
CACHE_TTL_USER_PREFS=86400
```

## 🔄 工作流集成

### 搜索节点更新
```python
async def plan_search(state: ConversationState) -> ConversationState:
    # 1. 尝试从缓存获取RAG上下文
    rag_context = cache_strategy.get_rag_context(user_message)
    
    if rag_context is None:
        # 2. 从知识库检索相关上下文
        rag_context = knowledge_base.get_relevant_context(user_message)
        
        # 3. 缓存RAG上下文
        if rag_context:
            cache_strategy.cache_rag_context(user_message, rag_context)
    
    # 4. 返回规划结果

async def execute_search(state: ConversationState) -> ConversationState:
    # 1. 尝试从缓存获取搜索结果
    cached_results = cache_strategy.get_search_results(search_query)
    
    if cached_results is not None:
        return {**state, "search_results": cached_results, "cache_hit": True}
    
    # 2. 执行实际搜索
    search_results = [...]
    
    # 3. 缓存结果
    cache_strategy.cache_search_results(search_query, search_results)
    
    return {**state, "search_results": search_results, "cache_hit": False}
```

## 💰 成本优化效果

| 优化项 | 节省比例 | 说明 |
|--------|----------|------|
| **Prompt Cache** | ~75% | Claude缓存读取成本25% |
| **混合RAG** | 减少重复计算 | 知识库检索一次，多次使用 |
| **Redis缓存** | 减少API调用 | 搜索结果、推荐结果缓存 |
| **三层LLM** | 90%+ | 简单任务用便宜模型 |

### Claude Prompt Cache示例
```
系统提示词缓存：
- 原始成本: $3/1M tokens
- 缓存成本: $0.75/1M tokens
- 节省: 75%

假设每天1000次对话，每次系统提示1000 tokens：
- 原始成本: 1000 × 1000 × $3/1M = $3/天
- 缓存成本: 1000 × 1000 × $0.75/1M = $0.75/天
- 年节省: $821.25
```

## 📊 Redis缓存效果

| 缓存类型 | TTL | 命中率 | 节省估算 |
|----------|-----|--------|----------|
| 搜索结果 | 1小时 | 30-50% | 减少30-50%搜索API调用 |
| 推荐结果 | 6小时 | 40-60% | 减少40-60%推荐API调用 |
| RAG上下文 | 1小时 | 50-70% | 减少50-70%知识库查询 |
| 用户偏好 | 24小时 | 80-90% | 几乎无重复查询 |

## 🧪 测试

```bash
# 运行单元测试
pytest tests/test_rag.py -v
pytest tests/test_cache.py -v

# 运行集成测试
pytest tests/test_rag_cache_integration.py -v

# 语法验证
python3 verify_phase2_syntax.py
```

## ✅ 验证清单

- [x] EmbeddingFactory能正确创建和管理Embedding模型
- [x] VectorStoreManager能正确创建和加载FAISS存储
- [x] HybridRetriever能正确执行向量+BM25混合检索
- [x] KnowledgeBase能正确添加和搜索文档
- [x] PromptCacheManager能正确缓存系统提示和RAG上下文
- [x] CacheKeyGenerator能正确生成缓存键
- [x] CacheStrategy能正确实现Cache-Aside模式
- [x] RedisCache能正确连接和操作Redis
- [x] 搜索节点能正确集成RAG和缓存
- [x] 所有配置可通过环境变量覆盖

## 🎯 关键特性

1. **优雅降级**: Redis不可用时返回None而不是异常
2. **错误处理**: 所有缓存操作都有完善的try-except
3. **日志记录**: 关键操作都有DEBUG级别日志
4. **TTL配置**: 可通过环境变量自定义TTL
5. **统计监控**: 支持缓存命中率和统计信息查询
6. **持久化**: Prompt缓存支持磁盘持久化
7. **灵活性**: 支持自定义权重、过滤器等配置
