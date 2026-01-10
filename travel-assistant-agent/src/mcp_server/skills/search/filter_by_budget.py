"""FilterByBudgetSkill - Filter search results within budget constraints"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class FilterByBudgetSkill(BaseSkill):
    """Filter options to fit within budget
    
    This skill filters flight, hotel, or combined search results to only
    show options that fit within the user's specified budget.
    """
    
    name = "filter_by_budget"
    agent_type = "search"
    description = "Filter search results to fit within specified budget constraints"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "description": "Array of options to filter (flights, hotels, etc.)",
                    "items": {"type": "object"}
                },
                "budget": {
                    "type": "object",
                    "description": "Budget constraints",
                    "properties": {
                        "max_total": {"type": "number", "description": "Maximum total budget"},
                        "max_per_person": {"type": "number", "description": "Maximum per person"},
                        "currency": {"type": "string", "default": "USD"}
                    }
                },
                "option_type": {
                    "type": "string",
                    "description": "Type of options being filtered",
                    "enum": ["flights", "hotels", "activities", "combined"]
                },
                "sort_by": {
                    "type": "string",
                    "description": "How to sort filtered results",
                    "enum": ["price_low_to_high", "price_high_to_low", "best_value"],
                    "default": "price_low_to_high"
                }
            },
            "required": ["options", "budget", "option_type"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filtered_options": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Options within budget"
                },
                "excluded_options": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Options excluded due to budget"
                },
                "budget_summary": {
                    "type": "object",
                    "properties": {
                        "total_budget": {"type": "number"},
                        "cheapest_option": {"type": "number"},
                        "most_expensive_option": {"type": "number"},
                        "average_price": {"type": "number"},
                        "options_within_budget": {"type": "integer"},
                        "options_over_budget": {"type": "integer"},
                        "savings_potential": {"type": "number"}
                    }
                }
            },
            "required": ["filtered_options", "budget_summary"]
        }
    
    async def execute(
        self,
        options: List[Dict[str, Any]],
        budget: Dict[str, Any],
        option_type: str,
        sort_by: str = "price_low_to_high",
        **kwargs
    ) -> Dict[str, Any]:
        """Filter options by budget
        
        Args:
            options: List of options to filter
            budget: Budget constraints
            option_type: Type of options
            sort_by: Sorting method
            
        Returns:
            Filtered options and budget analysis
        """
        if not self.validate_input({
            "options": options,
            "budget": budget,
            "option_type": option_type
        }):
            raise ValueError("Invalid input: options, budget, and option_type are required")
        
        if not options:
            return {
                "filtered_options": [],
                "excluded_options": [],
                "budget_summary": {
                    "total_budget": budget.get("max_total", 0),
                    "cheapest_option": 0,
                    "most_expensive_option": 0,
                    "average_price": 0,
                    "options_within_budget": 0,
                    "options_over_budget": 0,
                    "savings_potential": 0
                }
            }
        
        max_budget = budget.get("max_total") or budget.get("max_per_person", float('inf'))
        
        # Extract prices and filter
        filtered_options = []
        excluded_options = []
        all_prices = []
        
        for option in options:
            price = self._extract_price(option, option_type)
            all_prices.append(price)
            
            if price <= max_budget:
                # Add price comparison info
                option_with_info = option.copy()
                option_with_info["_budget_info"] = {
                    "price": price,
                    "within_budget": True,
                    "budget_utilization": round((price / max_budget) * 100, 1) if max_budget > 0 else 0,
                    "savings": round(max_budget - price, 2)
                }
                filtered_options.append(option_with_info)
            else:
                option_with_info = option.copy()
                option_with_info["_budget_info"] = {
                    "price": price,
                    "within_budget": False,
                    "over_budget_by": round(price - max_budget, 2)
                }
                excluded_options.append(option_with_info)
        
        # Sort filtered options
        filtered_options = self._sort_options(filtered_options, sort_by, option_type)
        
        # Calculate budget summary
        within_budget_prices = [opt["_budget_info"]["price"] for opt in filtered_options]
        
        budget_summary = {
            "total_budget": max_budget,
            "cheapest_option": min(all_prices) if all_prices else 0,
            "most_expensive_option": max(all_prices) if all_prices else 0,
            "average_price": round(sum(all_prices) / len(all_prices), 2) if all_prices else 0,
            "options_within_budget": len(filtered_options),
            "options_over_budget": len(excluded_options),
            "savings_potential": round(max_budget - min(within_budget_prices), 2) if within_budget_prices else 0
        }
        
        return {
            "filtered_options": filtered_options,
            "excluded_options": excluded_options,
            "budget_summary": budget_summary
        }
    
    def _extract_price(self, option: Dict[str, Any], option_type: str) -> float:
        """Extract price from an option based on its type"""
        if option_type == "flights":
            return option.get("total_price") or option.get("price_per_person", 0)
        elif option_type == "hotels":
            return option.get("total_price") or option.get("price_per_night", 0)
        elif option_type == "activities":
            return option.get("price") or option.get("cost", 0)
        else:  # combined
            return option.get("total_price") or option.get("price", 0)
    
    def _sort_options(
        self, options: List[Dict[str, Any]], sort_by: str, option_type: str
    ) -> List[Dict[str, Any]]:
        """Sort options based on criteria"""
        if sort_by == "price_low_to_high":
            return sorted(options, key=lambda x: x["_budget_info"]["price"])
        elif sort_by == "price_high_to_low":
            return sorted(options, key=lambda x: x["_budget_info"]["price"], reverse=True)
        elif sort_by == "best_value":
            # Best value = highest quality at lowest price
            # For flights: fewer stops, shorter duration
            # For hotels: higher rating
            if option_type == "flights":
                return sorted(
                    options,
                    key=lambda x: (
                        x["_budget_info"]["price"] * (1 + x.get("stops", 0) * 0.2),
                        x.get("duration_minutes", 300)
                    )
                )
            elif option_type == "hotels":
                return sorted(
                    options,
                    key=lambda x: (
                        x["_budget_info"]["price"] / max(x.get("rating", 3), 1),
                        -x.get("review_score", 7.0)
                    )
                )
            else:
                return sorted(options, key=lambda x: x["_budget_info"]["price"])
        
        return options
