# REST API Layer Documentation

## Overview

The travel-assistant-agent now includes a complete REST API layer that exposes core search, recommendation, and booking capabilities for frontend applications (React, mobile apps, etc.).

## Architecture

```
Frontend (React) → REST API → MCP Skills → Java API
                     ↓
               Task Store (in-memory)
```

## API Endpoints

### 1. Search API
**POST** `/api/agent/search`

Search for flights and hotels based on travel criteria.

**Request Body:**
```json
{
  "origin": "Beijing",
  "destination": "Tokyo",
  "departure_date": "2025-02-01",
  "passengers": 2,
  "return_date": "2025-02-05",
  "cabin_class": "economy",
  "trip_type": "roundtrip",
  "check_in_date": "2025-02-01",
  "check_out_date": "2025-02-05",
  "rooms": 1,
  "min_rating": 4.0,
  "include_hotels": true
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "outbound_flights": [
    {
      "flight_id": "FL123456",
      "airline": "Japan Airlines",
      "flight_number": "JL001",
      "departure_time": "08:00",
      "arrival_time": "12:30",
      "duration_minutes": 270,
      "stops": 0,
      "price_per_person": 600.0,
      "total_price": 1200.0,
      "currency": "USD",
      "available_seats": 150,
      "cabin_class": "economy"
    }
  ],
  "return_flights": [],
  "hotels": [
    {
      "hotel_id": "HT789012",
      "name": "Tokyo Grand Hotel",
      "rating": 4.5,
      "review_count": 1250,
      "address": "Shinjuku, Tokyo",
      "amenities": ["wifi", "breakfast", "gym"],
      "price_per_night": 120.0,
      "total_price": 600.0,
      "currency": "USD"
    }
  ],
  "search_metadata": {
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "passengers": 2,
    "results_count": 10
  },
  "timestamp": "2025-01-12T10:00:00Z"
}
```

### 2. Recommend API
**POST** `/api/agent/recommend`

Get comprehensive travel recommendations including destination info, attractions, weather, and reviews.

**Request Body:**
```json
{
  "destination": "Tokyo",
  "start_date": "2025-02-01",
  "end_date": "2025-02-05",
  "preferences": ["culture", "food", "nature"],
  "include_attractions": true,
  "include_weather": true,
  "include_reviews": true,
  "max_attractions": 5,
  "attraction_category": null
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "destination_info": {
    "destination": "Tokyo",
    "country": "Japan",
    "description": "Tokyo is Japan's capital and the world's most populous metropolis...",
    "best_time_to_visit": "March-May, September-November",
    "currency": "JPY",
    "language": "Japanese",
    "visa_info": "Visa-free for 90 days for many nationalities"
  },
  "attractions": [
    {
      "name": "Senso-ji Temple",
      "category": "culture",
      "description": "Ancient Buddhist temple in Asakusa",
      "rating": 4.8,
      "must_see": true,
      "estimated_duration": "2-3 hours",
      "entrance_fee": "Free"
    }
  ],
  "weather_forecast": [
    {
      "date": "2025-02-01",
      "day_of_week": "Saturday",
      "temperature_high": 8,
      "temperature_low": 2,
      "condition": "Partly Cloudy",
      "humidity": 65,
      "precipitation_chance": 20
    }
  ],
  "reviews": {
    "overall_rating": 4.7,
    "total_reviews": 15420,
    "recommended_by": 94.5,
    "sentiment_breakdown": {
      "positive": 85,
      "neutral": 12,
      "negative": 3
    },
    "pros": ["Great food", "Efficient transport", "Safe city"],
    "cons": ["Expensive", "Crowded"]
  },
  "timestamp": "2025-01-12T10:00:00Z"
}
```

### 3. Book API
**POST** `/api/agent/book`

Create a travel booking for selected flights, hotels, and services.

**Request Body:**
```json
{
  "customer_info": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123"
  },
  "trip_details": {
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "return_date": "2025-02-05",
    "travelers": 2
  },
  "selected_flight": {
    "flight_id": "FL123456",
    "airline": "Japan Airlines",
    "flight_number": "JL001",
    "total_price": 1200.0
  },
  "selected_hotel": {
    "hotel_id": "HT789012",
    "name": "Tokyo Grand Hotel",
    "total_price": 600.0
  },
  "passengers": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com"
    }
  ],
  "additional_services": [
    {
      "service": "travel_insurance",
      "price": 50.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440002",
  "booking_id": "BK789012",
  "status": "pending_payment",
  "created_at": "2025-01-12T10:00:00Z",
  "expires_at": "2025-01-13T10:00:00Z",
  "customer_info": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123"
  },
  "trip_summary": {
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "return_date": "2025-02-05",
    "travelers": 2,
    "flight_included": true,
    "hotel_included": true,
    "additional_services_count": 1
  },
  "price_breakdown": {
    "flights_total": 1200.0,
    "hotels_total": 600.0,
    "services_total": 50.0,
    "subtotal": 1850.0,
    "taxes_and_fees": 222.0,
    "total": 2072.0,
    "currency": "USD"
  },
  "payment_required": true,
  "next_steps": [
    "Review booking details carefully",
    "Proceed to payment to confirm booking",
    "Complete payment within 24 hours or booking will be released"
  ],
  "timestamp": "2025-01-12T10:00:00Z"
}
```

