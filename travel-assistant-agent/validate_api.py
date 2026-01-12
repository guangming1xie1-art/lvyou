#!/usr/bin/env python3
"""
Simple validation script to check API module structure
Does not require dependencies to be installed
"""
import os
import ast


def validate_python_file(filepath):
    """Validate Python file syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def main():
    """Validate all API module files"""
    print("="*70)
    print("VALIDATING REST API MODULE")
    print("="*70)
    
    base_path = "/home/engine/project/travel-assistant-agent/src/api"
    files_to_validate = [
        "schemas.py",
        "routes.py",
        "__init__.py"
    ]
    
    all_valid = True
    
    for filename in files_to_validate:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            is_valid, error = validate_python_file(filepath)
            if is_valid:
                print(f"✅ {filename:20} - Syntax valid")
            else:
                print(f"❌ {filename:20} - Syntax error: {error}")
                all_valid = False
        else:
            print(f"⚠️  {filename:20} - File not found")
            all_valid = False
    
    print("\n" + "="*70)
    
    # Check that routes.py imports are correct
    routes_path = os.path.join(base_path, "routes.py")
    with open(routes_path, 'r', encoding='utf-8') as f:
        routes_content = f.read()
    
    checks = [
        ("SearchRequest", "SearchRequest import"),
        ("SearchResponse", "SearchResponse import"),
        ("RecommendRequest", "RecommendRequest import"),
        ("RecommendResponse", "RecommendResponse import"),
        ("BookRequest", "BookRequest import"),
        ("BookResponse", "BookResponse import"),
        ("@router.post", "Router decorator"),
        ("async def search_travel", "Search endpoint"),
        ("async def recommend_travel", "Recommend endpoint"),
        ("async def create_booking", "Book endpoint"),
        ("async def get_task_status", "Status endpoint"),
    ]
    
    print("CHECKING ROUTE DEFINITIONS")
    print("="*70)
    
    for check_str, description in checks:
        if check_str in routes_content:
            print(f"✅ {description:30} - Found")
        else:
            print(f"❌ {description:30} - Missing")
            all_valid = False
    
    print("\n" + "="*70)
    
    # Check schemas.py
    schemas_path = os.path.join(base_path, "schemas.py")
    with open(schemas_path, 'r', encoding='utf-8') as f:
        schemas_content = f.read()
    
    print("CHECKING SCHEMA DEFINITIONS")
    print("="*70)
    
    schema_checks = [
        ("class SearchRequest", "SearchRequest model"),
        ("class SearchResponse", "SearchResponse model"),
        ("class RecommendRequest", "RecommendRequest model"),
        ("class RecommendResponse", "RecommendResponse model"),
        ("class BookRequest", "BookRequest model"),
        ("class BookResponse", "BookResponse model"),
        ("class StatusResponse", "StatusResponse model"),
    ]
    
    for check_str, description in schema_checks:
        if check_str in schemas_content:
            print(f"✅ {description:30} - Found")
        else:
            print(f"❌ {description:30} - Missing")
            all_valid = False
    
    print("\n" + "="*70)
    
    # Check main.py includes the routes
    main_path = "/home/engine/project/travel-assistant-agent/src/main.py"
    with open(main_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    print("CHECKING MAIN.PY INTEGRATION")
    print("="*70)
    
    integration_checks = [
        ("from api import routes as api_routes", "API routes import"),
        ("app.include_router(api_routes.router)", "Router registration"),
    ]
    
    for check_str, description in integration_checks:
        if check_str in main_content:
            print(f"✅ {description:30} - Found")
        else:
            print(f"❌ {description:30} - Missing")
            all_valid = False
    
    print("\n" + "="*70)
    
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED")
        print("="*70)
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit(main())
