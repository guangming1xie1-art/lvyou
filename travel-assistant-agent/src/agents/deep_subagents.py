"""
DeepAgent 子代理管理
创建搜索和推荐专用的简化版 DeepAgent 实例
支持多模型分层调用
"""
import asyncio
from typing import Any, Dict, List, Optional
from langchain_experimental import create_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.tools import BaseTool
from loguru import logger
from config import settings


class SimplifiedDeepAgent:
    """简化版 DeepAgent 实现
    
    支持任意 OpenAI 兼容的 LLM 实例
    """
    
    def __init__(self, llm: Any, system_prompt: str, tools: List[BaseTool] = None):
        """
        初始化 DeepAgent
        
        Args:
            llm: LLM 实例（ChatOpenAI, ChatAnthropic 或其他兼容实例）
            system_prompt: 系统提示词
            tools: 工具列表
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.agent = None
        
        # 记录 LLM 类型信息
        if hasattr(llm, 'model_name'):
            self.llm_model = llm.model_name
        elif hasattr(llm, 'model'):
            self.llm_model = llm.model
        else:
            self.llm_model = str(type(llm).__name__)
        
        logger.info(f"SimplifiedDeepAgent initialized with model: {self.llm_model}")
        
    async def initialize(self):
        """初始化代理"""
        try:
            self.agent = create_agent(
                model=self.llm,
                tools=self.tools,
                system_prompt=self.system_prompt
            )
            logger.info("Simplified DeepAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DeepAgent: {e}")
            raise
            
    async def ainvoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行代理"""
        if not self.agent:
            await self.initialize()
            
        try:
            # 将 inputs 转换为字符串格式
            input_text = str(inputs)
            
            # 调用代理
            result = await self.agent.ainvoke({"input": input_text})
            
            return result
        except Exception as e:
            logger.error(f"DeepAgent execution failed: {e}")
            return {"error": str(e), "content": f"DeepAgent 执行失败: {str(e)}"}


