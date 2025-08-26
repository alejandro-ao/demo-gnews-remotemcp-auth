#!/usr/bin/env python3
"""
Test script for GNews MCP Server
Run this to verify the server is working correctly
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the current directory to the path to import main
sys.path.insert(0, str(Path(__file__).parent))

from main import mcp, get_api_key


async def test_server():
    """Test the GNews MCP server functionality"""
    print("🧪 Testing GNews MCP Server")
    print("=" * 50)
    
    # Test 1: Check API key
    print("\n1. Testing API key configuration...")
    try:
        api_key = get_api_key()
        print(f"✅ API key found: {api_key[:8]}...")
    except ValueError as e:
        print(f"❌ API key error: {e}")
        print("💡 Please set GNEWS_API_KEY environment variable")
        return False
    
    # Test 2: Test tools are registered
    print("\n2. Testing tool registration...")
    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    expected_tools = ["search_news", "get_top_headlines"]
    
    for tool_name in expected_tools:
        if tool_name in tool_names:
            print(f"✅ Tool '{tool_name}' registered")
        else:
            print(f"❌ Tool '{tool_name}' not found")
            return False
    
    # Test 3: Test resources are registered
    print("\n3. Testing resource registration...")
    resources = await mcp.list_resources()
    resource_uris = [resource.uri for resource in resources]
    expected_resources = [
        "gnews://supported-languages",
        "gnews://supported-countries", 
        "gnews://query-syntax"
    ]
    
    for resource_uri in expected_resources:
        if resource_uri in resource_uris:
            print(f"✅ Resource '{resource_uri}' registered")
        else:
            print(f"❌ Resource '{resource_uri}' not found")
            return False
    
    # Test 4: Test resource content
    print("\n4. Testing resource content...")
    try:
        # Test supported languages resource
        result = await mcp.read_resource("gnews://supported-languages")
        content = result.contents[0].text if result.contents else ""
        if "English" in content and "Spanish" in content:
            print("✅ Supported languages resource working")
        else:
            print("❌ Supported languages resource content issue")
            
        # Test query syntax resource  
        result = await mcp.read_resource("gnews://query-syntax")
        content = result.contents[0].text if result.contents else ""
        if "AND" in content and "OR" in content:
            print("✅ Query syntax resource working")
        else:
            print("❌ Query syntax resource content issue")
    except Exception as e:
        print(f"❌ Resource test error: {e}")
        return False
    
    # Test 5: Test prompts
    print("\n5. Testing prompt registration...")
    prompts = await mcp.list_prompts()
    prompt_names = [prompt.name for prompt in prompts]
    
    if "create_news_search_prompt" in prompt_names:
        print("✅ News search prompt registered")
    else:
        print("❌ News search prompt not found")
        return False
    
    # Test 6: Test prompt execution
    try:
        result = await mcp.get_prompt("create_news_search_prompt", arguments={"topic": "AI"})
        if result.messages:
            print("✅ News search prompt working")
        else:
            print("❌ News search prompt not generating content")
    except Exception as e:
        print(f"❌ Prompt test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Server is ready to use.")
    print("\n💡 Next steps:")
    print("1. Add this server to your Claude Desktop config")
    print("2. Set the GNEWS_API_KEY environment variable")
    print("3. Start using the news search capabilities!")
    
    return True


def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required modules
    required_modules = ["mcp", "httpx", "pydantic"]
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError:
            print(f"❌ {module} not found - run: pip install {module}")
            return False
    
    # Check if we can import the main module
    try:
        import main
        print("✅ Main module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main module: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 GNews MCP Server Test Suite")
    print("=" * 50)
    
    # Test environment first
    if not test_environment():
        print("\n❌ Environment test failed")
        sys.exit(1)
    
    # Test server functionality
    try:
        result = asyncio.run(test_server())
        if result:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        sys.exit(1)
