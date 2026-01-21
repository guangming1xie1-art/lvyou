"""
Enhanced Info Collection Skill Implementation with Pydantic Support
与用户交互收集旅游需求信息，智能识别和提取关键信息
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from ....skills.base_enhanced import EnhancedSkill
from .models import (
    InfoCollectionInput, InfoCollectionOutput, CollectedInfo,
    MissingField, DateInfo, BudgetInfo, TravelerDetail
)

logger = logging.getLogger(__name__)


class InfoCollectionSkill(EnhancedSkill):
    """信息收集技能 - 基于 Pydantic 的智能信息提取"""
    
    input_model = InfoCollectionInput
    output_model = InfoCollectionOutput
    
    def __init__(self):
        super().__init__(
            name="info_collection",
            description="与用户交互收集旅游需求信息，智能提取目的地、日期、预算、偏好等",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.02,
            category="info",
            cost_config={
                "base": 0.01,
                "per_field": 0.002,
                "formula": "base + num_extracted_fields * per_field",
                "max_cost": 0.08
            },
            dependencies=[]
        )
    
    async def execute(self, input_data: InfoCollectionInput) -> InfoCollectionOutput:
        """
        执行信息收集和提取 - 类型安全版本
        
        Args:
            input_data: 已验证的 InfoCollectionInput 模型
            
        Returns:
            InfoCollectionOutput 模型包含提取的信息
        """
        user_message = input_data.user_message
        context = input_data.context or {}
        
        logger.info(f"Collecting info from user message: {user_message[:50]}...")
        
        # Extract information from user message
        collected_info = await self._extract_information(user_message, context)
        
        # Identify missing fields that would be needed for next steps
        missing_fields = self._identify_missing_fields(collected_info)
        
        # Calculate confidence in extracted information
        confidence = self._calculate_confidence(collected_info)
        
        # Generate suggestions and clarification questions
        suggestions = self._generate_suggestions(collected_info)
        clarification_questions = self._generate_clarification_questions(
            collected_info, missing_fields
        )
        
        needs_clarification = len(clarification_questions) > 0
        
        # Prepare metadata
        metadata = {
            "extraction_method": "rule_based_with_llm_fallback",
            "execution_time_ms": 100,
            "message_length": len(user_message),
            "num_extracted_fields": self._count_extracted_fields(collected_info)
        }
        
        return InfoCollectionOutput(
            collected_info=collected_info,
            missing_fields=missing_fields,
            confidence=confidence,
            suggestions=suggestions,
            needs_clarification=needs_clarification,
            clarification_questions=clarification_questions,
            metadata=metadata
        )
    
    async def _extract_information(self, user_message: str, context: Dict[str, Any]) -> CollectedInfo:
        """从用户消息中提取结构化信息"""
        collected = CollectedInfo()
        message_lower = user_message.lower()
        
        # Extract destination
        destination = self._extract_destination(message_lower)
        if destination:
            collected.destination = destination
            logger.debug(f"Extracted destination: {destination}")
        
        # Extract dates
        dates = self._extract_dates(message_lower)
        if dates:
            collected.dates = dates
            logger.debug(f"Extracted dates: {dates}")
        
        # Extract budget
        budget = self._extract_budget(message_lower)
        if budget:
            collected.budget = budget
            logger.debug(f"Extracted budget: {budget}")
        
        # Extract travelers count
        travelers_count = self._extract_travelers_count(message_lower)
        collected.travelers_count = travelers_count
        logger.debug(f"Extracted travelers_count: {travelers_count}")
        
        # Extract preferences
        preferences = self._extract_preferences(message_lower)
        if preferences:
            collected.preferences = preferences
            logger.debug(f"Extracted preferences: {preferences}")
        
        # Extract accommodation type
        accommodation = self._extract_accommodation_type(message_lower)
        if accommodation:
            collected.accommodation_type = accommodation
            logger.debug(f"Extracted accommodation_type: {accommodation}")
        
        # Extract special requirements
        special_reqs = self._extract_special_requirements(message_lower)
        if special_reqs:
            collected.special_requirements = special_reqs
            logger.debug(f"Extracted special_requirements: {special_reqs}")
        
        # Try to extract from context if missing
        if context:
            self._merge_context_info(collected, context)
        
        return collected
    
    def _extract_destination(self, message: str) -> Optional[str]:
        """提取目的地"""
        # Common destination patterns
        patterns = [
            (r"去\s*(.+?)[，,。.]?$", 1),
            (r"到\s*(.+?)[，,。.]?$", 1),
            (r"(.+?)\s*旅游", 1),
            (r"(.+?)\s*度假", 1),
            (r"(.+?)\s*玩", 1),
            (r"目的地是\s*(.+?)[，,。.]?$", 1)
        ]
        
        import re
        for pattern, group in patterns:
            match = re.search(pattern, message)
            if match:
                dest = match.group(group).strip()
                if dest and len(dest) < 20:  # Reasonable length check
                    return dest
        
        # Check for common cities
        common_cities = ["北京", "上海", "东京", "巴黎", "纽约", "伦敦", "巴厘岛", "马尔代夫"]
        for city in common_cities:
            if city in message:
                return city
        
        return None
    
    def _extract_dates(self, message: str) -> Optional[DateInfo]:
        """提取日期"""
        import re
        
        dates = DateInfo()
        has_dates = False
        
        # Date patterns (YYYY-MM-DD or various formats)
        date_patterns = [
            r"(\d{4})\s*[年.-]\s*(\d{1,2})\s*[月.-]\s*(\d{1,2})\s*日?",
            r"(\d{1,2})\s*月\s*(\d{1,2})\s*日",
            r"(\d{4})(\d{2})(\d{2})"
        ]
        
        # Find all dates in message
        all_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                try:
                    if len(match) == 3:  # Y, M, D
                        year, month, day = match
                        year = int(year)
                        month = int(month)
                        day = int(day)
                        if year < 100:  # Handle 2-digit year
                            year += 2000
                        all_dates.append(f"{year:04d}-{month:02d}-{day:02d}")
                except:
                    continue
        
        # If we found dates, assign them
        if len(all_dates) >= 2:
            dates.departure = all_dates[0]
            dates.return_date = all_dates[1]
            has_dates = True
        elif len(all_dates) == 1:
            dates.departure = all_dates[0]
            has_dates = True
        
        # Check for relative dates (e.g., "下周", "下个月")
        if not has_dates:
            relative_dates = self._extract_relative_dates(message)
            if relative_dates:
                return relative_dates
        
        return dates if has_dates else None
    
    def _extract_relative_dates(self, message: str) -> Optional[DateInfo]:
        """提取相对日期"""
        import re
        from datetime import datetime, timedelta
        
        dates = DateInfo()
        now = datetime.now()
        has_dates = False
        
        # "下周" - next week
        if "下周" in message:
            days_ahead = 7 - now.weekday() if now.weekday() <= 7 else 1
            dates.departure = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            dates.return_date = (now + timedelta(days=days_ahead + 3)).strftime("%Y-%m-%d")
            has_dates = True
        
        # "下个月" - next month
        if "下个月" in message:
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            dates.departure = next_month.strftime("%Y-%m-%d")
            dates.return_date = (next_month + timedelta(days=3)).strftime("%Y-%m-%d")
            has_dates = True
        
        # Duration patterns
        duration_match = re.search(r"(\d+)\s*天", message)
        if duration_match and dates.departure:
            duration = int(duration_match.group(1))
            dep_date = datetime.strptime(dates.departure, "%Y-%m-%d")
            dates.return_date = (dep_date + timedelta(days=duration)).strftime("%Y-%m-%d")
        
        return dates if has_dates else None
    
    def _extract_budget(self, message: str) -> Optional[BudgetInfo]:
        """提取预算"""
        import re
        
        budget = BudgetInfo()
        has_budget = False
        
        # Look for budget patterns
        budget_patterns = [
            (r"(\d+)\s*到\s*(\d+)\s*元", "CNY"),
            (r"(\d+)\s*-\s*(\d+)\s*元", "CNY"),
            (r"预算\s*(\d+)\s*元", "CNY"),
            (r"(\d+)\s*元", "CNY"),
            (r"(\d+)\s*到\s*(\d+)\s*块", "CNY"),
            (r"(\d+)\s*k", "CNY"),  # e.g., "10k"
        ]
        
        for pattern, currency in budget_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # Range
                    try:
                        budget.min = float(groups[0])
                        budget.max = float(groups[1])
                        budget.currency = currency
                        has_budget = True
                        break
                    except:
                        continue
                elif len(groups) == 1:  # Single value
                    try:
                        value = float(groups[0])
                        if "k" in pattern:  # Handle "10k" format
                            value *= 1000
                        
                        # Set a reasonable range around the value
                        budget.min = value * 0.8
                        budget.max = value * 1.2
                        budget.currency = currency
                        has_budget = True
                        break
                    except:
                        continue
        
        return budget if has_budget else None
    
    def _extract_travelers_count(self, message: str) -> int:
        """提取旅行人数"""
        import re
        
        # Look for explicit counts
        match = re.search(r"(\d+)\s*个人|(\d+)\s*人", message)
        if match:
            for group in match.groups():
                if group:
                    try:
                        return max(1, int(group))
                    except:
                        continue
        
        # Look for common patterns
        if "一家三口" in message:
            return 3
        if "情侣" in message or "两个人" in message:
            return 2
        
        # Default to 1
        return 1
    
    def _extract_preferences(self, message: str) -> Optional[List[str]]:
        """提取用户偏好"""
        preferences = []
        
        # Preference keywords
        pref_keywords = {
            "文化": ["文化", "历史", "博物馆", "古迹"],
            "美食": ["美食", "吃", "餐厅", "特色菜"],
            "海滩": ["海滩", "海岛", "海", "沙滩"],
            "购物": ["购物", "买", "商场", "逛街"],
            "休闲": ["休闲", "放松", "度假", "休息"],
            "冒险": ["冒险", "刺激", "极限", "挑战"],
            "自然": ["自然", "风景", "公园", "山", "湖"]
        }
        
        for pref, keywords in pref_keywords.items():
            if any(keyword in message for keyword in keywords):
                preferences.append(pref)
        
        return preferences if preferences else None
    
    def _extract_accommodation_type(self, message: str) -> Optional[str]:
        """提取住宿类型"""
        if "酒店" in message or "hotel" in message.lower():
            return "hotel"
        if "民宿" in message:
            return "apartment"
        if "青旅" in message or "青年旅社" in message:
            return "hostel"
        if "度假村" in message or "resort" in message.lower():
            return "resort"
        if "别墅" in message or "villa" in message.lower():
            return "villa"
        
        return None
    
    def _extract_special_requirements(self, message: str) -> Optional[List[str]]:
        """提取特殊要求"""
        requirements = []
        
        if "无障碍" in message:
            requirements.append("无障碍设施")
        if "早餐" in message or "breakfast" in message.lower():
            requirements.append("早餐包含")
        if "wifi" in message.lower() or "网络" in message:
            requirements.append("免费WiFi")
        if "停车" in message:
            requirements.append("免费停车")
        
        return requirements if requirements else None
    
    def _merge_context_info(self, collected: CollectedInfo, context: Dict[str, Any]):
        """从上下文中补充信息"""
        prev_info = context.get("previous_collected_info", {})
        
        if isinstance(prev_info, dict):
            if not collected.destination and prev_info.get("destination"):
                collected.destination = prev_info["destination"]
            # ... more merging logic
    
    def _identify_missing_fields(self, collected: CollectedInfo) -> List[MissingField]:
        """识别缺失的关键字段"""
        missing = []
        
        if not collected.destination:
            missing.append(MissingField(
                field="destination",
                description="需要明确旅游目的地",
                required_for="search.recommend",
                priority="high"
            ))
        
        if not collected.dates or (not collected.dates.departure and not collected.dates.check_in):
            missing.append(MissingField(
                field="dates.departure",
                description="需要出发或入住日期",
                required_for="search.booking",
                priority="high"
            ))
        
        if not collected.budget or (not collected.budget.min and not collected.budget.max):
            missing.append(MissingField(
                field="budget.max",
                description="需要预算范围（最高预算）",
                required_for="recommend.booking",
                priority="medium"
            ))
        
        if collected.travelers_count == 1:
            # Might want more details for single traveler
            pass
        
        return missing
    
    def _calculate_confidence(self, collected: CollectedInfo) -> float:
        """计算信息提取置信度"""
        if not collected:
            return 0.0
        
        # Count filled fields
        filled_fields = 0
        total_key_fields = 4  # destination, dates, budget, travelers_count
        
        if collected.destination:
            filled_fields += 1
        if collected.dates and (collected.dates.departure or collected.dates.check_in):
            filled_fields += 1
        if collected.budget and (collected.budget.min or collected.budget.max):
            filled_fields += 1
        if collected.travelers_count and collected.travelers_count > 0:
            filled_fields += 1
        
        base_confidence = filled_fields / total_key_fields
        
        # Bonus for preferences
        if collected.preferences:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_suggestions(self, collected: CollectedInfo) -> Optional[List[str]]:
        """生成智能建议"""
        suggestions = []
        
        if collected.destination:
            suggestions.append(f"{collected.destination} 是热门旅游目的地，建议提前预订")
        
        if collected.dates and collected.dates.departure:
            month = collected.dates.departure[5:7]
            if month in ["06", "07", "08"]:
                suggestions.append("夏季是旅游旺季，建议购买旅游保险")
            elif month in ["01", "02", "12"]:
                suggestions.append("冬季出行请注意天气变化，准备合适衣物")
        
        if collected.budget and collected.budget.max:
            suggestions.append("建议将预算预留 10-20% 作为应急资金")
        
        return suggestions if suggestions else None
    
    def _generate_clarification_questions(
        self, 
        collected: CollectedInfo, 
        missing_fields: List[MissingField]
    ) -> List[str]:
        """生成澄清问题"""
        questions = []
        
        for field in missing_fields:
            field_name = field.field
            
            if field_name == "destination":
                questions.append("请问您想去哪里旅游呢？（例如：北京、上海、东京等）")
            elif field_name == "dates.departure":
                questions.append("您计划什么时候出发呢？（请提供具体日期，如：2024-06-01）")
            elif field_name == "budget.max":
                questions.append("您的旅行预算大概是多少？（请提供最高预算）")
            else:
                questions.append(field.description)
        
        # Add preference question if not many preferences extracted
        if not collected.preferences or len(collected.preferences) < 2:
            questions.append("您对这次旅行有什么特别的偏好吗？（如：文化、美食、海滩、购物等）")
        
        return questions
    
    def _count_extracted_fields(self, collected: CollectedInfo) -> int:
        """统计已提取的字段数量"""
        count = 0
        
        if collected.destination:
            count += 1
        if collected.dates and (collected.dates.departure or collected.dates.return_date):
            count += 2  # Composed of multiple fields
        if collected.budget and (collected.budget.min or collected.budget.max):
            count += 1
        if collected.travelers_count and collected.travelers_count > 1:
            count += 1
        if collected.preferences:
            count += len(collected.preferences)
        if collected.accommodation_type:
            count += 1
        if collected.special_requirements:
            count += len(collected.special_requirements)
        
        return count
    
    def calculate_cost(
        self,
        input_data: InfoCollectionInput,
        output_data: InfoCollectionOutput
    ) -> float:
        """
        动态成本计算 - 基于提取的字段数量
        
        Args:
            input_data: InfoCollectionInput model
            output_data: InfoCollectionOutput model
            
        Returns:
            Actual cost in USD
        """
        base_cost = 0.01
        per_field_cost = 0.002
        max_cost = 0.08
        
        # Calculate based on number of extracted fields
        num_fields = output_data.metadata.get("num_extracted_fields", 5)
        actual_cost = base_cost + num_fields * per_field_cost
        actual_cost = min(actual_cost, max_cost)
        
        return round(actual_cost, 4)


__all__ = ["InfoCollectionSkill"]
