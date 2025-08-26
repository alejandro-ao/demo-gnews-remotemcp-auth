#!/usr/bin/env python3
"""
Example usage of the GNews MCP Server
This demonstrates how to use the server programmatically
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set example API key (replace with your actual key)
os.environ["GNEWS_API_KEY"] = "your_api_key_here"

from main import search_news, get_top_headlines


async def example_search():
    """Example of searching for news"""
    print("🔍 Example: Searching for AI news")
    print("=" * 50)
    
    try:
        result = await search_news(
            q="artificial intelligence",
            lang="en",
            max=5,
            sortby="publishedAt"
        )
        
        if result["success"]:
            print(f"Found {result['totalArticles']} articles")
            print("\nTop articles:")
            for i, article in enumerate(result["articles"][:3], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']['name']}")
                print(f"   Published: {article['publishedAt']}")
                print(f"   URL: {article['url']}")
        else:
            print(f"Search failed: {result['error']}")
            
    except Exception as e:
        print(f"Error: {e}")


async def example_headlines():
    """Example of getting top headlines"""
    print("\n📰 Example: Getting top technology headlines")
    print("=" * 50)
    
    try:
        result = await get_top_headlines(
            category="technology",
            country="us",
            max=3
        )
        
        if result["success"]:
            print(f"Found {result['totalArticles']} headlines")
            print(f"\nTop {result['category']} headlines:")
            for i, article in enumerate(result["articles"], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']['name']}")
                print(f"   Published: {article['publishedAt']}")
        else:
            print(f"Headlines failed: {result['error']}")
            
    except Exception as e:
        print(f"Error: {e}")


async def example_complex_search():
    """Example of complex search query"""
    print("\n🔍 Example: Complex search with logical operators")
    print("=" * 50)
    
    try:
        result = await search_news(
            q='(Tesla OR "electric vehicle") AND NOT "stock price"',
            lang="en",
            max=3,
            sortby="relevance"
        )
        
        if result["success"]:
            print(f"Found {result['totalArticles']} articles")
            print(f"\nQuery: {result['query']}")
            print("\nMatching articles:")
            for i, article in enumerate(result["articles"], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Description: {article['description'][:100]}...")
                print(f"   Source: {article['source']['name']}")
        else:
            print(f"Search failed: {result['error']}")
            
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples"""
    print("🚀 GNews MCP Server Examples")
    print("=" * 50)
    print("Note: You need a valid GNews API key for these examples to work")
    print("Set GNEWS_API_KEY environment variable with your API key")
    print("Get your free key at: https://gnews.io/")
    
    # Check if API key is set to a real value
    api_key = os.getenv("GNEWS_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("\n⚠️  No valid API key found!")
        print("These examples will fail without a real API key.")
        print("But you can still see the structure of the responses.")
        print("\nTo get started:")
        print("1. Visit https://gnews.io/ and sign up")
        print("2. Get your API key")
        print("3. Set it: export GNEWS_API_KEY='your_real_key'")
        print("4. Run this script again")
        return
    
    await example_search()
    await example_headlines()
    await example_complex_search()
    
    print("\n" + "=" * 50)
    print("✅ Examples completed!")
    print("\n💡 Integration with MCP clients:")
    print("- Add this server to Claude Desktop config")
    print("- Use with any MCP-compatible client")
    print("- Access via stdio transport")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Example error: {e}")
        print("\nThis might be due to missing API key or network issues")
