"""Recommendation Skills - Skills for RecommendationAgent

These skills provide destination insights, attractions, weather, and reviews.
"""

from .get_destination_info import GetDestinationInfoSkill
from .get_attractions import GetAttractionsSkill
from .get_weather_forecast import GetWeatherForecastSkill
from .get_destination_reviews import GetDestinationReviewsSkill

__all__ = [
    "GetDestinationInfoSkill",
    "GetAttractionsSkill",
    "GetWeatherForecastSkill",
    "GetDestinationReviewsSkill",
]
