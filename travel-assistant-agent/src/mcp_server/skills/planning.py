"""CreateTravelPlanSkill - Generate comprehensive travel plans"""

from typing import Any, Dict, List
from .base_skill import BaseSkill


class CreateTravelPlanSkill(BaseSkill):
    """Skill for creating comprehensive travel plans based on gathered information"""
    
    name = "create_travel_plan"
    description = "Create a detailed travel itinerary based on destination, budget, and preferences"
    category = "planning"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Travel destination"
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Number of days for the trip",
                    "default": 5
                },
                "budget": {
                    "type": "number",
                    "description": "Total budget in USD"
                },
                "travel_dates": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"}
                    }
                },
                "interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Traveler interests and preferences"
                },
                "accommodation_type": {
                    "type": "string",
                    "description": "Preferred accommodation style",
                    "default": "mid-range"
                },
                "pace": {
                    "type": "string",
                    "description": "Travel pace (relaxed, moderate, packed)",
                    "default": "moderate"
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
                "title": {"type": "string"},
                "overview": {"type": "string"},
                "itinerary": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day": {"type": "integer"},
                            "date": {"type": "string"},
                            "theme": {"type": "string"},
                            "activities": {"type": "array", "items": {"type": "string"}},
                            "meals": {"type": "array", "items": {"type": "string"}},
                            "accommodation": {"type": "string"},
                            "transport": {"type": "string"}
                        }
                    }
                },
                "budget_breakdown": {
                    "type": "object",
                    "properties": {
                        "flights": {"type": "number"},
                        "accommodation": {"type": "number"},
                        "food": {"type": "number"},
                        "activities": {"type": "number"},
                        "transport": {"type": "number"},
                        "buffer": {"type": "number"},
                        "total": {"type": "number"}
                    }
                },
                "packing_list": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "tips": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "booking_recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["destination"]
        }
    
    async def execute(
        self,
        destination: str,
        duration_days: int = 5,
        budget: float = None,
        travel_dates: Dict = None,
        interests: List[str] = None,
        accommodation_type: str = "mid-range",
        pace: str = "moderate"
    ) -> Dict[str, Any]:
        """Execute travel plan creation with mock data"""
        
        interests = interests or []
        
        # Sample itineraries based on destination
        itineraries = {
            "tokyo": {
                "title": "Tokyo Adventure",
                "theme": "Modern meets Traditional",
                "overview": "Experience the perfect blend of cutting-edge technology and ancient traditions in Japan's vibrant capital.",
                "activities_by_day": [
                    {
                        "day": 1,
                        "theme": "Arrival & Traditional Tokyo",
                        "activities": ["Arrive at Narita/Haneda Airport", "Check in at hotel in Shinjuku", "Explore Shibuya Crossing", "Dinner at local izakaya"],
                        "meals": ["Breakfast on flight", "Lunch at Shibuya cafe", "Dinner at izakaya"]
                    },
                    {
                        "day": 2,
                        "theme": "Ancient Temples & Culture",
                        "activities": ["Senso-ji Temple visit", "Nakamise shopping street", "Asakusa traditional district", "Sumida River cruise"],
                        "meals": ["Hotel breakfast", "Lunch at traditional restaurant", "Dinner at riverside restaurant"]
                    },
                    {
                        "day": 3,
                        "theme": "Modern Attractions",
                        "activities": ["Tokyo Skytree", "Akihabara electronic district", "TeamLab Planets digital museum", "Evening at Tokyo Tower"],
                        "meals": ["Hotel breakfast", "Lunch in Akihabara", "Dinner at Roppongi Hills"]
                    },
                    {
                        "day": 4,
                        "theme": "Day Trip & Parks",
                        "activities": ["Day trip to Mt. Fuji (optional)", "Shinjuku Gyoen garden", "Harajuku fashion street", "Takeshita Street exploration"],
                        "meals": ["Hotel breakfast", "Lunch in Harajuku", "Farewell dinner at tempura restaurant"]
                    },
                    {
                        "day": 5,
                        "theme": "Departure",
                        "activities": ["Last minute shopping", "Visit Imperial Palace gardens", "Head to airport"],
                        "meals": ["Hotel breakfast", "Lunch near palace", "Snacks for flight"]
                    }
                ],
                "packing": [
                    "Comfortable walking shoes",
                    "Suica/Pasmo card for transport",
                    "Portable WiFi or SIM",
                    "Power adapter (Type A/B)",
                    "Light rain jacket",
                    "Cash (many places don't accept cards)"
                ],
                "tips": [
                    "Get an IC card (Suica/Pasmo/ICOCA) for easy transport",
                    "Download Google Maps offline",
                    "JR Pass may be worth it for day trips",
                    "Peak hours on metro are very crowded",
                    "Most museums closed on Mondays"
                ],
                "booking_recommendations": [
                    "Book Shinkansen tickets in advance for day trips",
                    "Make restaurant reservations for fine dining",
                    "Consider hotel with breakfast included",
                    "Book TeamLab tickets online to skip lines"
                ]
            },
            "paris": {
                "title": "Paris Romance",
                "theme": "City of Lights",
                "overview": "Discover the magic of Paris - from iconic landmarks to hidden gems in charming neighborhoods.",
                "activities_by_day": [
                    {
                        "day": 1,
                        "theme": "Iconic First Impressions",
                        "activities": ["Arrive at Charles de Gaulle Airport", "Check in at hotel near Marais", "Eiffel Tower visit", "Seine River cruise at sunset"],
                        "meals": ["Lunch at Latin Quarter", "Dinner near Eiffel Tower"]
                    },
                    {
                        "day": 2,
                        "theme": "Art & Culture",
                        "activities": ["Louvre Museum (arrive early)", "Tuileries Garden", "Musée d'Orsay", "Montmartre sunset"],
                        "meals": ["Café au lait and croissant", "Lunch in Saint-Germain", "Dinner in Montmartre"]
                    },
                    {
                        "day": 3,
                        "theme": "Historic Paris",
                        "activities": ["Notre-Dame Cathedral", "Pont Neuf", "Conciergerie", "Latin Quarter exploration", "Luxembourg Gardens"],
                        "meals": ["Market picnic in the Marais", "Classic French dinner"]
                    },
                    {
                        "day": 4,
                        "theme": "Palaces & Gardens",
                        "activities": ["Versailles Day Trip", "Palace of Versailles", " Gardens and Trianon", "Return via train"],
                        "meals": ["Picnic in Versailles gardens", "Dinner in local neighborhood"]
                    },
                    {
                        "day": 5,
                        "theme": "Shopping & Departure",
                        "activities": ["Champs-Élysées shopping", "Arc de Triomphe", "Le Marais boutiques", "Head to airport"],
                        "meals": ["Final French breakfast", "Lunch in Le Marais"]
                    }
                ],
                "packing": [
                    "Elegant casual clothes for dining",
                    "Comfortable walking shoes (cobblestones!)",
                    "Light rain jacket",
                    "Power adapter (Type E)",
                    "Museum pass (if visiting many sites)"
                ],
                "tips": [
                    "Book museum tickets online to avoid lines",
                    "Museum pass includes Palace of Versailles",
                    "Avoid restaurants on main boulevards",
                    "Learn basic French phrases",
                    "Be aware of pickpockets near tourist sites"
                ],
                "booking_recommendations": [
                    "Book Louvre tickets for specific time slot",
                    "Make dinner reservations for famous restaurants",
                    "Consider Paris Museum Pass for savings",
                    "Book Seine cruise in advance for sunset"
                ]
            },
            "bali": {
                "title": "Bali Bliss",
                "theme": "Island Paradise",
                "overview": "Experience the perfect balance of beach relaxation, cultural exploration, and wellness in the Island of the Gods.",
                "activities_by_day": [
                    {
                        "day": 1,
                        "theme": "Arrival & Beach",
                        "activities": ["Arrive at Ngurah Rai Airport", "Transfer to Seminyak hotel", "Beach relaxation", "Beach club sunset dinner"],
                        "meals": ["Lunch on arrival", "Dinner at beach club"]
                    },
                    {
                        "day": 2,
                        "theme": "Cultural Immersion",
                        "activities": ["Uluwatu Temple visit", "Kecak dance performance", "Jimbaran Beach dinner", "Spa treatment"],
                        "meals": ["Hotel breakfast", "Lunch at clifftop cafe", "Seafood dinner at Jimbaran"]
                    },
                    {
                        "day": 3,
                        "theme": "Ubud Wellness",
                        "activities": ["Transfer to Ubud", "Rice terrace trek", "Traditional cooking class", "Evening yoga session"],
                        "meals": ["Hotel breakfast", "Lunch at warung", "Own healthy dinner"]
                    },
                    {
                        "day": 4,
                        "theme": "Nature & Temples",
                        "activities": ["Sacred Monkey Forest", "Tegallalang Rice Terraces", "Local temple visit", "Balinese massage"],
                        "meals": ["Hotel breakfast", "Lunch with rice terrace view", "Dinner in Ubud market"]
                    },
                    {
                        "day": 5,
                        "theme": "Departure",
                        "activities": ["Morning beach time", "Spa treatment", "Head to airport"],
                        "meals": ["Hotel breakfast", "Lunch before departure"]
                    }
                ],
                "packing": [
                    "Swimwear and beachwear",
                    "Modest clothing for temples",
                    "Sunscreen (high SPF)",
                    "Insect repellent",
                    "Yoga clothes (if interested)",
                    "Reef-safe sunscreen for ocean"
                ],
                "tips": [
                    "Bargain at markets but stay friendly",
                    "Hire a scooter for flexibility",
                    "Book activities through reputable sources",
                    "Respect local customs at temples",
                    "Try the local coffee (Kopi Luwak!)"
                ],
                "booking_recommendations": [
                    "Book cooking class in advance",
                    "Reserve Uluwatu temple sunset spot",
                    "Book beach club day passes early",
                    "Consider villa with private pool"
                ]
            }
        }
        
        dest_lower = destination.lower().strip()
        plan = itineraries.get(dest_lower, {
            "title": f"Explore {destination}",
            "theme": "Adventure Awaits",
            "overview": f"Discover the wonders of {destination} with this curated itinerary.",
            "activities_by_day": [
                {
                    "day": 1,
                    "theme": "Arrival",
                    "activities": ["Arrive at destination", "Check in at hotel", "Local exploration"],
                    "meals": ["Lunch on arrival", "Dinner at local restaurant"]
                },
                {
                    "day": 2,
                    "theme": "Main Attractions",
                    "activities": ["Visit top attractions", "Local market exploration", "Cultural sites"],
                    "meals": ["Hotel breakfast", "Lunch in town", "Dinner at local spot"]
                }
            ],
            "packing": [
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Camera",
                "Portable charger"
            ],
            "tips": [
                "Research local customs before visiting",
                "Learn basic local phrases",
                "Stay aware of surroundings"
            ],
            "booking_recommendations": [
                "Book popular attractions in advance",
                "Make restaurant reservations for popular spots"
            ]
        })
        
        # Generate itinerary for requested duration
        days_needed = min(duration_days, len(plan["activities_by_day"]))
        full_itinerary = []
        
        for i in range(days_needed):
            day_plan = plan["activities_by_day"][i].copy()
            day_plan["day"] = i + 1
            day_plan["date"] = f"Day {i + 1}"
            full_itinerary.append(day_plan)
        
        # Calculate budget breakdown
        if budget:
            budget_percents = {
                "flights": 0.30,
                "accommodation": 0.25,
                "food": 0.20,
                "activities": 0.15,
                "transport": 0.05,
                "buffer": 0.05
            }
            
            budget_breakdown = {
                "flights": round(budget * budget_percents["flights"], 2),
                "accommodation": round(budget * budget_percents["accommodation"], 2),
                "food": round(budget * budget_percents["food"], 2),
                "activities": round(budget * budget_percents["activities"], 2),
                "transport": round(budget * budget_percents["transport"], 2),
                "buffer": round(budget * budget_percents["buffer"], 2),
                "total": budget
            }
        else:
            budget_breakdown = {
                "flights": 0,
                "accommodation": 0,
                "food": 0,
                "activities": 0,
                "transport": 0,
                "buffer": 0,
                "total": 0
            }
        
        return {
            "destination": destination,
            "title": plan["title"],
            "overview": plan["overview"],
            "itinerary": full_itinerary,
            "budget_breakdown": budget_breakdown,
            "packing_list": plan["packing"],
            "tips": plan["tips"],
            "booking_recommendations": plan["booking_recommendations"]
        }
