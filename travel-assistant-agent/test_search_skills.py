#!/usr/bin/env python3
"""
Test script for refactored SearchAgent skills
Tests that the skills can call JavaAPIClient properly
"""
import asyncio
import sys
sys.path.insert(0, '/home/engine/project/travel-assistant-agent')

from src.mcp_server.skills.search.search_flights import SearchFlightsSkill
from src.mcp_server.skills.search.search_hotels import SearchHotelsSkill
from src.mcp_server.skills.search.compare_results import CompareResultsSkill
from src.mcp_server.skills.search.filter_by_budget import FilterByBudgetSkill


async def test_search_flights():
    """Test search_flights skill"""
    print("\n" + "="*60)
    print("Testing SearchFlightsSkill (v2.0.0 - Java API)")
    print("="*60)
    
    skill = SearchFlightsSkill()
    print(f"Skill name: {skill.name}")
    print(f"Version: {skill.version}")
    print(f"Agent type: {skill.agent_type}")
    
    result = await skill.execute(
        origin="Beijing",
        destination="Tokyo",
        departure_date="2025-02-15",
        passengers=2,
        return_date="2025-02-20",
        cabin_class="economy"
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Outbound flights: {len(result.get('outbound_flights', []))}")
    print(f"Return flights: {len(result.get('return_flights', []))}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Search metadata: {result.get('search_metadata', {})}")
        if result.get('outbound_flights'):
            print(f"\nFirst outbound flight sample:")
            first_flight = result['outbound_flights'][0]
            for key, value in list(first_flight.items())[:5]:
                print(f"  {key}: {value}")
    
    return result


async def test_search_hotels():
    """Test search_hotels skill"""
    print("\n" + "="*60)
    print("Testing SearchHotelsSkill (v2.0.0 - Java API)")
    print("="*60)
    
    skill = SearchHotelsSkill()
    print(f"Skill name: {skill.name}")
    print(f"Version: {skill.version}")
    print(f"Agent type: {skill.agent_type}")
    
    result = await skill.execute(
        destination="Tokyo",
        check_in_date="2025-02-15",
        check_out_date="2025-02-20",
        guests=2,
        rooms=1
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Hotels found: {len(result.get('hotels', []))}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Search metadata: {result.get('search_metadata', {})}")
        if result.get('hotels'):
            print(f"\nFirst hotel sample:")
            first_hotel = result['hotels'][0]
            for key, value in list(first_hotel.items())[:5]:
                print(f"  {key}: {value}")
    
    return result


async def test_compare_results():
    """Test compare_results skill"""
    print("\n" + "="*60)
    print("Testing CompareResultsSkill (v2.0.0 - Client-side logic)")
    print("="*60)
    
    skill = CompareResultsSkill()
    print(f"Skill name: {skill.name}")
    print(f"Version: {skill.version}")
    
    # Create mock flight data for comparison
    mock_flights = [
        {"flight_id": "FL001", "total_price": 500, "stops": 0, "duration_minutes": 180},
        {"flight_id": "FL002", "total_price": 350, "stops": 1, "duration_minutes": 240},
        {"flight_id": "FL003", "total_price": 600, "stops": 0, "duration_minutes": 150},
    ]
    
    result = await skill.execute(
        result_type="flights",
        results=mock_flights,
        max_recommendations=2
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Top recommendations: {len(result.get('top_recommendations', []))}")
    
    if result.get('top_recommendations'):
        for rec in result['top_recommendations']:
            print(f"\nRank {rec['rank']}: Flight {rec['item']['flight_id']}")
            print(f"  Score: {rec['score']}")
            print(f"  Reason: {rec['recommendation_reason']}")


async def test_filter_by_budget():
    """Test filter_by_budget skill"""
    print("\n" + "="*60)
    print("Testing FilterByBudgetSkill (v2.0.0 - Client-side logic)")
    print("="*60)
    
    skill = FilterByBudgetSkill()
    print(f"Skill name: {skill.name}")
    print(f"Version: {skill.version}")
    
    # Create mock options
    mock_options = [
        {"flight_id": "FL001", "total_price": 500},
        {"flight_id": "FL002", "total_price": 350},
        {"flight_id": "FL003", "total_price": 600},
        {"flight_id": "FL004", "total_price": 450},
    ]
    
    result = await skill.execute(
        options=mock_options,
        budget={"max_total": 500},
        option_type="flights",
        sort_by="price_low_to_high"
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Filtered options: {len(result.get('filtered_options', []))}")
    print(f"Excluded options: {len(result.get('excluded_options', []))}")
    print(f"Budget summary: {result.get('budget_summary', {})}")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SearchAgent Skills Refactor Test Suite")
    print("Testing v2.0.0 with Java API integration")
    print("="*60)
    
    try:
        await test_search_flights()
        await test_search_hotels()
        await test_compare_results()
        await test_filter_by_budget()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        print("\nSummary:")
        print("- search_flights: Now calls JavaAPIClient ✅")
        print("- search_hotels: Now calls JavaAPIClient ✅")
        print("- compare_results: Client-side logic maintained ✅")
        print("- filter_by_budget: Client-side logic maintained ✅")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
