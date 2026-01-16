# Agent Skills Registry

## 概述
所有 Agent Skills 的统一元数据索引。LLM 平时只看这个文件的摘要，按需时才加载完整实现。

## 可用 Skills

### 1. search (搜索技能)
- **名称**: search
- **描述**: 根据用户需求搜索旅游目的地、酒店、航班等信息。支持多种过滤条件（预算、日期、偏好）。
- **输入**: `{"query": string, "filters": object}`
- **输出**: `{"results": array, "total": number, "search_quality": float}`
- **成本估计**: $0.05 per call
- **平均执行时间**: 500ms
- **加载路径**: `src/skills/search/`

### 2. recommend (推荐技能)
- **名称**: recommend
- **描述**: 基于用户偏好和搜索结果生成个性化旅游推荐方案。综合考虑预算、时间、偏好等因素。
- **输入**: `{"user_prefs": object, "search_results": array}`
- **输出**: `{"recommendations": array, "confidence": float}`
- **成本估计**: $0.08 per call
- **平均执行时间**: 800ms
- **加载路径**: `src/skills/recommend/`

### 3. booking (预订技能)
- **名称**: booking
- **描述**: 创建旅游预订、获取预订状态。支持酒店、航班、景点门票等多种预订类型。
- **输入**: `{"booking_details": object}` 或 `{"booking_id": string}` (查询状态)
- **输出**: `{"booking_id": string, "status": string, "details": object}`
- **成本估计**: $0.03 per call
- **平均执行时间**: 300ms
- **加载路径**: `src/skills/booking/`

### 4. info_collection (信息收集技能)
- **名称**: info_collection
- **描述**: 与用户交互收集旅游需求信息。智能提取目的地、日期、预算、偏好等关键信息。
- **输入**: `{"user_message": string, "context": object}`
- **输出**: `{"collected_info": object, "missing_fields": array}`
- **成本估计**: $0.02 per call
- **平均执行时间**: 200ms
- **加载路径**: `src/skills/info_collection/`

## 快速查询

### 列出所有 Skill
```python
from src.skills.registry import SkillRegistry
skills = SkillRegistry.list_skills()
# 返回: [{"name": "search", "description": "..."}, ...]
```

### 加载完整 Skill 实现
```python
from src.skills.registry import SkillRegistry
skill = await SkillRegistry.load_skill("search")
result = await skill.execute({"query": "Paris", "filters": {...}})
```

### 获取 Skill 摘要
```python
from src.skills.registry import SkillRegistry
summary = SkillRegistry.get_skill_summary("search")
# 返回完整的参数和返回值格式
```

### 批量获取摘要（用于 LLM Prompt）
```python
from src.skills.registry import SkillRegistry
summaries = SkillRegistry.get_all_summaries()
# 返回所有 skill 的名称、描述、参数格式
```

## 设计原则

1. **按需加载**: 平时只加载 SKILLS.md，需要时才加载完整实现
2. **成本优化**: 避免在 prompt 中包含大量 skill 实现代码
3. **模块化**: 每个 skill 独立文件夹，方便管理和扩展
4. **统一接口**: 所有 skill 继承 BaseSkill，保证接口一致性

## 扩展 Skill

添加新 skill 的步骤：
1. 在 `src/skills/` 下创建新文件夹（如 `payment/`）
2. 创建 `SKILL.md` 描述文件
3. 创建 `skill.py` 实现文件，继承 `BaseSkill`
4. 更新本文件 `SKILLS.md`，添加新 skill 条目
5. SkillRegistry 会自动发现新 skill
