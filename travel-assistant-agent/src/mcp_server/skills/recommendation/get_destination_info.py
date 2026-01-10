"""GetDestinationInfoSkill - Fetch general destination information"""

from typing import Any, Dict
from ..base_skill import BaseSkill


class GetDestinationInfoSkill(BaseSkill):
    """Get general information about a travel destination
    
    This skill provides comprehensive destination information including
    description, currency, language, visa requirements, and travel tips.
    """
    
    name = "get_destination_info"
    agent_type = "recommendation"
    description = "Fetch general destination information including description, currency, language, and visa requirements"
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
                    "description": "Preferred language for information",
                    "default": "en"
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
                "best_time_to_visit": {"type": "string"},
                "average_duration": {"type": "string"},
                "currency": {"type": "string"},
                "language": {"type": "string"},
                "visa_info": {"type": "string"},
                "local_tips": {"type": "array", "items": {"type": "string"}},
                "timezone": {"type": "string"},
                "emergency_number": {"type": "string"}
            },
            "required": ["destination", "country", "description"]
        }
    
    async def execute(self, destination: str, language: str = "en", **kwargs) -> Dict[str, Any]:
        """Get destination information
        
        Args:
            destination: Destination name
            language: Preferred language
            
        Returns:
            Comprehensive destination information
        """
        if not self.validate_input({"destination": destination}):
            raise ValueError("Invalid input: destination is required")
        
        # Mock destination database
        mock_destinations = {
            "tokyo": {
                "destination": "Tokyo",
                "country": "Japan",
                "region": "Asia",
                "description": "Tokyo is a vibrant metropolis blending ultramodern and traditional culture. Experience cutting-edge technology alongside ancient temples.",
                "best_time_to_visit": "March-May (cherry blossom) or September-November (autumn foliage)",
                "average_duration": "5-7 days",
                "currency": "Japanese Yen (JPY)",
                "language": "Japanese",
                "visa_info": "Visa-free for many countries for up to 90 days",
                "local_tips": [
                    "Get a Suica or Pasmo card for easy transportation",
                    "Download offline maps - Tokyo Metro can be complex",
                    "Tipping is not customary in Japan",
                    "Carry cash - many small shops don't accept cards"
                ],
                "timezone": "JST (UTC+9)",
                "emergency_number": "110 (Police), 119 (Ambulance/Fire)"
            },
            "paris": {
                "destination": "Paris",
                "country": "France",
                "region": "Europe",
                "description": "Paris, the City of Light, offers world-renowned art, cuisine, and architecture. The romantic capital awaits with iconic landmarks and charming cafes.",
                "best_time_to_visit": "April-June or September-October",
                "average_duration": "4-5 days",
                "currency": "Euro (EUR)",
                "language": "French",
                "visa_info": "Schengen visa required for non-EU visitors",
                "local_tips": [
                    "Learn basic French phrases - locals appreciate the effort",
                    "Museum pass can save money on multiple attractions",
                    "Avoid tourist restaurants near major landmarks",
                    "Metro is the easiest way to get around"
                ],
                "timezone": "CET (UTC+1)",
                "emergency_number": "112 (All emergencies)"
            },
            "bali": {
                "destination": "Bali",
                "country": "Indonesia",
                "region": "Southeast Asia",
                "description": "Bali is a tropical paradise known for its beautiful beaches, ancient temples, and vibrant arts scene. The Island of the Gods offers something for every traveler.",
                "best_time_to_visit": "April-October (dry season)",
                "average_duration": "7-10 days",
                "currency": "Indonesian Rupiah (IDR)",
                "language": "Indonesian (Bahasa Indonesia)",
                "visa_info": "Visa on arrival available for 30 days (extendable)",
                "local_tips": [
                    "Respect local customs and dress modestly at temples",
                    "Rent a scooter for flexibility",
                    "Bargain at markets but with a smile",
                    "Try the local cuisine - nasi goreng and satay!"
                ],
                "timezone": "WITA (UTC+8)",
                "emergency_number": "112 (All emergencies)"
            },
            "new york": {
                "destination": "New York",
                "country": "USA",
                "region": "North America",
                "description": "The city that never sleeps offers world-class museums, dining, theater, and iconic landmarks. Experience the energy of one of the world's most dynamic cities.",
                "best_time_to_visit": "April-June or September-November",
                "average_duration": "4-6 days",
                "currency": "US Dollar (USD)",
                "language": "English",
                "visa_info": "ESTA required for many countries, or B1/B2 visa",
                "local_tips": [
                    "Get a MetroCard for subway travel",
                    "Walk between attractions - many are closer than you think",
                    "Tipping 15-20% is expected at restaurants",
                    "Book Broadway tickets in advance"
                ],
                "timezone": "EST (UTC-5)",
                "emergency_number": "911 (All emergencies)"
            }
        }
        
        # Normalize destination name for lookup
        dest_lower = destination.lower().strip()
        
        # Check for exact or partial match
        result = mock_destinations.get(dest_lower)
        if not result:
            for key, value in mock_destinations.items():
                if dest_lower in key or key in dest_lower:
                    result = value
                    break
        
        if not result:
            # Return generic info for unknown destinations
            result = {
                "destination": destination,
                "country": "Unknown",
                "region": "Unknown",
                "description": f"Information for {destination} is being prepared. This is a wonderful destination with unique attractions and culture.",
                "best_time_to_visit": "Check local climate and seasons",
                "average_duration": "3-5 days",
                "currency": "Local currency",
                "language": "Local language",
                "visa_info": "Check with embassy or consulate",
                "local_tips": [
                    "Research local customs before visiting",
                    "Learn basic local phrases",
                    "Check visa requirements well in advance"
                ],
                "timezone": "Check local timezone",
                "emergency_number": "Check local emergency services"
            }
        
        return result
