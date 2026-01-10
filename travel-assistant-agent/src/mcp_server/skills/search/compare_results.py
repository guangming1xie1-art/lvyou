"""CompareResultsSkill - Compare and rank search results"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class CompareResultsSkill(BaseSkill):
    """Compare and rank multiple search results
    
    This skill takes multiple flight or hotel options and compares them
    based on various criteria (price, rating, convenience) to help users
    make informed decisions.
    """
    
    name = "compare_results"
    agent_type = "search"
    description = "Compare and rank search results based on various criteria"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result_type": {
                    "type": "string",
                    "description": "Type of results to compare",
                    "enum": ["flights", "hotels", "mixed"]
                },
                "results": {
                    "type": "array",
                    "description": "Array of search results to compare",
                    "items": {"type": "object"}
                },
                "criteria": {
                    "type": "object",
                    "description": "Comparison criteria weights",
                    "properties": {
                        "price": {"type": "number", "default": 0.4},
                        "quality": {"type": "number", "default": 0.3},
                        "convenience": {"type": "number", "default": 0.3}
                    }
                },
                "max_recommendations": {
                    "type": "integer",
                    "description": "Maximum number of top recommendations",
                    "default": 3
                }
            },
            "required": ["result_type", "results"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "top_recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer"},
                            "item": {"type": "object"},
                            "score": {"type": "number"},
                            "strengths": {"type": "array", "items": {"type": "string"}},
                            "weaknesses": {"type": "array", "items": {"type": "string"}},
                            "recommendation_reason": {"type": "string"}
                        }
                    }
                },
                "comparison_summary": {
                    "type": "object",
                    "properties": {
                        "best_value": {"type": "object"},
                        "best_quality": {"type": "object"},
                        "most_convenient": {"type": "object"},
                        "price_range": {"type": "object"}
                    }
                }
            },
            "required": ["top_recommendations", "comparison_summary"]
        }
    
    async def execute(
        self,
        result_type: str,
        results: List[Dict[str, Any]],
        criteria: Dict[str, float] = None,
        max_recommendations: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Compare and rank results
        
        Args:
            result_type: Type of results (flights, hotels, mixed)
            results: List of results to compare
            criteria: Comparison criteria weights
            max_recommendations: Number of top recommendations
            
        Returns:
            Ranked comparison results with recommendations
        """
        if not self.validate_input({"result_type": result_type, "results": results}):
            raise ValueError("Invalid input: result_type and results are required")
        
        if not results:
            return {
                "top_recommendations": [],
                "comparison_summary": {
                    "best_value": None,
                    "best_quality": None,
                    "most_convenient": None,
                    "price_range": {"min": 0, "max": 0, "average": 0}
                }
            }
        
        # Default criteria weights
        if not criteria:
            criteria = {"price": 0.4, "quality": 0.3, "convenience": 0.3}
        
        # Score each result
        scored_results = []
        all_prices = []
        
        for result in results:
            scores = self._calculate_scores(result, result_type)
            
            # Calculate weighted total score
            total_score = (
                scores["price_score"] * criteria.get("price", 0.4) +
                scores["quality_score"] * criteria.get("quality", 0.3) +
                scores["convenience_score"] * criteria.get("convenience", 0.3)
            )
            
            scored_results.append({
                "item": result,
                "scores": scores,
                "total_score": round(total_score, 2)
            })
            
            # Track prices for range calculation
            price = result.get("total_price") or result.get("price_per_night", 0)
            all_prices.append(price)
        
        # Sort by total score
        scored_results.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Generate recommendations
        top_recommendations = []
        for i, scored in enumerate(scored_results[:max_recommendations]):
            rank = i + 1
            strengths, weaknesses, reason = self._generate_recommendation_text(
                scored, result_type, rank
            )
            
            top_recommendations.append({
                "rank": rank,
                "item": scored["item"],
                "score": scored["total_score"],
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendation_reason": reason
            })
        
        # Find best in each category
        best_value = max(scored_results, key=lambda x: x["scores"]["price_score"])
        best_quality = max(scored_results, key=lambda x: x["scores"]["quality_score"])
        most_convenient = max(scored_results, key=lambda x: x["scores"]["convenience_score"])
        
        return {
            "top_recommendations": top_recommendations,
            "comparison_summary": {
                "best_value": best_value["item"],
                "best_quality": best_quality["item"],
                "most_convenient": most_convenient["item"],
                "price_range": {
                    "min": min(all_prices) if all_prices else 0,
                    "max": max(all_prices) if all_prices else 0,
                    "average": round(sum(all_prices) / len(all_prices), 2) if all_prices else 0
                }
            }
        }
    
    def _calculate_scores(self, result: Dict[str, Any], result_type: str) -> Dict[str, float]:
        """Calculate individual scores for a result"""
        scores = {
            "price_score": 0.0,
            "quality_score": 0.0,
            "convenience_score": 0.0
        }
        
        if result_type == "flights":
            # Price score (lower is better, normalize to 0-1 scale)
            price = result.get("total_price", result.get("price_per_person", 1000))
            scores["price_score"] = max(0, 1 - (price / 2000))  # Assume $2000 is max reasonable
            
            # Quality score based on airline, stops, etc.
            stops = result.get("stops", 0)
            scores["quality_score"] = 1.0 if stops == 0 else 0.7 if stops == 1 else 0.4
            
            # Convenience score based on departure time and duration
            duration = result.get("duration_minutes", 300)
            scores["convenience_score"] = max(0, 1 - (duration / 600))  # 10 hours max
            
        elif result_type == "hotels":
            # Price score
            price = result.get("total_price", result.get("price_per_night", 200))
            scores["price_score"] = max(0, 1 - (price / 500))  # Assume $500/night is max
            
            # Quality score based on rating and reviews
            rating = result.get("rating", 3)
            review_score = result.get("review_score", 7.0)
            scores["quality_score"] = (rating / 5.0) * 0.5 + (review_score / 10.0) * 0.5
            
            # Convenience score based on location
            distance = result.get("distance_to_center", "5 km")
            try:
                dist_km = float(distance.split()[0])
                scores["convenience_score"] = max(0, 1 - (dist_km / 10))  # 10km is far
            except:
                scores["convenience_score"] = 0.5
        
        return scores
    
    def _generate_recommendation_text(
        self, scored: Dict[str, Any], result_type: str, rank: int
    ) -> tuple:
        """Generate strengths, weaknesses, and recommendation reason"""
        item = scored["item"]
        scores = scored["scores"]
        
        strengths = []
        weaknesses = []
        
        # Analyze scores
        if scores["price_score"] >= 0.7:
            strengths.append("Excellent value for money")
        elif scores["price_score"] < 0.4:
            weaknesses.append("Higher price point")
        
        if scores["quality_score"] >= 0.8:
            strengths.append("High quality option")
        elif scores["quality_score"] < 0.5:
            weaknesses.append("Lower quality rating")
        
        if scores["convenience_score"] >= 0.7:
            strengths.append("Very convenient")
        elif scores["convenience_score"] < 0.4:
            weaknesses.append("Less convenient option")
        
        # Generate reason based on rank
        if rank == 1:
            reason = f"Best overall choice with a score of {scored['total_score']}/1.0. Excellent balance of price, quality, and convenience."
        elif rank == 2:
            reason = f"Strong alternative option with a score of {scored['total_score']}/1.0. Good overall value."
        else:
            reason = f"Solid choice with a score of {scored['total_score']}/1.0. Worth considering based on your priorities."
        
        return strengths, weaknesses, reason