### 4. Status API
**GET** `/api/agent/status/{task_id}`

Query the status of a previously submitted task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": { /* task result */ },
  "error": null,
  "created_at": 1234567890.0,
  "updated_at": 1234567891.5,
  "progress": 1.0
}
```

**Task Status Values:**
- `pending` - Task is waiting to be processed
- `processing` - Task is currently being executed
- `completed` - Task completed successfully
- `failed` - Task failed with an error

### 5. List Tasks API
**GET** `/api/agent/tasks?status=completed&limit=20`

List all tasks, optionally filtered by status.

**Response:**
```json
{
  "total": 50,
  "filtered": 10,
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "result": { /* task result */ },
      "error": null,
      "created_at": 1234567890.0,
      "updated_at": 1234567891.5,
      "progress": 1.0
    }
  ]
}
```

## File Structure

```
src/
├── api/
│   ├── __init__.py          # API module exports
│   ├── routes.py            # API route definitions
│   └── schemas.py           # Pydantic request/response models
└── main.py                 # FastAPI app with routes registered
```

## Error Handling

All endpoints return a consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "JAVA_API_ERROR",
    "message": "Connection timeout",
    "status_code": 504,
    "details": { /* additional context */ }
  },
  "timestamp": "2025-01-12T10:00:00Z"
}
```

**Error Codes:**
- `INVALID_INPUT` - Request validation failed
- `JAVA_API_ERROR` - Java API call failed
- `FLIGHT_SEARCH_ERROR` - Flight search specific error
- `HOTEL_SEARCH_ERROR` - Hotel search specific error
- `BOOKING_FAILED` - Booking creation failed
- `INTERNAL_ERROR` - Unexpected server error

## Task Tracking

The API uses an in-memory task store to track async operations. Each endpoint returns a `task_id` that can be used to query the status of long-running operations.

**Note:** In production, the task store should be replaced with a persistent storage solution like Redis or a database.

## CORS Configuration

CORS is configured to allow requests from specified origins:

```python
# In .env.example
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

For development, you can add additional origins:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
```

## Integration with MCP Skills

The REST API integrates with the existing MCP skill architecture:

1. **Search API** → Calls `search_flights` and `search_hotels` skills
2. **Recommend API** → Calls `get_destination_info`, `get_attractions`, `get_weather_forecast`, `get_destination_reviews` skills
3. **Book API** → Calls `create_booking` skill

All skills are invoked through the MCP client, which provides:
- Automatic fallback to mock data if Java API is unavailable
- Consistent error handling
- Skill result transformation

## Testing

A comprehensive test suite is provided in `test_rest_api.py`:

```bash
# Run the test suite
python test_rest_api.py
```

The test suite validates:
- ✅ Search API with flights and hotels
- ✅ Recommend API with all recommendation types
- ✅ Book API with booking creation
- ✅ Status API for task tracking
- ✅ List Tasks API

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage with cURL

### Search for flights
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "passengers": 2,
    "return_date": "2025-02-05",
    "include_hotels": true
  }'
```

### Get recommendations
```bash
curl -X POST "http://localhost:8000/api/agent/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "start_date": "2025-02-01",
    "end_date": "2025-02-05"
  }'
```

### Create a booking
```bash
curl -X POST "http://localhost:8000/api/agent/book" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_info": {"name": "John Doe", "email": "john@example.com"},
    "trip_details": {
      "destination": "Tokyo",
      "departure_date": "2025-02-01",
      "return_date": "2025-02-05",
      "travelers": 2
    }
  }'
```

### Check task status
```bash
curl -X GET "http://localhost:8000/api/agent/status/{task_id}"
```

## Future Enhancements

1. **Persistent Task Storage**: Replace in-memory task store with Redis or database
2. **Authentication**: Add JWT authentication for protected endpoints
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Pagination**: Add pagination for large result sets
5. **Webhooks**: Support webhook callbacks for task completion
6. **Caching**: Cache frequent requests to reduce API calls
7. **Metrics**: Add Prometheus metrics for monitoring
8. **Async Task Queue**: Use Celery or similar for background tasks

## Support

For issues or questions:
- Check the API logs for detailed error messages
- Use the `/api/agent/tasks` endpoint to debug task states
- Review MCP skill documentation for specific skill behavior
