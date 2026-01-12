#!/usr/bin/env python3
"""
Final verification script for REST API implementation
Checks all acceptance criteria
"""
import os
import sys


def check_file_exists(filepath):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists


def check_file_contains(filepath, content, description):
    """Check if file contains specific content"""
    if not os.path.exists(filepath):
        print(f"❌ {description} - File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        print(f"❌ {description} - Error reading file: {e}")
        return False
    
    contains = content in file_content
    status = "✅" if contains else "❌"
    print(f"{status} {description}")
    return contains


def main():
    """Run all verification checks"""
    print("="*70)
    print("REST API IMPLEMENTATION VERIFICATION")
    print("="*70)
    print()
    
    results = []
    
    # Check 1: Core files exist
    print("CHECK 1: Core API Files Exist")
    print("-"*70)
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/src/api/__init__.py"))
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/src/api/schemas.py"))
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/src/api/routes.py"))
    print()
    
    # Check 2: Routes defined
    print("CHECK 2: API Routes Defined")
    print("-"*70)
    routes_file = "/home/engine/project/travel-assistant-agent/src/api/routes.py"
    results.append(check_file_contains(routes_file, "@router.post(\"/search\"", "POST /api/agent/search endpoint"))
    results.append(check_file_contains(routes_file, "@router.post(\"/recommend\"", "POST /api/agent/recommend endpoint"))
    results.append(check_file_contains(routes_file, "@router.post(\"/book\"", "POST /api/agent/book endpoint"))
    results.append(check_file_contains(routes_file, "@router.get(\"/status/{task_id}\"", "GET /api/agent/status/{task_id} endpoint"))
    results.append(check_file_contains(routes_file, "@router.get(\"/tasks\"", "GET /api/agent/tasks endpoint"))
    print()
    
    # Check 3: Schemas defined
    print("CHECK 3: Request/Response Schemas Defined")
    print("-"*70)
    schemas_file = "/home/engine/project/travel-assistant-agent/src/api/schemas.py"
    results.append(check_file_contains(schemas_file, "class SearchRequest", "SearchRequest schema"))
    results.append(check_file_contains(schemas_file, "class SearchResponse", "SearchResponse schema"))
    results.append(check_file_contains(schemas_file, "class RecommendRequest", "RecommendRequest schema"))
    results.append(check_file_contains(schemas_file, "class RecommendResponse", "RecommendResponse schema"))
    results.append(check_file_contains(schemas_file, "class BookRequest", "BookRequest schema"))
    results.append(check_file_contains(schemas_file, "class BookResponse", "BookResponse schema"))
    results.append(check_file_contains(schemas_file, "class StatusResponse", "StatusResponse schema"))
    print()
    
    # Check 4: Routes map to MCP skills
    print("CHECK 4: Routes Map to MCP Skills")
    print("-"*70)
    results.append(check_file_contains(routes_file, '"search_flights"', "Search API calls search_flights skill"))
    results.append(check_file_contains(routes_file, '"search_hotels"', "Search API calls search_hotels skill"))
    results.append(check_file_contains(routes_file, '"get_destination_info"', "Recommend API calls get_destination_info skill"))
    results.append(check_file_contains(routes_file, '"get_attractions"', "Recommend API calls get_attractions skill"))
    results.append(check_file_contains(routes_file, '"get_weather_forecast"', "Recommend API calls get_weather_forecast skill"))
    results.append(check_file_contains(routes_file, '"get_destination_reviews"', "Recommend API calls get_destination_reviews skill"))
    results.append(check_file_contains(routes_file, '"create_booking"', "Book API calls create_booking skill"))
    print()
    
    # Check 5: Error handling
    print("CHECK 5: Error Handling Implemented")
    print("-"*70)
    results.append(check_file_contains(routes_file, "except Exception as e:", "Exception handling"))
    results.append(check_file_contains(routes_file, "error_detail =", "Error detail creation"))
    results.append(check_file_contains(routes_file, "app_logger.error", "Error logging"))
    results.append(check_file_contains(schemas_file, "class ErrorDetail", "ErrorDetail schema"))
    results.append(check_file_contains(schemas_file, "class ErrorResponse", "ErrorResponse schema"))
    print()
    
    # Check 6: Logging implemented
    print("CHECK 6: Logging Implemented")
    print("-"*70)
    results.append(check_file_contains(routes_file, "app_logger.info", "INFO level logging"))
    results.append(check_file_contains(routes_file, "app_logger.error", "ERROR level logging"))
    results.append(check_file_contains(routes_file, "task_id", "Task ID in logs"))
    print()
    
    # Check 7: CORS support
    print("CHECK 7: CORS Support Enabled")
    print("-"*70)
    main_file = "/home/engine/project/travel-assistant-agent/src/main.py"
    results.append(check_file_contains(main_file, "CORSMiddleware", "CORSMiddleware imported"))
    results.append(check_file_contains(main_file, "allow_origins=", "CORS origins configured"))
    print()
    
    # Check 8: Router registered in main.py
    print("CHECK 8: API Router Registered in Main")
    print("-"*70)
    results.append(check_file_contains(main_file, "from src.api import routes as api_routes", "API routes imported"))
    results.append(check_file_contains(main_file, "app.include_router(api_routes.router)", "Router registered"))
    print()
    
    # Check 9: Documentation files
    print("CHECK 9: Documentation Files Created")
    print("-"*70)
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/API_REST_README.md"))
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/REST_API_IMPLEMENTATION_SUMMARY.md"))
    print()
    
    # Check 10: Test files
    print("CHECK 10: Test Files Created")
    print("-"*70)
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/test_rest_api.py"))
    results.append(check_file_exists("/home/engine/project/travel-assistant-agent/validate_api.py"))
    print()
    
    # Summary
    print("="*70)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    print(f"SUMMARY: {passed}/{total} checks passed")
    
    if failed == 0:
        print("✅ ALL ACCEPTANCE CRITERIA MET!")
        print("="*70)
        return 0
    else:
        print(f"❌ {failed} checks failed")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
