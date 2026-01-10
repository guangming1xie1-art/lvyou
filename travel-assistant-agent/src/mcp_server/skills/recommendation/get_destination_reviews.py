"""GetDestinationReviewsSkill - Fetch user reviews and ratings for destinations"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill


class GetDestinationReviewsSkill(BaseSkill):
    """Get user reviews and ratings for a destination
    
    This skill provides aggregated reviews, ratings, sentiment analysis,
    and pros/cons summary for destinations.
    """
    
    name = "get_destination_reviews"
    agent_type = "recommendation"
    description = "Get user reviews, ratings, and sentiment analysis for travel destinations"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Name of the destination"
                },
                "category": {
                    "type": "string",
                    "description": "Review category filter",
                    "enum": ["general", "hotels", "attractions", "restaurants", "transportation"],
                    "default": "general"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of reviews to return",
                    "default": 5
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
                "rating_breakdown": {
                    "type": "object",
                    "properties": {
                        "5_star": {"type": "integer"},
                        "4_star": {"type": "integer"},
                        "3_star": {"type": "integer"},
                        "2_star": {"type": "integer"},
                        "1_star": {"type": "integer"}
                    }
                },
                "sentiment_breakdown": {
                    "type": "object",
                    "properties": {
                        "positive": {"type": "number"},
                        "neutral": {"type": "number"},
                        "negative": {"type": "number"}
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
                            "helpful_count": {"type": "integer"},
                            "verified_traveler": {"type": "boolean"}
                        }
                    }
                },
                "pros_cons": {
                    "type": "object",
                    "properties": {
                        "pros": {"type": "array", "items": {"type": "string"}},
                        "cons": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "recommended_by": {"type": "number", "description": "Percentage who recommend"}
            },
            "required": ["destination", "overall_rating", "total_reviews", "reviews"]
        }
    
    async def execute(
        self,
        destination: str,
        category: str = "general",
        limit: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Get destination reviews
        
        Args:
            destination: Destination name
            category: Review category
            limit: Number of reviews
            
        Returns:
            Reviews and ratings data
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")
        
        # Mock review database
        review_data = {
            "tokyo": {
                "overall_rating": 4.6,
                "total_reviews": 12580,
                "rating_breakdown": {"5_star": 7800, "4_star": 3200, "3_star": 1100, "2_star": 350, "1_star": 130},
                "sentiment": {"positive": 0.82, "neutral": 0.13, "negative": 0.05},
                "reviews": [
                    {
                        "author": "Sarah M.",
                        "rating": 5.0,
                        "date": "2024-01-15",
                        "title": "Amazing blend of tradition and modernity",
                        "content": "Tokyo exceeded all expectations! The public transport is incredibly efficient, food is outstanding, and there's so much to see. Loved visiting temples in the morning and exploring vibrant neighborhoods at night.",
                        "helpful_count": 245,
                        "verified_traveler": True
                    },
                    {
                        "author": "James K.",
                        "rating": 5.0,
                        "date": "2024-01-10",
                        "title": "Food paradise!",
                        "content": "If you love food, Tokyo is heaven. From Michelin-starred restaurants to tiny ramen shops, everything was delicious. The Tsukiji market is a must-visit for breakfast.",
                        "helpful_count": 198,
                        "verified_traveler": True
                    },
                    {
                        "author": "Emma L.",
                        "rating": 4.0,
                        "date": "2024-01-05",
                        "title": "Great but expensive",
                        "content": "Tokyo is fantastic but can be pricey. The subway system is confusing at first but you get used to it. Definitely recommend getting a Suica card. Cherry blossoms in spring were breathtaking.",
                        "helpful_count": 167,
                        "verified_traveler": True
                    },
                    {
                        "author": "Michael R.",
                        "rating": 5.0,
                        "date": "2023-12-28",
                        "title": "Clean, safe, and fascinating",
                        "content": "Felt incredibly safe walking around at any time. The city is spotlessly clean and people are respectful. Language barrier was occasionally challenging but people were patient and helpful.",
                        "helpful_count": 143,
                        "verified_traveler": True
                    },
                    {
                        "author": "Lisa W.",
                        "rating": 4.0,
                        "date": "2023-12-20",
                        "title": "Unique experience",
                        "content": "Very different from Western cities. Takes time to adjust to the pace and customs. Amazing shopping and technology. Would recommend staying in Shibuya or Shinjuku for first-timers.",
                        "helpful_count": 89,
                        "verified_traveler": True
                    }
                ],
                "pros": [
                    "Excellent public transportation",
                    "Safe and clean",
                    "Amazing food scene",
                    "Efficient and organized",
                    "Rich culture and history"
                ],
                "cons": [
                    "Can be expensive",
                    "Language barrier",
                    "Crowded during peak times",
                    "Subway system initially confusing"
                ],
                "recommended_by": 92
            },
            "paris": {
                "overall_rating": 4.4,
                "total_reviews": 18230,
                "rating_breakdown": {"5_star": 8900, "4_star": 6200, "3_star": 2100, "2_star": 750, "1_star": 280},
                "sentiment": {"positive": 0.75, "neutral": 0.18, "negative": 0.07},
                "reviews": [
                    {
                        "author": "Sophie B.",
                        "rating": 5.0,
                        "date": "2024-01-12",
                        "title": "The city of dreams",
                        "content": "Paris is magical! The architecture, the art, the food - everything is as beautiful as you imagine. Spent hours at the Louvre and still didn't see everything. Seine river at sunset is unforgettable.",
                        "helpful_count": 312,
                        "verified_traveler": True
                    },
                    {
                        "author": "David P.",
                        "rating": 4.0,
                        "date": "2024-01-08",
                        "title": "Romantic but touristy",
                        "content": "Beautiful city with incredible museums and landmarks. Can be very crowded at major attractions. Metro is convenient but avoid restaurants right near tourist spots - they're overpriced and underwhelming.",
                        "helpful_count": 234,
                        "verified_traveler": True
                    },
                    {
                        "author": "Rachel T.",
                        "rating": 5.0,
                        "date": "2023-12-30",
                        "title": "Art lover's paradise",
                        "content": "As an art enthusiast, Paris was perfect. Musée d'Orsay and Louvre are world-class. Wandering through Montmartre was a highlight. Learning some basic French helped a lot.",
                        "helpful_count": 187,
                        "verified_traveler": True
                    }
                ],
                "pros": [
                    "Stunning architecture",
                    "World-class museums and art",
                    "Excellent cuisine",
                    "Romantic atmosphere",
                    "Good public transportation"
                ],
                "cons": [
                    "Very crowded at tourist spots",
                    "Can be expensive",
                    "Some service staff unfriendly",
                    "Pickpockets in tourist areas"
                ],
                "recommended_by": 87
            },
            "bali": {
                "overall_rating": 4.7,
                "total_reviews": 9450,
                "rating_breakdown": {"5_star": 6200, "4_star": 2400, "3_star": 650, "2_star": 150, "1_star": 50},
                "sentiment": {"positive": 0.88, "neutral": 0.09, "negative": 0.03},
                "reviews": [
                    {
                        "author": "Amanda G.",
                        "rating": 5.0,
                        "date": "2024-01-14",
                        "title": "Paradise found!",
                        "content": "Bali is absolutely stunning! Beautiful beaches, incredible temples, friendly locals, and amazing food. Rice terraces in Ubud are breathtaking. Yoga and wellness culture is wonderful.",
                        "helpful_count": 298,
                        "verified_traveler": True
                    },
                    {
                        "author": "Chris H.",
                        "rating": 5.0,
                        "date": "2024-01-09",
                        "title": "Perfect for digital nomads",
                        "content": "Spent a month in Canggu and loved it. Great wifi, coworking spaces, and social scene. Cost of living is reasonable. Rented a scooter which gave us freedom to explore.",
                        "helpful_count": 267,
                        "verified_traveler": True
                    },
                    {
                        "author": "Jennifer L.",
                        "rating": 4.0,
                        "date": "2024-01-02",
                        "title": "Beautiful but touristy in spots",
                        "content": "Some areas like Seminyak are very developed and touristy. Head to Amed or Sidemen for more authentic experiences. The Mount Batur sunrise trek was a highlight!",
                        "helpful_count": 154,
                        "verified_traveler": True
                    }
                ],
                "pros": [
                    "Beautiful natural scenery",
                    "Affordable",
                    "Friendly locals",
                    "Great yoga and wellness",
                    "Delicious food"
                ],
                "cons": [
                    "Traffic can be bad",
                    "Some areas overdeveloped",
                    "Monsoon season very rainy",
                    "Scooter riding can be dangerous"
                ],
                "recommended_by": 94
            }
        }
        
        # Get reviews for destination
        dest_lower = destination.lower().strip()
        data = review_data.get(dest_lower)
        
        if not data:
            # Try partial match
            for key, value in review_data.items():
                if dest_lower in key or key in dest_lower:
                    data = value
                    break
        
        if not data:
            # Default data
            data = {
                "overall_rating": 4.0,
                "total_reviews": 500,
                "rating_breakdown": {"5_star": 200, "4_star": 180, "3_star": 80, "2_star": 30, "1_star": 10},
                "sentiment": {"positive": 0.72, "neutral": 0.20, "negative": 0.08},
                "reviews": [
                    {
                        "author": "Traveler",
                        "rating": 4.0,
                        "date": "2024-01-01",
                        "title": "Great destination",
                        "content": f"{destination} is a wonderful place to visit with lots to see and do.",
                        "helpful_count": 50,
                        "verified_traveler": True
                    }
                ],
                "pros": ["Interesting sights", "Good local food", "Friendly people"],
                "cons": ["Limited information available"],
                "recommended_by": 80
            }
        
        # Limit reviews
        reviews = data["reviews"][:limit]
        
        return {
            "destination": destination,
            "overall_rating": data["overall_rating"],
            "total_reviews": data["total_reviews"],
            "rating_breakdown": data["rating_breakdown"],
            "sentiment_breakdown": data["sentiment"],
            "reviews": reviews,
            "pros_cons": {
                "pros": data["pros"],
                "cons": data["cons"]
            },
            "recommended_by": data["recommended_by"]
        }