class DeepSubAgentsManager:
    """DeepAgent 子代理管理器
    
    支持任意 OpenAI 兼容的 LLM 实例
    """
    
    def __init__(self, llm: Any):
        """
        初始化管理器
        
        Args:
            llm: LLM 实例（ChatOpenAI, ChatAnthropic 或其他兼容实例）
        """
        self.llm = llm
        self.search_deep_agent = None
        self.recommend_deep_agent = None
        self.mcp_client = None
        self._initialized = False
        
        # 记录 LLM 类型信息
        if hasattr(llm, 'model_name'):
            self.llm_model = llm.model_name
        elif hasattr(llm, 'model'):
            self.llm_model = llm.model
        else:
            self.llm_model = str(type(llm).__name__)
        
        logger.info(f"DeepSubAgentsManager initialized with model: {self.llm_model}")
        
    async def initialize(self):
        """初始化 DeepAgent 实例"""
        if self._initialized:
            return
            
        logger.info("Initializing DeepSubAgents...")
        
        try:
            # 创建搜索 DeepAgent
            self.search_deep_agent = await self._create_search_deep_agent()
            
            # 创建推荐 DeepAgent  
            self.recommend_deep_agent = await self._create_recommend_deep_agent()
            
            self._initialized = True
            logger.info("DeepSubAgents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepSubAgents: {e}")
            raise
            
    async def _create_search_deep_agent(self):
        """创建搜索 DeepAgent"""
        
        # 静态搜索系统提示词（便于 Prompt Cache）
        SEARCH_SYSTEM_PROMPT = """你是一个专业的旅游搜索专家。

你的任务是：
1. 分析用户需求，确定搜索策略
2. 模拟搜索相关信息的过程
3. 评估搜索质量和完整性
4. 整理搜索结果供后续推荐使用

搜索策略：
- 先搜索目的地基本信息（景点、天气、文化等）
- 再搜索具体服务（酒店、机票、餐厅等）
- 最后搜索用户评价和实时信息

评估标准：
- 搜索结果覆盖度 > 80%
- 信息时效性 > 70%
- 数据完整性 > 75%

返回格式：
{
    "search_strategy": "搜索策略说明",
    "search_results": "搜索结果汇总",
    "search_quality": 0.85,
    "search_completeness": "搜索完整性评估",
    "next_steps": "下一步行动建议"
}

重要：使用中文输出，保持专业性和准确性。"""

        try:
            # 创建 DeepAgent 实例
            search_deep_agent = SimplifiedDeepAgent(
                llm=self.llm,
                system_prompt=SEARCH_SYSTEM_PROMPT,
                tools=[]
            )
            
            await search_deep_agent.initialize()
            logger.info("Search DeepAgent created successfully")
            return search_deep_agent
            
        except Exception as e:
            logger.error(f"Failed to create search DeepAgent: {e}")
            raise
            
    async def _create_recommend_deep_agent(self):
        """创建推荐 DeepAgent"""
        
        # 静态推荐系统提示词（便于 Prompt Cache）
        RECOMMEND_SYSTEM_PROMPT = """你是一个专业的旅游推荐专家。

你的任务是：
1. 分析用户偏好和搜索结果
2. 综合多维度因素进行深度思考
3. 生成个性化推荐方案
4. 评估推荐质量和可信度

推荐维度：
- 价格：预算匹配度、成本效益比
- 质量：评分、用户评价、专业认证
- 匹配度：与用户偏好的契合度
- 时效性：季节适宜性、当前热门程度
- 独特性：特色亮点、差异化体验

推理过程：
1. 解析用户画像和需求
2. 分析搜索结果质量和覆盖度
3. 应用推荐算法和权重模型
4. 生成多个候选方案
5. 评估和排序推荐结果

返回格式：
{
    "recommendation_strategy": "推荐策略说明",
    "user_analysis": "用户需求分析",
    "recommendations": [
        {
            "id": "方案ID",
            "title": "方案标题",
            "summary": "方案概要",
            "score": 0.92,
            "strengths": ["优势1", "优势2"],
            "considerations": ["注意事项1", "注意事项2"],
            "estimated_cost": "预估费用",
            "best_for": "最适合人群"
        }
    ],
    "recommendation_quality": 0.88,
    "confidence_level": 0.85
}

重要：使用中文输出，提供实用、可操作的建议。"""

        try:
            # 创建 DeepAgent 实例
            recommend_deep_agent = SimplifiedDeepAgent(
                llm=self.llm,
                system_prompt=RECOMMEND_SYSTEM_PROMPT,
                tools=[]
            )
            
            await recommend_deep_agent.initialize()
            logger.info("Recommendation DeepAgent created successfully")
            return recommend_deep_agent
            
        except Exception as e:
            logger.error(f"Failed to create recommendation DeepAgent: {e}")
            raise
            
    async def search_with_deep_agent(self, user_message: str, collected_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用 DeepAgent 执行搜索"""
        if not self._initialized:
            await self.initialize()
            
        try:
            logger.info("Starting DeepAgent search...")
            
            # 构造搜索输入
            search_input = {
                "user_message": user_message,
                "collected_info": collected_info,
                "task": "请执行旅游搜索，收集全面的旅游信息并评估搜索质量。"
            }
            
            # 调用 DeepAgent
            result = await self.search_deep_agent.ainvoke(search_input)
            
            # 解析结果
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
                
            # 尝试解析 JSON
            try:
                import json
                search_results = json.loads(content)
                # 确保必要的字段存在
                if 'search_quality' not in search_results:
                    search_results['search_quality'] = 0.6
                if 'search_results' not in search_results:
                    search_results['search_results'] = {}
                return search_results
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，包装成标准格式
                return {
                    "search_strategy": "使用 DeepAgent 深度搜索",
                    "search_results": {"raw_content": content},
                    "search_quality": 0.7,
                    "search_completeness": "基础搜索完成"
                }
                
        except Exception as e:
            logger.error(f"DeepAgent search failed: {e}")
            return {
                "search_strategy": "降级搜索策略",
                "search_results": {"error": str(e)},
                "search_quality": 0.3,
                "search_completeness": "搜索失败"
            }
            
    async def recommend_with_deep_agent(self, user_message: str, collected_info: Dict[str, Any], 
                                      search_results: Dict[str, Any]) -> Dict[str, Any]:
        """使用 DeepAgent 执行推荐"""
        if not self._initialized:
            await self.initialize()
            
        try:
            logger.info("Starting DeepAgent recommendation...")
            
            # 构造推荐输入
            recommend_input = {
                "user_message": user_message,
                "collected_info": collected_info,
                "search_results": search_results,
                "task": "请基于以上信息，生成个性化的旅游推荐方案。"
            }
            
            # 调用 DeepAgent
            result = await self.recommend_deep_agent.ainvoke(recommend_input)
            
            # 解析结果
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
                
            # 尝试解析 JSON
            try:
                import json
                recommendations = json.loads(content)
                # 确保必要的字段存在
                if 'recommendations' not in recommendations:
                    recommendations['recommendations'] = []
                if 'recommendation_quality' not in recommendations:
                    recommendations['recommendation_quality'] = 0.7
                return recommendations
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，包装成标准格式
                return {
                    "recommendation_strategy": "使用 DeepAgent 深度推荐",
                    "user_analysis": "基于收集信息分析",
                    "recommendations": [
                        {
                            "id": "default_plan",
                            "title": "定制化旅游方案",
                            "summary": content[:200] + "..." if len(content) > 200 else content,
                            "score": 0.7,
                            "strengths": ["个性化定制"],
                            "considerations": ["需要进一步确认"],
                            "estimated_cost": "待评估",
                            "best_for": "所有用户"
                        }
                    ],
                    "recommendation_quality": 0.7
                }
                
        except Exception as e:
            logger.error(f"DeepAgent recommendation failed: {e}")
            return {
                "recommendation_strategy": "降级推荐策略",
                "recommendations": [],
                "recommendation_quality": 0.3,
                "error": str(e)
            }
            
    async def cleanup(self):
        """清理资源"""
        try:
            self._initialized = False
            logger.info("DeepSubAgents cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# 全局实例管理器
_deep_agents_manager: Optional[DeepSubAgentsManager] = None


async def get_deep_agents_manager(llm: Any) -> DeepSubAgentsManager:
    """获取 DeepAgents 管理器实例
    
    Args:
        llm: LLM 实例（ChatOpenAI, ChatAnthropic 或其他兼容实例）
    """
    global _deep_agents_manager
    
    if _deep_agents_manager is None:
        _deep_agents_manager = DeepSubAgentsManager(llm)
        await _deep_agents_manager.initialize()
        
    return _deep_agents_manager


async def cleanup_deep_agents():
    """清理 DeepAgents 资源"""
    global _deep_agents_manager
    
    if _deep_agents_manager:
        await _deep_agents_manager.cleanup()
        _deep_agents_manager = None