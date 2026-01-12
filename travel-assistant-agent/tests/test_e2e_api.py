#!/usr/bin/env python3
"""
End-to-End API Integration Tests
Tests the complete React → Agent → Java API workflow
"""
import pytest
import httpx
import json
from datetime import datetime, timedelta
import asyncio


# API base URL
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_search_api_e2e():
    """Test the complete search API workflow"""
    print("\n" + "="*70)
    print("TESTING SEARCH API E2E")
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
        
        # Test 1: Valid request
        response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=search_request,
            timeout=60.0
        )
        
        print(f"\nResponse Status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        result = response.json()
        print(f"Task ID: {result.get('task_id')}")
        
        # Validate response structure
        assert result.get('success') is True, "Search should be successful"
        assert 'task_id' in result, "Task ID should be present"
        assert 'outbound_flights' in result, "Outbound flights should be present"
        assert 'hotels' in result, "Hotels should be present"
        
        # Validate data integrity
        assert len(result.get('outbound_flights', [])) > 0, "Should have outbound flights"
        assert len(result.get('hotels', [])) > 0, "Should have hotels"
        
        # Test 2: Invalid parameters
        invalid_request = {
            "origin": "",  # Invalid: empty origin
            "destination": "Tokyo",
            "departure_date": "invalid-date",  # Invalid date format
        }
        
        response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=invalid_request,
            timeout=30.0
        )
        
        print(f"\nInvalid request response: {response.status_code}")
        assert response.status_code == 400, "Invalid request should return 400"
        
        print("\n✅ Search API E2E test PASSED")


@pytest.mark.asyncio
async def test_recommend_api_e2e():
    """Test the complete recommend API workflow"""
    print("\n" + "="*70)
    print("TESTING RECOMMEND API E2E")
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
        
        response = await client.post(
            f"{BASE_URL}/api/agent/recommend",
            json=recommend_request,
            timeout=60.0
        )
        
        print(f"\nResponse Status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        result = response.json()
        
        # Validate response structure
        assert result.get('success') is True, "Recommend should be successful"
        assert 'task_id' in result, "Task ID should be present"
        assert 'destination_info' in result, "Destination info should be present"
        assert 'attractions' in result, "Attractions should be present"
        assert 'weather_forecast' in result, "Weather forecast should be present"
        
        # Validate data integrity
        destination_info = result.get('destination_info')
        assert destination_info.get('destination') == "Tokyo", "Destination should match"
        assert len(result.get('attractions', [])) > 0, "Should have attractions"
        assert len(result.get('weather_forecast', [])) > 0, "Should have weather forecast"
        
        print("\n✅ Recommend API E2E test PASSED")


@pytest.mark.asyncio
async def test_book_api_e2e():
    """Test the complete book API workflow"""
    print("\n" + "="*70)
    print("TESTING BOOK API E2E")
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
        
        response = await client.post(
            f"{BASE_URL}/api/agent/book",
            json=book_request,
            timeout=60.0
        )
        
        print(f"\nResponse Status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        result = response.json()
        
        # Validate response structure
        assert result.get('success') is True, "Booking should be successful"
        assert 'task_id' in result, "Task ID should be present"
        assert 'booking_id' in result, "Booking ID should be present"
        assert 'status' in result, "Status should be present"
        assert 'price_breakdown' in result, "Price breakdown should be present"
        
        # Validate booking ID generation
        booking_id = result.get('booking_id')
        assert booking_id is not None and len(booking_id) > 0, "Booking ID should be generated"
        
        print(f"Booking ID: {booking_id}")
        print("\n✅ Book API E2E test PASSED")


@pytest.mark.asyncio
async def test_status_api_e2e():
    """Test the complete status API workflow"""
    print("\n" + "="*70)
    print("TESTING STATUS API E2E")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # First, trigger a search to get a task_id
        departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        search_request = {
            "origin": "Beijing",
            "destination": "Tokyo",
            "departure_date": departure_date,
            "passengers": 2,
        }
        
        search_response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=search_request,
            timeout=60.0
        )
        
        assert search_response.status_code == 200
        search_result = search_response.json()
        task_id = search_result.get('task_id')
        
        print(f"Task ID: {task_id}")
        
        # Test status polling
        for i in range(3):  # Poll 3 times
            response = await client.get(
                f"{BASE_URL}/api/agent/status/{task_id}",
                timeout=10.0
            )
            
            print(f"\nPoll {i+1} - Response Status: {response.status_code}")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            status_result = response.json()
            print(f"Status: {status_result.get('status')}")
            print(f"Progress: {status_result.get('progress', 0) * 100}%")
            
            # Validate status response structure
            assert 'task_id' in status_result, "Task ID should be present"
            assert 'status' in status_result, "Status should be present"
            assert 'progress' in status_result, "Progress should be present"
            
            # Check if task is completed
            if status_result.get('status') == 'completed':
                break
            
            await asyncio.sleep(1)  # Wait before next poll
        
        print("\n✅ Status API E2E test PASSED")


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "="*70)
    print("TESTING ERROR HANDLING")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Invalid parameters
        invalid_request = {
            "origin": "",
            "destination": "",
            "departure_date": "invalid-date",
        }
        
        response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=invalid_request,
            timeout=30.0
        )
        
        print(f"Invalid parameters test - Status: {response.status_code}")
        assert response.status_code == 400, "Invalid parameters should return 400"
        
        error_result = response.json()
        assert 'error' in error_result, "Error response should contain error field"
        print(f"Error message: {error_result.get('error', {}).get('message')}")
        
        # Test 2: Non-existent task ID
        response = await client.get(
            f"{BASE_URL}/api/agent/status/non-existent-task-id",
            timeout=10.0
        )
        
        print(f"Non-existent task test - Status: {response.status_code}")
        assert response.status_code == 404, "Non-existent task should return 404"
        
        # Test 3: Invalid endpoint
        response = await client.get(
            f"{BASE_URL}/api/agent/invalid-endpoint",
            timeout=10.0
        )
        
        print(f"Invalid endpoint test - Status: {response.status_code}")
        assert response.status_code == 404, "Invalid endpoint should return 404"
        
        print("\n✅ Error handling test PASSED")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_search_api_e2e())
    asyncio.run(test_recommend_api_e2e())
    asyncio.run(test_book_api_e2e())
    asyncio.run(test_status_api_e2e())
    asyncio.run(test_error_handling())
    
    print("\n" + "="*70)
    print("ALL E2E API TESTS COMPLETED")
    print("="*70)