import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def hybrid_rank(
    raw_results: List[Dict[str, Any]], 
    rag_docs: List[Any], 
    criteria: Dict[str, Any],
    item_type: str = "hotel"
) -> List[Dict[str, Any]]:
    """
    混合排序算法
    权重配置：
    - DB 分（位置权）：0.25
    - RAG 分（语义权）：0.35
    - 价格分：0.25
    - 评分分：0.15
    """
    weights = {
        "db": 0.25,
        "rag": 0.35,
        "price": 0.25,
        "rating": 0.15
    }
    
    ranked_items = []
    
    # 提取 RAG 文档的内容和分数
    rag_scores = {}
    for i, doc in enumerate(rag_docs):
        # 假设 doc 有 content 和 metadata，或者直接是 content
        content = getattr(doc, 'page_content', str(doc))
        metadata = getattr(doc, 'metadata', {})
        # 尝试匹配 ID
        item_id = metadata.get('id')
        if item_id:
            # 排名越靠前分数越高，简单归一化
            rag_scores[str(item_id)] = 1.0 - (i / len(rag_docs)) if len(rag_docs) > 0 else 0.5

    for i, item in enumerate(raw_results):
        item_id = str(item.get('id'))
        
        # 1. DB 分 (基于原始排序，假设原始排序已经有一定逻辑)
        db_score = 1.0 - (i / len(raw_results)) if len(raw_results) > 0 else 0.5
        
        # 2. RAG 分
        rag_score = rag_scores.get(item_id, 0.0)
        
        # 3. 价格分
        price_score = _calc_price_score(item.get('price', 0), criteria.get('price_range', {}))
        
        # 4. 评分分
        rating_score = (item.get('rating', 0) / 5.0) if item.get('rating') else 0.0
        
        # 总分计算
        total_score = (
            db_score * weights["db"] +
            rag_score * weights["rag"] +
            price_score * weights["price"] +
            rating_score * weights["rating"]
        )
        
        # 生成说明
        explanation = _explain_score(db_score, rag_score, price_score, rating_score, weights)
        
        item_with_score = item.copy()
        item_with_score['_score'] = round(total_score, 4)
        item_with_score['_explanation'] = explanation
        ranked_items.append(item_with_score)
        
    # 按总分排序
    ranked_items.sort(key=lambda x: x['_score'], reverse=True)
    
    return ranked_items

def _calc_price_score(price: float, budget_range: Dict[str, float]) -> float:
    """价格匹配分"""
    if not budget_range:
        return 0.5
    
    min_p = budget_range.get('min', 0)
    max_p = budget_range.get('max', float('inf'))
    
    if min_p <= price <= max_p:
        return 1.0
    elif price < min_p:
        # 低于预算也给不错的分数，但不完美
        return 0.8
    else:
        # 高于预算，按超出程度扣分
        diff = price - max_p
        return max(0, 1.0 - (diff / max_p)) if max_p > 0 else 0.0

def _explain_score(db_score: float, rag_score: float, price_score: float, rating_score: float, weights: Dict[str, float]) -> str:
    """生成排序说明"""
    reasons = []
    if rag_score > 0.7:
        reasons.append("语义匹配度高")
    if price_score >= 1.0:
        reasons.append("符合预算")
    if rating_score > 0.8:
        reasons.append("用户评价极好")
        
    explanation = f"综合评分 {round(db_score*weights['db'] + rag_score*weights['rag'] + price_score*weights['price'] + rating_score*weights['rating'], 2)}: "
    explanation += ", ".join(reasons) if reasons else "匹配度良好"
    return explanation
