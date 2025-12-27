"""GetDestinationReviewsSkill - Fetch user reviews and ratings"""

from typing import Any, Dict, List
from .base_skill import BaseSkill


class GetDestinationReviewsSkill(BaseSkill):
    """Skill for fetching destination reviews and ratings"""
    
    name = "get_destination_reviews"
    description = "Get user reviews, ratings, and sentiment analysis for travel destinations"
    category = "reviews"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Name of the destination to get reviews for"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (hotels, attractions, restaurants, general)",
                    "default": "general"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of reviews to return",
                    "default": 5
                },
                "include_sentiment": {
                    "type": "boolean",
                    "description": "Include sentiment analysis",
                    "default": True
                }
            },
            "required": ["destination"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "overall_rating": {"type": "number"},
                "total_reviews": {"type": "integer"},
                "sentiment_breakdown": {
                    "type": "object",
                    "properties": {
                        "positive": {"type": "number"},
                        "neutral": {"type": "number"},
                        "negative": {"type": "number"}
                    }
                },
                "rating_breakdown": {
                    "type": "object",
                    "properties": {
                        "5_star": {"type": "number"},
                        "4_star": {"type": "number"},
                        "3_star": {"type": "number"},
                        "2_star": {"type": "number"},
                        "1_star": {"type": "number"}
                    }
                },
                "reviews": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "author": {"type": "string"},
                            "rating": {"type": "number"},
                            "date": {"type": "string"},
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "sentiment": {"type": "string"}
                        }
                    }
                },
                "pros_cons": {
                    "type": "object",
                    "properties": {
                        "pros": {"type": "array", "items": {"type": "string"}},
                        "cons": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["destination"]
        }
    
    async def execute(
        self,
        destination: str,
        category: str = "general",
        limit: int = 5,
        include_sentiment: bool = True
    ) -> Dict[str, Any]:
        """Execute review fetch with mock data"""
        
        # Mock review data
        review_data = {
            "tokyo": {
                "overall_rating": 4.7,
                "total_reviews": 15420,
                "sentiment_breakdown": {"positive": 85, "neutral": 12, "negative": 3},
                "rating_breakdown": {"5_star": 60, "4_star": 25, "3_star": 10, "2_star": 3, "1_star": 2},
                "reviews": [
                    {
                        "author": "Traveler_123",
                        "rating": 5,
                        "date": "2024-03-15",
                        "title": "Amazing blend of old and new!",
                        "content": "Tokyo exceeded all expectations. The food, the people, the technology - everything was incredible. Shibuya Crossing is a must-see!",
                        "sentiment": "positive"
                    },
                    {
                        "author": "WorldExplorer",
                        "rating": 5,
                        "date": "2024-03-10",
                        "title": "Clean, safe, and fascinating",
                        "content": "First time in Japan and I was blown away by how clean and safe everything felt. The metro system takes getting used to but works great.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "BudgetBackpacker",
                        "rating": 4,
                        "date": "2024-02-28",
                        "title": "Expensive but worth it",
                        "content": "Tokyo is pricey but you get what you pay for. Great value for money overall. Accommodations can be small but functional.",
                        "sentiment": "neutral"
                    },
                    {
                        "author": "CultureSeeker",
                        "rating": 5,
                        "date": "2024-02-20",
                        "title": "Temple hopping was incredible",
                        "content": "Senso-ji and Meiji Shrine were highlights. The traditional districts like Asakusa preserve so much history.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "FirstTimeAsia",
                        "rating": 4,
                        "date": "2024-02-15",
                        "title": "Language barrier but manageable",
                        "content": "Not much English spoken outside tourist areas but translation apps helped a lot. Locals are very helpful once you communicate.",
                        "sentiment": "neutral"
                    }
                ],
                "pros_cons": {
                    "pros": [
                        "Excellent public transportation",
                        "Incredible food scene",
                        "Safety and cleanliness",
                        "Rich culture and history",
                        "Cutting-edge technology"
                    ],
                    "cons": [
                        "Can be expensive",
                        "Language barrier outside tourist areas",
                        "Crowded during peak seasons",
                        "Accommodations can be small"
                    ]
                }
            },
            "paris": {
                "overall_rating": 4.5,
                "total_reviews": 28340,
                "sentiment_breakdown": {"positive": 78, "neutral": 15, "negative": 7},
                "rating_breakdown": {"5_star": 50, "4_star": 28, "3_star": 15, "2_star": 5, "1_star": 2},
                "reviews": [
                    {
                        "author": "RomanticDreamer",
                        "rating": 5,
                        "date": "2024-03-14",
                        "title": "City of Romance indeed!",
                        "content": "Paris is magical. The Eiffel Tower at night, Seine river walk, cozy cafes - perfect for couples.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "ArtLover",
                        "rating": 5,
                        "date": "2024-03-08",
                        "title": "Louvre is a must",
                        "content": "Spent 3 days exploring museums. The Louvre, Musée d'Orsay, and Orangerie are world-class.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "PracticalTraveler",
                        "rating": 3,
                        "date": "2024-02-25",
                        "title": "Beautiful but touristy",
                        "content": "Many areas feel overly tourist-focused. Step away from main attractions to find authentic Paris.",
                        "sentiment": "neutral"
                    },
                    {
                        "author": "FoodieExplorer",
                        "rating": 4,
                        "date": "2024-02-18",
                        "title": "Great food but need local tips",
                        "content": "Amazing cuisine but avoid restaurants on main boulevards. Le Marais has fantastic hidden gems.",
                        "sentiment": "neutral"
                    }
                ],
                "pros_cons": {
                    "pros": [
                        "World-class museums and art",
                        "Beautiful architecture",
                        "Amazing cuisine and wine",
                        "Romantic atmosphere",
                        "Great shopping"
                    ],
                    "cons": [
                        "Can be crowded with tourists",
                        "Some areas can be pricey",
                        "Language barrier with staff",
                        "Pickpocketing in tourist areas"
                    ]
                }
            },
            "bali": {
                "overall_rating": 4.6,
                "total_reviews": 12780,
                "sentiment_breakdown": {"positive": 82, "neutral": 14, "negative": 4},
                "rating_breakdown": {"5_star": 55, "4_star": 27, "3_star": 12, "2_star": 4, "1_star": 2},
                "reviews": [
                    {
                        "author": "BeachLover",
                        "rating": 5,
                        "date": "2024-03-12",
                        "title": "Tropical paradise!",
                        "content": "Uluwatu cliffs, beaches in Canggu, rice terraces in Ubud - Bali has it all. The spirituality of Ubud touched my soul.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "YogaEnthusiast",
                        "rating": 5,
                        "date": "2024-03-05",
                        "title": "Perfect for wellness retreats",
                        "content": "Did a week-long yoga retreat. The energy of this place is special. Healthy food options everywhere.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "BudgetTraveler",
                        "rating": 4,
                        "date": "2024-02-22",
                        "title": "Great value for money",
                        "content": "Amazing how far your dollar goes here. Great accommodations and food at reasonable prices.",
                        "sentiment": "positive"
                    },
                    {
                        "author": "LuxurySeeker",
                        "rating": 4,
                        "date": "2024-02-15",
                        "title": "Great villas and resorts",
                        "content": "Stayed in a private villa with pool. Excellent service and beautiful surroundings. Highly recommend Seminyak.",
                        "sentiment": "positive"
                    }
                ],
                "pros_cons": {
                    "pros": [
                        "Beautiful beaches",
                        "Affordable luxury",
                        "Rich spiritual culture",
                        "Great surfing spots",
                        "Friendly locals"
                    ],
                    "cons": [
                        "Monkey Forest can be tricky",
                        "Traffic in main areas",
                        "Some areas overly developed",
                        "Bargaining culture takes getting used to"
                    ]
                }
            }
        }
        
        dest_lower = destination.lower().strip()
        result = review_data.get(dest_lower)
        
        if not result:
            # Generate generic result
            result = {
                "overall_rating": 4.0,
                "total_reviews": 500,
                "sentiment_breakdown": {"positive": 70, "neutral": 20, "negative": 10},
                "rating_breakdown": {"5_star": 40, "4_star": 30, "3_star": 20, "2_star": 7, "1_star": 3},
                "reviews": [
                    {
                        "author": "Traveler",
                        "rating": 4,
                        "date": "2024-03-01",
                        "title": "Good destination",
                        "content": "Had a pleasant experience. Would recommend to friends.",
                        "sentiment": "positive"
                    }
                ],
                "pros_cons": {
                    "pros": ["Interesting attractions", "Good food", "Friendly people"],
                    "cons": ["Some areas need improvement", "Can be crowded"]
                }
            }
        
        # Limit reviews
        result["reviews"] = result["reviews"][:limit]
        
        if not include_sentiment:
            for review in result["reviews"]:
                review.pop("sentiment", None)
        
        return result
