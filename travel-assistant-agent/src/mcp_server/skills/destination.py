"""SearchDestinationSkill - Search and get destination information"""

from typing import Any, Dict, List
from .base_skill import BaseSkill


class SearchDestinationSkill(BaseSkill):
    """Skill for searching and retrieving destination information"""
    
    name = "search_destination"
    description = "Search for travel destination information including attractions, culture, best time to visit, and local tips"
    category = "destination"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Name of the destination (city, country, or region)"
                },
                "language": {
                    "type": "string",
                    "description": "Preferred language for information (default: en)",
                    "default": "en"
                },
                "include_tips": {
                    "type": "boolean",
                    "description": "Include travel tips and recommendations",
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
                "country": {"type": "string"},
                "region": {"type": "string"},
                "description": {"type": "string"},
                "highlights": {"type": "array", "items": {"type": "string"}},
                "best_time_to_visit": {"type": "string"},
                "average_duration": {"type": "string"},
                "local_tips": {"type": "array", "items": {"type": "string"}},
                "currency": {"type": "string"},
                "language": {"type": "string"},
                "visa_info": {"type": "string"}
            },
            "required": ["destination"]
        }
    
    async def execute(self, destination: str, language: str = "en", include_tips: bool = True) -> Dict[str, Any]:
        """Execute destination search with mock data"""
        # Mock data for demo purposes
        mock_destinations = {
            "tokyo": {
                "destination": "Tokyo",
                "country": "Japan",
                "region": "Asia",
                "description": "Tokyo is a vibrant metropolis blending ultramodern and traditional culture. Experience cutting-edge technology alongside ancient temples.",
                "highlights": [
                    "Senso-ji Temple in Asakusa",
                    "Shibuya Crossing",
                    "Tokyo Tower and Skytree",
                    "Imperial Palace",
                    "Tsukiji Outer Market",
                    "Akihabara electronics district"
                ],
                "best_time_to_visit": "March-May (cherry blossom) or September-November (autumn foliage)",
                "average_duration": "5-7 days",
                "local_tips": [
                    "Get a Suica or Pasmo card for easy transportation",
                    "Download offline maps - Tokyo Metro can be complex",
                    "Tipping is not customary in Japan",
                    "Carry cash - many small shops don't accept cards"
                ],
                "currency": "Japanese Yen (JPY)",
                "language": "Japanese",
                "visa_info": "Visa-free for many countries for up to 30 days"
            },
            "paris": {
                "destination": "Paris",
                "country": "France",
                "region": "Europe",
                "description": "Paris, the City of Light, offers world-renowned art, cuisine, and architecture. The浪漫之都 awaits with iconic landmarks and charming cafes.",
                "highlights": [
                    "Eiffel Tower",
                    "Louvre Museum",
                    "Notre-Dame Cathedral",
                    "Montmartre and Sacré-Cœur",
                    "Champs-Élysées and Arc de Triomphe",
                    "Seine River cruise"
                ],
                "best_time_to_visit": "April-June or September-October",
                "average_duration": "4-5 days",
                "local_tips": [
                    "Learn basic French phrases - locals appreciate the effort",
                    "Museum pass can save money on multiple attractions",
                    "Avoid tourist restaurants near major landmarks",
                    "Metro is the easiest way to get around"
                ],
                "currency": "Euro (EUR)",
                "language": "French",
                "visa_info": "Schengen visa for non-EU visitors"
            },
            "bali": {
                "destination": "Bali",
                "country": "Indonesia",
                "region": "Southeast Asia",
                "description": "Bali is a tropical paradise known for its beautiful beaches, ancient temples, and vibrant arts scene. The Island of the Gods offers something for every traveler.",
                "highlights": [
                    "Uluwatu Temple",
                    "Rice terraces of Tegallalang",
                    "Sac monkey forest in Ubud",
                    "Mount Batur sunrise trek",
                    "Seminyak beach clubs",
                    "Traditional dance performances"
                ],
                "best_time_to_visit": "April-October (dry season)",
                "average_duration": "7-10 days",
                "local_tips": [
                    "Respect local customs and dress modestly at temples",
                    "Rent a scooter for flexibility",
                    "Bargain at markets but with a smile",
                    "Try the local cuisine - nasi goreng and satay!"
                ],
                "currency": "Indonesian Rupiah (IDR)",
                "language": "Indonesian (Bahasa Indonesia)",
                "visa_info": "Visa on arrival available for 30 days (extendable)"
            }
        }
        
        # Normalize destination name for lookup
        dest_lower = destination.lower().strip()
        
        # Check for exact match or partial match
        result = mock_destinations.get(dest_lower)
        if not result:
            # Try partial match
            for key, value in mock_destinations.items():
                if dest_lower in key or key in dest_lower:
                    result = value
                    break
        
        if not result:
            # Return generic info
            result = {
                "destination": destination,
                "country": "Unknown",
                "region": "Unknown",
                "description": f"Information for {destination} is being prepared.",
                "highlights": ["Local attractions", "Cultural sites", "Restaurants", "Shopping areas"],
                "best_time_to_visit": "Check local climate",
                "average_duration": "3-5 days",
                "local_tips": [
                    "Research local customs before visiting",
                    "Learn basic local phrases",
                    "Check visa requirements"
                ],
                "currency": "Verify local currency",
                "language": "Verify local language",
                "visa_info": "Check with embassy"
            }
        
        if not include_tips:
            result["local_tips"] = None
        
        return result
