#!/usr/bin/env python3
"""
Complete API Integration Tests
Tests the full React → Agent → Java API workflow
"""
import pytest
import httpx
import json
from datetime import datetime, timedelta
import asyncio
import time


# API base URL
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_complete_workflow():
    """Test the complete workflow: search → recommend → book → status"""
    print("\n" + "="*70)
    print("TESTING COMPLETE WORKFLOW")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Search for flights and hotels
        print("\n1. Searching for flights and hotels...")
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
        
        search_response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=search_request,
            timeout=60.0
        )
        
        assert search_response.status_code == 200
        search_result = search_response.json()
        assert search_result.get('success') is True
        assert len(search_result.get('outbound_flights', [])) > 0
        assert len(search_result.get('hotels', [])) > 0
        
        search_task_id = search_result.get('task_id')
        print(f"✅ Search completed. Task ID: {search_task_id}")
        
        # Step 2: Get recommendations
        print("\n2. Getting travel recommendations...")
        recommend_request = {
            "destination": "Tokyo",
            "start_date": departure_date,
            "end_date": return_date,
            "preferences": ["culture", "food", "nature"],
            "include_attractions": True,
            "include_weather": True,
            "include_reviews": True,
            "max_attractions": 5
        }
        
        recommend_response = await client.post(
            f"{BASE_URL}/api/agent/recommend",
            json=recommend_request,
            timeout=60.0
        )
        
        assert recommend_response.status_code == 200
        recommend_result = recommend_response.json()
        assert recommend_result.get('success') is True
        assert 'destination_info' in recommend_result
        assert len(recommend_result.get('attractions', [])) > 0
        
        recommend_task_id = recommend_result.get('task_id')
        print(f"✅ Recommendations received. Task ID: {recommend_task_id}")
        
        # Step 3: Create booking
        print("\n3. Creating booking...")
        
        # Use data from search results
        first_flight = search_result.get('outbound_flights', [{}])[0]
        first_hotel = search_result.get('hotels', [{}])[0]
        
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
                "flight_id": first_flight.get('flight_id', 'FL123456'),
                "airline": first_flight.get('airline', 'Sample Airline'),
                "flight_number": first_flight.get('flight_number', 'SA123'),
                "total_price": first_flight.get('total_price', 1200.0)
            },
            "selected_hotel": {
                "hotel_id": first_hotel.get('hotel_id', 'HT789012'),
                "name": first_hotel.get('name', 'Sample Hotel'),
                "total_price": first_hotel.get('price_per_night', 200.0) * 7  # 7 nights
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
        
        book_response = await client.post(
            f"{BASE_URL}/api/agent/book",
            json=book_request,
            timeout=60.0
        )
        
        assert book_response.status_code == 200
        book_result = book_response.json()
        assert book_result.get('success') is True
        assert 'booking_id' in book_result
        assert len(book_result.get('booking_id', '')) > 0
        
        booking_id = book_result.get('booking_id')
        book_task_id = book_result.get('task_id')
        print(f"✅ Booking created. Booking ID: {booking_id}")
        
        # Step 4: Check status of all tasks
        print("\n4. Checking task statuses...")
        
        for task_id, task_name in [
            (search_task_id, "Search"),
            (recommend_task_id, "Recommend"),
            (book_task_id, "Booking")
        ]:
            if task_id:
                status_response = await client.get(
                    f"{BASE_URL}/api/agent/status/{task_id}",
                    timeout=10.0
                )
                
                assert status_response.status_code == 200
                status_result = status_response.json()
                assert status_result.get('task_id') == task_id
                print(f"  {task_name} task status: {status_result.get('status')}")
        
        print("\n✅ Complete workflow test PASSED")
        
        # Validate data consistency
        assert search_result.get('destination') == "Tokyo"
        assert recommend_result.get('destination_info', {}).get('destination') == "Tokyo"
        assert book_result.get('trip_summary', {}).get('destination') == "Tokyo"
        
        print("✅ Data consistency verified")


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test concurrent API requests"""
    print("\n" + "="*70)
    print("TESTING CONCURRENT REQUESTS")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Prepare multiple search requests
        departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        search_requests = [
            {
                "origin": "Beijing",
                "destination": "Tokyo",
                "departure_date": departure_date,
                "passengers": 2,
            },
            {
                "origin": "Shanghai",
                "destination": "Osaka",
                "departure_date": departure_date,
                "passengers": 1,
            },
            {
                "origin": "Guangzhou",
                "destination": "Seoul",
                "departure_date": departure_date,
                "passengers": 3,
            }
        ]
        
        # Send concurrent requests
        tasks = []
        for i, request in enumerate(search_requests):
            task = asyncio.create_task(
                client.post(
                    f"{BASE_URL}/api/agent/search",
                    json=request,
                    timeout=60.0
                )
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Validate all responses
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i+1} failed: {response}")
                assert False, f"Request {i+1} failed with exception: {response}"
            
            assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
            
            result = response.json()
            assert result.get('success') is True, f"Request {i+1} should be successful"
            assert 'task_id' in result, f"Request {i+1} should have task_id"
            
            print(f"Request {i+1} completed successfully. Task ID: {result.get('task_id')}")
        
        print("\n✅ Concurrent requests test PASSED")


@pytest.mark.asyncio
async def test_performance():
    """Test API performance"""
    print("\n" + "="*70)
    print("TESTING PERFORMANCE")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Single request response time
        print("\n1. Testing single request response time...")
        departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        search_request = {
            "origin": "Beijing",
            "destination": "Tokyo",
            "departure_date": departure_date,
            "passengers": 2,
        }
        
        start_time = time.time()
        response = await client.post(
            f"{BASE_URL}/api/agent/search",
            json=search_request,
            timeout=60.0
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Single request response time: {response_time:.2f} seconds")
        
        assert response.status_code == 200
        assert response_time < 10.0, "Single request should complete in under 10 seconds"
        
        # Test 2: Batch requests throughput
        print("\n2. Testing batch requests throughput...")
        
        batch_size = 5
        start_time = time.time()
        
        tasks = []
        for i in range(batch_size):
            task = asyncio.create_task(
                client.post(
                    f"{BASE_URL}/api/agent/search",
                    json=search_request,
                    timeout=60.0
                )
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        batch_time = end_time - start_time
        throughput = batch_size / batch_time
        
        print(f"Batch of {batch_size} requests completed in {batch_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} requests/second")
        
        # Validate all batch responses
        successful_requests = 0
        for response in responses:
            if isinstance(response, Exception):
                continue
            if response.status_code == 200:
                successful_requests += 1
        
        print(f"Successful requests: {successful_requests}/{batch_size}")
        assert successful_requests == batch_size, "All batch requests should be successful"
        
        # Test 3: Memory usage (basic check)
        print("\n3. Testing memory usage...")
        
        # Run multiple requests and check if server handles them without crashing
        for i in range(3):
            response = await client.post(
                f"{BASE_URL}/api/agent/search",
                json=search_request,
                timeout=60.0
            )
            assert response.status_code == 200
        
        print("Memory usage test completed (server did not crash)")
        
        print("\n✅ Performance test PASSED")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_complete_workflow())
    asyncio.run(test_concurrent_requests())
    asyncio.run(test_performance())
    
    print("\n" + "="*70)
    print("ALL API INTEGRATION TESTS COMPLETED")
    print("="*70)