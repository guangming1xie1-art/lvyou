"""
Query改写引擎模块

实现企业级Query改写功能，包括指代消解、意图补全等。
采用混合策略：规则过滤 → 微调模型 → 大模型兜底。

改写场景：
1. 指代消解："它有什么优势？" → "A酒店有什么优势？"
2. 意图补全："便宜点的" → "推荐便宜的酒店"
3. 上下文补全："五天" → "去三亚玩五天"

改写策略：
1. 快速检查：判断是否需要改写
2. 微调模型：使用7B模型进行改写
3. 大模型兜底：使用GPT-4等大模型
"""
from typing import Dict, List, Any, Optional
import logging
import re
from enum import Enum

from llm.factory import LLMFactory
from utils.logger import app_logger

logger = app_logger.getChild(__name__)


class RewriteScenario(Enum):
    """改写场景枚举"""
    PRONOUN_RESOLUTION = "pronoun_resolution"  # 指代消解
    INTENT_COMPLETION = "intent_completion"    # 意图补全
    CONTEXT_COMPLETION = "context_completion"  # 上下文补全
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"  # 歧义消解


class QueryRewriter:
    """Query改写引擎
    
    实现企业级Query改写功能，包括指代消解、意图补全等。
    采用混合策略：规则过滤 → 微调模型 → 大模型兜底。
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        use_local_model: bool = True,
        local_model_name: str = "qwen-7b",
        cloud_model_name: str = "gpt-4"
    ):
        """
        初始化Query改写引擎
        
        Args:
            confidence_threshold: 置信度阈值
            use_local_model: 是否使用本地微调模型
            local_model_name: 本地模型名称
            cloud_model_name: 云端模型名称
        """
        self.confidence_threshold = confidence_threshold
        self.use_local_model = use_local_model
        self.local_model_name = local_model_name
        self.cloud_model_name = cloud_model_name
        
        # 初始化LLM
        self.llm_factory = LLMFactory()
        self.local_llm = None
        self.cloud_llm = None
        
        logger.info(f"QueryRewriter initialized: local_model={use_local_model}, threshold={confidence_threshold}")
    
    async def initialize(self):
        """初始化改写引擎"""
        try:
            logger.info("Initializing QueryRewriter...")
            
            # 初始化云端LLM（兜底）
            self.cloud_llm = self.llm_factory.get_llm(
                provider="openai",
                model=self.cloud_model_name,
                temperature=0.3
            )
            
            # 初始化本地LLM（可选）
            if self.use_local_model:
                try:
                    self.local_llm = self.llm_factory.get_llm(
                        provider="zhipu",
                        model=self.local_model_name,
                        temperature=0.3
                    )
                    logger.info(f"Local model {self.local_model_name} initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize local model: {e}, will use cloud model only")
                    self.use_local_model = False
            
            logger.info("QueryRewriter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize QueryRewriter: {e}")
            raise
    
    async def rewrite(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        long_term_memory: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        改写Query
        
        Args:
            query: 原始查询
            conversation_history: 对话历史
            long_term_memory: 长期记忆
            
        Returns:
            改写结果
        """
        try:
            logger.info(f"Rewriting query: '{query}'")
            
            # 1. 快速检查是否需要改写
            needs_rewrite, scenario = self._needs_rewrite(query, conversation_history)
            
            if not needs_rewrite:
                logger.info("Query does not need rewrite")
                return {
                    "original_query": query,
                    "rewritten_query": query,
                    "needs_rewrite": False,
                    "scenario": None,
                    "model_used": None
                }
            
            logger.info(f"Query needs rewrite: scenario={scenario}")
            
            # 2. 尝试使用本地模型
            if self.use_local_model and self.local_llm:
                try:
                    result = await self._rewrite_with_local_model(
                        query=query,
                        conversation_history=conversation_history,
                        long_term_memory=long_term_memory,
                        scenario=scenario
                    )
                    
                    if result["confidence"] >= self.confidence_threshold:
                        logger.info(f"Query rewritten with local model: confidence={result['confidence']}")
                        return {
                            "original_query": query,
                            "rewritten_query": result["query"],
                            "needs_rewrite": True,
                            "scenario": scenario,
                            "model_used": "local_7b",
                            "confidence": result["confidence"]
                        }
                except Exception as e:
                    logger.warning(f"Local model failed: {e}")
            
            # 3. 兜底：使用云端大模型
            result = await self._rewrite_with_cloud_model(
                query=query,
                conversation_history=conversation_history,
                long_term_memory=long_term_memory,
                scenario=scenario
            )
            
            logger.info(f"Query rewritten with cloud model")
            return {
                "original_query": query,
                "rewritten_query": result["query"],
                "needs_rewrite": True,
                "scenario": scenario,
                "model_used": "cloud_gpt4",
                "confidence": result.get("confidence", 0.9)
            }
        
        except Exception as e:
            logger.error(f"Failed to rewrite query: {e}")
            return {
                "original_query": query,
                "rewritten_query": query,
                "needs_rewrite": False,
                "scenario": None,
                "model_used": None,
                "error": str(e)
            }
    
    def _needs_rewrite(
        self,
        query: str,
        conversation_history: List[Dict[str, str]]
    ) -> tuple[bool, Optional[RewriteScenario]]:
        """
        快速检查是否需要改写
        
        Args:
            query: 查询文本
            conversation_history: 对话历史
            
        Returns:
            (是否需要改写, 改写场景)
        """
        # 1. 检查指代词
        pronouns = ["它", "他", "她", "这个", "那个", "这些", "那些"]
        if any(p in query for p in pronouns):
            return True, RewriteScenario.PRONOUN_RESOLUTION
        
        # 2. 检查省略
        if len(query) < 5:
            return True, RewriteScenario.INTENT_COMPLETION
        
        # 3. 检查模糊词
        vague_words = ["便宜", "贵", "好", "差", "多", "少"]
        if any(word in query for word in vague_words):
            return True, RewriteScenario.AMBIGUITY_RESOLUTION
        
        # 4. 检查数字（可能是省略）
        if re.match(r'^\d+.*', query):
            return True, RewriteScenario.CONTEXT_COMPLETION
        
        # 5. 检查是否有上下文
        if not conversation_history:
            return False, None
        
        # 6. 检查是否与上一轮对话相关
        last_message = conversation_history[-1].get("content", "")
        if last_message and len(query) < 10:
            return True, RewriteScenario.CONTEXT_COMPLETION
        
        return False, None
    
    async def _rewrite_with_local_model(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        long_term_memory: Optional[Dict[str, Any]],
        scenario: RewriteScenario
    ) -> Dict[str, Any]:
        """
        使用本地模型改写
        
        Args:
            query: 原始查询
            conversation_history: 对话历史
            long_term_memory: 长期记忆
            scenario: 改写场景
            
        Returns:
            改写结果
        """
        prompt = self._build_rewrite_prompt(
            query=query,
            conversation_history=conversation_history,
            long_term_memory=long_term_memory,
            scenario=scenario
        )
        
        response = await self.local_llm.ainvoke(prompt)
        
        return {
            "query": response.strip(),
            "confidence": 0.8
        }
    
    async def _rewrite_with_cloud_model(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        long_term_memory: Optional[Dict[str, Any]],
        scenario: RewriteScenario
    ) -> Dict[str, Any]:
        """
        使用云端模型改写
        
        Args:
            query: 原始查询
            conversation_history: 对话历史
            long_term_memory: 长期记忆
            scenario: 改写场景
            
        Returns:
            改写结果
        """
        prompt = self._build_rewrite_prompt(
            query=query,
            conversation_history=conversation_history,
            long_term_memory=long_term_memory,
            scenario=scenario
        )
        
        response = await self.cloud_llm.ainvoke(prompt)
        
        return {
            "query": response.strip(),
            "confidence": 0.9
        }
    
    def _build_rewrite_prompt(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        long_term_memory: Optional[Dict[str, Any]],
        scenario: RewriteScenario
    ) -> str:
        """
        构建改写Prompt
        
        Args:
            query: 原始查询
            conversation_history: 对话历史
            long_term_memory: 长期记忆
            scenario: 改写场景
            
        Returns:
            Prompt字符串
        """
        prompt_parts = []
        
        # 1. 系统提示
        prompt_parts.append("你是一个专业的Query改写助手。")
        prompt_parts.append("你的任务是根据对话上下文和用户偏好，将用户的不完整查询改写为完整、清晰的查询。")
        prompt_parts.append("")
        
        # 2. 场景说明
        scenario_descriptions = {
            RewriteScenario.PRONOUN_RESOLUTION: "指代消解：将代词替换为具体实体",
            RewriteScenario.INTENT_COMPLETION: "意图补全：补充缺失的意图信息",
            RewriteScenario.CONTEXT_COMPLETION: "上下文补全：补充上下文信息",
            RewriteScenario.AMBIGUITY_RESOLUTION: "歧义消解：消除模糊表述"
        }
        prompt_parts.append(f"改写场景：{scenario_descriptions.get(scenario, '通用改写')}")
        prompt_parts.append("")
        
        # 3. 对话历史
        if conversation_history:
            prompt_parts.append("对话历史：")
            for i, msg in enumerate(conversation_history[-5:]):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("")
        
        # 4. 长期记忆
        if long_term_memory:
            prompt_parts.append("用户偏好：")
            preferences = long_term_memory.get("preferences", [])
            for pref in preferences[:5]:
                prompt_parts.append(f"- {pref}")
            prompt_parts.append("")
        
        # 5. 当前查询
        prompt_parts.append(f"当前查询：{query}")
        prompt_parts.append("")
        
        # 6. 改写要求
        prompt_parts.append("改写要求：")
        prompt_parts.append("1. 保持原意不变")
        prompt_parts.append("2. 补充缺失的信息")
        prompt_parts.append("3. 消除歧义和指代")
        prompt_parts.append("4. 保持简洁明了")
        prompt_parts.append("5. 只返回改写后的查询，不要其他内容")
        prompt_parts.append("")
        prompt_parts.append("改写后的查询：")
        
        return "\n".join(prompt_parts)
    
    async def batch_rewrite(
        self,
        queries: List[str],
        conversation_history: List[Dict[str, str]],
        long_term_memory: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量改写Query
        
        Args:
            queries: 查询列表
            conversation_history: 对话历史
            long_term_memory: 长期记忆
            
        Returns:
            改写结果列表
        """
        results = []
        
        for query in queries:
            result = await self.rewrite(
                query=query,
                conversation_history=conversation_history,
                long_term_memory=long_term_memory
            )
            results.append(result)
        
        return results


# 全局Query改写引擎实例
query_rewriter = QueryRewriter()
