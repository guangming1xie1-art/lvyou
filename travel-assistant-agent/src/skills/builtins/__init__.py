"""
Built-in Agent Skills

This package contains built-in agent skills for the Travel Assistant.
"""

from .search_skills import (
    SearchDestinationSkill,
    SearchFlightSkill,
    SearchHotelSkill,
)

from .recommend_skills import (
    RecommendFlightSkill,
    RecommendHotelSkill,
)

from .booking_skills import (
    BookFlightSkill,
    BookHotelSkill,
)

__all__ = [
    # Search Skills
    "SearchDestinationSkill",
    "SearchFlightSkill",
    "SearchHotelSkill",
    
    # Recommend Skills
    "RecommendFlightSkill",
    "RecommendHotelSkill",
    
    # Booking Skills
    "BookFlightSkill",
    "BookHotelSkill",
]
