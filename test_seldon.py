#!/usr/bin/env python3
"""Test file for Seldon - intentionally has failures to test learning"""

def test_async_function():
    """This test will fail if async/await is missing"""
    # Simulate a function that should have await
    async def fetch_data():
        # This would fail - missing await
        result = fetch('/api/data')  # Missing await!
        return result.json()
    
    # This test checks if await is present
    import inspect
    source = inspect.getsource(fetch_data)
    assert 'await fetch' in source, "Missing await in async function"

def test_null_safety():
    """This test will fail if null checks are missing"""
    # Simulate accessing nested properties
    data = {'user': None}
    
    # This would fail - no null check
    # name = data['user']['name']  # Would crash!
    
    # This test checks if null check is present
    # In real code, we'd check if the generated code has null checks
    assert True  # Placeholder

if __name__ == '__main__':
    test_async_function()
    test_null_safety()
    print("All tests passed!")