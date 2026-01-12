#!/usr/bin/env python3
"""
Test script for REST API endpoints
Validates the search, recommend, and book endpoints
"""
import asyncio
import httpx
import json
from datetime import datetime, timedelta


# API base URL
BASE_URL = "http://localhost:8000"


async def test_search_api():
    """Test the search API endpoint"""
    print("\n" + "="*70)
    print("TESTING SEARCH API")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Prepare search request
        departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        search_request = {
            "origin": "Beijing",
            "destination": "Tokyo",
            "departure_date": departure_date,
            "passengers": 2,
            "return_date": return_date,
            "cabin_class": "economy",
            "trip_type": "roundtrip",
            "check_in_date": departure_date,
            "check_out_date": return_date,
            "rooms": 1,
            "min_rating": 4.0,
            "include_hotels": True
        }
        
        print(f"Request: {json.dumps(search_request, indent=2)}")
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/agent/search",
                json=search_request,
                timeout=60.0
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nTask ID: {result.get('task_id')}")
                print(f"Success: {result.get('success')}")
                print(f"Outbound Flights: {len(result.get('outbound_flights', []))}")
                print(f"Return Flights: {len(result.get('return_flights', []))}")
                print(f"Hotels: {len(result.get('hotels', []))}")
                
                # Show first flight
                if result.get('outbound_flights'):
                    print(f"\nFirst Outbound Flight:")
                    flight = result['outbound_flights'][0]
                    print(f"  Flight: {flight.get('airline')} {flight.get('flight_number')}")
                    print(f"  Time: {flight.get('departure_time')} - {flight.get('arrival_time')}")
                    print(f"  Price: ${flight.get('total_price')} ({flight.get('currency')})")
                
                # Show first hotel
                if result.get('hotels'):
                    print(f"\nFirst Hotel:")
                    hotel = result['hotels'][0]
                    print(f"  Name: {hotel.get('name')}")
                    print(f"  Rating: {hotel.get('rating')}")
                    print(f"  Price: ${hotel.get('price_per_night')}/night")
                
                print("\n✅ Search API test PASSED")
                return result.get('task_id')
            else:
                print(f"\n❌ Search API test FAILED")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"\n❌ Search API test FAILED with exception: {e}")
            return None


async def test_recommend_api():
    """Test the recommend API endpoint"""
    print("\n" + "="*70)
    print("TESTING RECOMMEND API")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Prepare recommend request
        start_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        recommend_request = {
            "destination": "Tokyo",
            "start_date": start_date,
            "end_date": end_date,
            "preferences": ["culture", "food", "nature"],
            "include_attractions": True,
            "include_weather": True,
            "include_reviews": True,
            "max_attractions": 5
        }
        
        print(f"Request: {json.dumps(recommend_request, indent=2)}")
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/agent/recommend",
                json=recommend_request,
                timeout=60.0
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nTask ID: {result.get('task_id')}")
                print(f"Success: {result.get('success')}")
                
                # Destination info
                if result.get('destination_info'):
                    dest = result['destination_info']
                    print(f"\nDestination: {dest.get('destination')}, {dest.get('country')}")
                    print(f"Best time to visit: {dest.get('best_time_to_visit')}")
                    print(f"Currency: {dest.get('currency')}")
                
                # Attractions
                print(f"\nAttractions: {len(result.get('attractions', []))}")
                if result.get('attractions'):
                    for i, attr in enumerate(result['attractions'][:3], 1):
                        print(f"  {i}. {attr.get('name')} ({attr.get('category')}) - Rating: {attr.get('rating')}")
                
                # Weather
                print(f"\nWeather Forecast: {len(result.get('weather_forecast', []))} days")
                if result.get('weather_forecast'):
                    for day in result['weather_forecast'][:3]:
                        print(f"  {day.get('date')}: {day.get('condition')}, {day.get('temperature_high')}°C/{day.get('temperature_low')}°C")
                
                # Reviews
                if result.get('reviews'):
                    reviews = result['reviews']
                    print(f"\nReviews: Overall Rating {reviews.get('overall_rating')}/5 ({reviews.get('total_reviews')} reviews)")
                    print(f"Recommended by: {reviews.get('recommended_by', 0)}%")
                
                print("\n✅ Recommend API test PASSED")
                return result.get('task_id')
            else:
                print(f"\n❌ Recommend API test FAILED")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"\n❌ Recommend API test FAILED with exception: {e}")
            return None


