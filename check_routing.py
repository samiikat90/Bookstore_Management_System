#!/usr/bin/env python3
"""
Route verification script - checks for common routing issues.
"""

import sys
import os
import re

def extract_routes_from_app():
    """Extract all route definitions from app.py"""
    app_file = os.path.join(os.path.dirname(__file__), 'app', 'app.py')
    
    if not os.path.exists(app_file):
        print(f"Error: {app_file} not found")
        return None, None
    
    routes = {}
    route_methods = {}
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all @app.route decorators and their corresponding functions
    route_pattern = r"@app\.route\('([^']+)'(?:,\s*methods=\[([^\]]+)\])?\)\s*\ndef\s+(\w+)"
    matches = re.finditer(route_pattern, content)
    
    for match in matches:
        route_path = match.group(1)
        methods = match.group(2) if match.group(2) else "'GET'"
        function_name = match.group(3)
        
        routes[function_name] = route_path
        route_methods[function_name] = methods
    
    return routes, route_methods

def extract_url_for_references():
    """Extract all url_for references from templates"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    url_for_refs = set()
    
    if not os.path.exists(templates_dir):
        print(f"Error: {templates_dir} not found")
        return url_for_refs
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find url_for patterns
                url_for_pattern = r"url_for\(['\"]([^'\"]+)['\"]"
                matches = re.finditer(url_for_pattern, content)
                
                for match in matches:
                    url_for_refs.add(match.group(1))
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return url_for_refs

def check_routing_integrity():
    """Main function to check routing integrity"""
    print("=" * 60)
    print("ROUTE INTEGRITY CHECK")
    print("=" * 60)
    
    # Extract routes from app.py
    routes, route_methods = extract_routes_from_app()
    if routes is None:
        return
    
    print(f"Found {len(routes)} route definitions:")
    for func_name, route_path in sorted(routes.items()):
        methods = route_methods.get(func_name, "'GET'")
        print(f"  {func_name:<25} -> {route_path:<30} [{methods}]")
    
    print("\n" + "=" * 60)
    
    # Extract url_for references from templates
    url_for_refs = extract_url_for_references()
    print(f"Found {len(url_for_refs)} url_for references in templates:")
    for ref in sorted(url_for_refs):
        print(f"  {ref}")
    
    print("\n" + "=" * 60)
    print("POTENTIAL ISSUES:")
    
    # Check for url_for references that don't have corresponding routes
    missing_routes = []
    special_cases = {'static'}  # Flask built-in routes
    
    for ref in url_for_refs:
        if ref not in routes and ref not in special_cases:
            missing_routes.append(ref)
    
    if missing_routes:
        print(f"\n❌ MISSING ROUTES ({len(missing_routes)}):")
        for missing in sorted(missing_routes):
            print(f"  - {missing} (referenced in templates but no route found)")
    else:
        print("\n✅ All template url_for references have corresponding routes")
    
    # Check for duplicate routes
    route_paths = {}
    for func_name, route_path in routes.items():
        if route_path in route_paths:
            route_paths[route_path].append(func_name)
        else:
            route_paths[route_path] = [func_name]
    
    duplicates = {path: funcs for path, funcs in route_paths.items() if len(funcs) > 1}
    
    if duplicates:
        print(f"\n⚠️  DUPLICATE ROUTES ({len(duplicates)}):")
        for path, funcs in duplicates.items():
            print(f"  - {path} -> {', '.join(funcs)}")
    else:
        print("\n✅ No duplicate route paths found")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Total routes defined: {len(routes)}")
    print(f"  Total url_for references: {len(url_for_refs)}")
    print(f"  Missing routes: {len(missing_routes)}")
    print(f"  Duplicate routes: {len(duplicates)}")
    
    if missing_routes:
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        for missing in sorted(missing_routes):
            print(f"  - Add route for '{missing}' or update template references")
    
    return len(missing_routes) == 0 and len(duplicates) == 0

if __name__ == "__main__":
    success = check_routing_integrity()
    sys.exit(0 if success else 1)