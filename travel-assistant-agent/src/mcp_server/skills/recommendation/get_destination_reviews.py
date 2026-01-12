"""GetDestinationReviewsSkill - Fetch user reviews and ratings for destinations"""

from typing import Any, Dict, List
from ..base_skill import BaseSkill
from src.utils.java_api_client import java_api_client, JavaAPIError
from src.utils.logger import app_logger


class GetDestinationReviewsSkill(BaseSkill):
    """Get user reviews and ratings for a destination

    This skill provides aggregated reviews, ratings, sentiment analysis,
    and pros/cons summary for destinations.

    Version 2.0.0: Refactored to call Java API instead of local mock implementation.
    """

    name = "get_destination_reviews"
    agent_type = "recommendation"
    description = "Get user reviews, ratings, and sentiment analysis for travel destinations"
    version = "2.0.0"

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
        """Get destination reviews by calling Java API

        Args:
            destination: Destination name
            category: Review category (general, hotels, attractions, restaurants, transportation)
            limit: Number of reviews to return

        Returns:
            Reviews and ratings data
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")

        app_logger.info(f"GetDestinationReviewsSkill: Fetching reviews for {destination} (category: {category})")

        try:
            # Call Java API to get destination reviews
            result = await java_api_client.get_destination_reviews(
                destination=destination,
                page=1,
                page_size=limit,
                sort_by="rating_high"
            )

            reviews = result.get("reviews", [])
            pagination = result.get("pagination", {})

            app_logger.info(f"GetDestinationReviewsSkill: Found {len(reviews)} reviews for {destination}")

            # Transform Java API response to match skill output schema
            # JavaAPIClient returns: reviews, pagination, average_rating, rating_distribution
            # Skill output schema expects: reviews, rating_breakdown, sentiment_breakdown, pros_cons, recommended_by

            # Build rating breakdown from distribution
            rating_dist = result.get("rating_distribution", {})
            rating_breakdown = {
                "5_star": rating_dist.get(5, 0),
                "4_star": rating_dist.get(4, 0),
                "3_star": rating_dist.get(3, 0),
                "2_star": rating_dist.get(2, 0),
                "1_star": rating_dist.get(1, 0)
            }

            # Build sentiment breakdown from reviews (simple version)
            positive_count = sum(1 for r in reviews if r.get("rating", 0) >= 4)
            neutral_count = sum(1 for r in reviews if r.get("rating", 0) == 3)
            negative_count = sum(1 for r in reviews if r.get("rating", 0) <= 2)
            total_reviews_count = len(reviews) if reviews else 1

            sentiment_breakdown = {
                "positive": round(positive_count / total_reviews_count, 2),
                "neutral": round(neutral_count / total_reviews_count, 2),
                "negative": round(negative_count / total_reviews_count, 2)
            }

            # Extract pros and cons from review content (simple version)
            pros = []
            cons = []
            for review in reviews[:limit]:
                content = review.get("content", "").lower()
                rating = review.get("rating", 0)
                if rating >= 4:
                    # High-rated reviews contribute to pros
                    if "good" in content:
                        pros.append("Good experience")
                    if "great" in content:
                        pros.append("Great destination")
                    if "beautiful" in content:
                        pros.append("Beautiful scenery")
                elif rating <= 2:
                    # Low-rated reviews contribute to cons
                    if "expensive" in content:
                        cons.append("Can be expensive")
                    if "crowded" in content:
                        cons.append("Crowded areas")
                    if "poor" in content:
                        cons.append("Poor service")

            # Remove duplicates
            pros = list(set(pros))
            cons = list(set(cons))

            # Calculate recommendation percentage from rating breakdown
            total_reviews = sum(rating_breakdown.values())
            high_ratings = rating_breakdown["5_star"] + rating_breakdown["4_star"]
            recommended_by = round((high_ratings / total_reviews * 100), 0) if total_reviews > 0 else 0

            # Transform reviews to match skill output schema
            transformed_reviews = []
            for review in reviews[:limit]:
                transformed = {
                    "author": review.get("author", "Anonymous"),
                    "rating": review.get("rating", 0.0),
                    "date": review.get("date", ""),
                    "title": review.get("title", ""),
                    "content": review.get("content", ""),
                    "helpful_count": review.get("helpful_count", 0),
                    "verified_traveler": review.get("verified_traveler", True)
                }
                transformed_reviews.append(transformed)

            return {
                "destination": destination,
                "overall_rating": result.get("average_rating", 0.0),
                "total_reviews": pagination.get("total_count", total_reviews),
                "rating_breakdown": rating_breakdown,
                "sentiment_breakdown": sentiment_breakdown,
                "reviews": transformed_reviews,
                "pros_cons": {
                    "pros": pros if pros else ["Good location", "Interesting attractions"],
                    "cons": cons if cons else ["No major issues reported"]
                },
                "recommended_by": recommended_by
            }

        except JavaAPIError as e:
            app_logger.error(f"GetDestinationReviewsSkill: Java API error - {e}")
            return {
                "destination": destination,
                "overall_rating": 0.0,
                "total_reviews": 0,
                "rating_breakdown": {"5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0},
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "reviews": [],
                "pros_cons": {
                    "pros": [],
                    "cons": []
                },
                "recommended_by": 0,
                "error": {
                    "code": "JAVA_API_ERROR",
                    "message": str(e),
                    "status_code": getattr(e, "status_code", None)
                }
            }
        except Exception as e:
            app_logger.error(f"GetDestinationReviewsSkill: Unexpected error - {e}")
            return {
                "destination": destination,
                "overall_rating": 0.0,
                "total_reviews": 0,
                "rating_breakdown": {"5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0},
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "reviews": [],
                "pros_cons": {
                    "pros": [],
                    "cons": []
                },
                "recommended_by": 0,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