async def test_book_api():
    """Test the book API endpoint"""
    print("\n" + "="*70)
    print("TESTING BOOK API")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Prepare book request
        departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        book_request = {
            "customer_info": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123"
            },
            "trip_details": {
                "destination": "Tokyo",
                "departure_date": departure_date,
                "return_date": return_date,
                "travelers": 2
            },
            "selected_flight": {
                "flight_id": "FL123456",
                "airline": "Sample Airline",
                "flight_number": "SA123",
                "total_price": 1200.0
            },
            "selected_hotel": {
                "hotel_id": "HT789012",
                "name": "Sample Hotel",
                "total_price": 840.0
            },
            "passengers": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com"
                },
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "jane.doe@example.com"
                }
            ],
            "additional_services": [
                {
                    "service": "travel_insurance",
                    "price": 50.0
                }
            ]
        }
        
        print(f"Request: {json.dumps(book_request, indent=2)}")
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/agent/book",
                json=book_request,
                timeout=60.0
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nTask ID: {result.get('task_id')}")
                print(f"Success: {result.get('success')}")
                print(f"Booking ID: {result.get('booking_id')}")
                print(f"Status: {result.get('status')}")
                
                if result.get('price_breakdown'):
                    price = result['price_breakdown']
                    print(f"\nPrice Breakdown:")
                    print(f"  Flights: ${price.get('flights_total')}")
                    print(f"  Hotels: ${price.get('hotels_total')}")
                    print(f"  Services: ${price.get('services_total')}")
                    print(f"  Subtotal: ${price.get('subtotal')}")
                    print(f"  Taxes & Fees: ${price.get('taxes_and_fees')}")
                    print(f"  Total: ${price.get('total')}")
                
                if result.get('next_steps'):
                    print(f"\nNext Steps:")
                    for step in result['next_steps']:
                        print(f"  - {step}")
                
                print("\n✅ Book API test PASSED")
                return result.get('task_id')
            else:
                print(f"\n❌ Book API test FAILED")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"\n❌ Book API test FAILED with exception: {e}")
            return None


async def test_status_api(task_id):
    """Test the status API endpoint"""
    print("\n" + "="*70)
    print("TESTING STATUS API")
    print("="*70)
    
    if not task_id:
        print("⚠️ No task ID provided, skipping status test")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/agent/status/{task_id}",
                timeout=10.0
            )
            
            print(f"Request: GET /api/agent/status/{task_id}")
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nTask ID: {result.get('task_id')}")
                print(f"Status: {result.get('status')}")
                print(f"Progress: {result.get('progress', 0) * 100}%")
                print(f"Created At: {result.get('created_at')}")
                print(f"Updated At: {result.get('updated_at')}")
                
                if result.get('error'):
                    print(f"\nError: {result.get('error')}")
                
                print("\n✅ Status API test PASSED")
            else:
                print(f"\n❌ Status API test FAILED")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"\n❌ Status API test FAILED with exception: {e}")


async def test_list_tasks():
    """Test the list tasks endpoint"""
    print("\n" + "="*70)
    print("TESTING LIST TASKS API")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/agent/tasks",
                timeout=10.0
            )
            
            print(f"Request: GET /api/agent/tasks")
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nTotal Tasks: {result.get('total')}")
                print(f"Filtered Tasks: {result.get('filtered')}")
                
                if result.get('tasks'):
                    print(f"\nRecent Tasks:")
                    for task in result['tasks'][:5]:
                        print(f"  - {task.get('task_id')}: {task.get('status')}")
                
                print("\n✅ List Tasks API test PASSED")
            else:
                print(f"\n❌ List Tasks API test FAILED")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"\n❌ List Tasks API test FAILED with exception: {e}")


async def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("REST API TEST SUITE")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    
    # Test all endpoints
    search_task_id = await test_search_api()
    recommend_task_id = await test_recommend_api()
    book_task_id = await test_book_api()
    
    # Test status with one of the task IDs
    await test_status_api(search_task_id)
    
    # List all tasks
    await test_list_tasks()
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
