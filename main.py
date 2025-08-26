"""
GNews API MCP Server

This server provides access to the GNews API through the Model Context Protocol (MCP).
It exposes two main tools for fetching news data:
1. search_news - Search for news articles with specific keywords
2. get_top_headlines - Get trending news articles by category

Features:
- Full support for GNews API parameters
- Comprehensive error handling
- Input validation
- Proper response formatting
"""

import os
import logging
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import FastMCP


# Configure logging for STDIO transport (writes to stderr)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="gnews-server",
    instructions="A Model Context Protocol server for accessing GNews API. Provides tools to search news articles and get top headlines."
)

# Supported languages and countries (from GNews API documentation)
SUPPORTED_LANGUAGES = {
    "ar": "Arabic", "zh": "Chinese", "nl": "Dutch", "en": "English",
    "fr": "French", "de": "German", "el": "Greek", "hi": "Hindi",
    "it": "Italian", "ja": "Japanese", "ml": "Malayalam", "mr": "Marathi",
    "no": "Norwegian", "pt": "Portuguese", "ro": "Romanian", "ru": "Russian",
    "es": "Spanish", "sv": "Swedish", "ta": "Tamil", "te": "Telugu", "uk": "Ukrainian"
}

SUPPORTED_COUNTRIES = {
    "au": "Australia", "br": "Brazil", "ca": "Canada", "cn": "China",
    "eg": "Egypt", "fr": "France", "de": "Germany", "gr": "Greece",
    "hk": "Hong Kong", "in": "India", "ie": "Ireland", "it": "Italy",
    "jp": "Japan", "nl": "Netherlands", "no": "Norway", "pk": "Pakistan",
    "pe": "Peru", "ph": "Philippines", "pt": "Portugal", "ro": "Romania",
    "ru": "Russian Federation", "sg": "Singapore", "es": "Spain",
    "se": "Sweden", "ch": "Switzerland", "tw": "Taiwan", "ua": "Ukraine",
    "gb": "United Kingdom", "us": "United States"
}

CATEGORIES = [
    "general", "world", "nation", "business", "technology", 
    "entertainment", "sports", "science", "health"
]

class NewsResponse(BaseModel):
    """Represents a news API response"""
    totalArticles: int
    articles: List[dict]


def get_api_key() -> str:
    """Get the GNews API key from environment variables"""
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError(
            "GNEWS_API_KEY environment variable is required. "
            "Get your free API key from https://gnews.io/"
        )
    return api_key


async def make_gnews_request(endpoint: str, params: dict) -> dict:
    """Make a request to the GNews API"""
    api_key = get_api_key()
    
    # Add API key to parameters
    params["apikey"] = api_key
    
    # Base URL for GNews API
    base_url = "https://gnews.io/api/v4"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Making request to {endpoint} with params: {params}")
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved {data.get('totalArticles', 0)} articles")
                return data
            else:
                error_msg = f"GNews API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                
                logger.error(error_msg)
                raise Exception(error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"Network error connecting to GNews API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool()
async def search_news(
    q: str = Field(description="Search keywords. Use logical operators like AND, OR, NOT. Use quotes for exact phrases."),
    lang: Optional[str] = Field(default=None, description=f"Language code (2 letters). Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"),
    country: Optional[str] = Field(default=None, description=f"Country code (2 letters). Supported: {', '.join(SUPPORTED_COUNTRIES.keys())}"),
    max_articles: Optional[int] = Field(default=10, description="Number of articles to return (1-100)"),
    search_in: Optional[str] = Field(default=None, description="Search in specific fields: title, description, content (comma-separated)"),
    nullable: Optional[str] = Field(default=None, description="Allow null values for: description, content, image (comma-separated)"),
    date_from: Optional[str] = Field(default=None, description="Filter articles from this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    date_to: Optional[str] = Field(default=None, description="Filter articles until this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    sortby: Optional[Literal["publishedAt", "relevance"]] = Field(default="publishedAt", description="Sort by publication date or relevance"),
    page: Optional[int] = Field(default=1, description="Page number for pagination")
) -> dict:
    """
    Search for news articles using specific keywords.
    
    This tool allows you to search for news articles based on keywords with various
    filtering options including language, country, date range, and sorting preferences.
    
    Query Syntax Examples:
    - Simple search: "Apple iPhone"
    - Exact phrase: '"Apple iPhone 15"'
    - Logical operators: "Apple AND iPhone", "Apple OR Microsoft", "Apple NOT iPhone"
    - Complex queries: "(Apple AND iPhone) OR Microsoft"
    
    Returns a structured response with article details including title, description,
    content, URL, image, publishedAt, and source information.
    """
    
    # Validate parameters
    if lang and lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language '{lang}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
    
    if country and country not in SUPPORTED_COUNTRIES:
        raise ValueError(f"Unsupported country '{country}'. Supported countries: {', '.join(SUPPORTED_COUNTRIES.keys())}")
    
    if max_articles and (max_articles < 1 or max_articles > 100):
        raise ValueError("Max articles must be between 1 and 100")
    
    if page and page < 1:
        raise ValueError("Page must be 1 or greater")
    
    # Build request parameters
    params = {"q": q}
    
    if lang:
        params["lang"] = lang
    if country:
        params["country"] = country
    if max_articles:
        params["max"] = max_articles
    if search_in:
        params["in"] = search_in
    if nullable:
        params["nullable"] = nullable
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    if sortby:
        params["sortby"] = sortby
    if page:
        params["page"] = page
    
    try:
        result = await make_gnews_request("search", params)
        return {
            "success": True,
            "query": q,
            "totalArticles": result.get("totalArticles", 0),
            "articles": result.get("articles", []),
            "parameters_used": params
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": q,
            "parameters_used": params
        }


@mcp.tool()
async def get_top_headlines(
    category: Optional[Literal["general", "world", "nation", "business", "technology", "entertainment", "sports", "science", "health"]] = Field(
        default="general", 
        description="News category"
    ),
    lang: Optional[str] = Field(default=None, description=f"Language code (2 letters). Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"),
    country: Optional[str] = Field(default=None, description=f"Country code (2 letters). Supported: {', '.join(SUPPORTED_COUNTRIES.keys())}"),
    max_articles: Optional[int] = Field(default=10, description="Number of articles to return (1-100)"),
    nullable: Optional[str] = Field(default=None, description="Allow null values for: description, content, image (comma-separated)"),
    date_from: Optional[str] = Field(default=None, description="Filter articles from this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    date_to: Optional[str] = Field(default=None, description="Filter articles until this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ)"),
    q: Optional[str] = Field(default=None, description="Additional search keywords to filter headlines"),
    page: Optional[int] = Field(default=1, description="Page number for pagination")
) -> dict:
    """
    Get current trending news articles based on Google News ranking.
    
    This tool retrieves the top headlines for a specific category. The articles
    are selected based on Google News ranking algorithm, providing the most
    relevant and trending news for the chosen category.
    
    Available categories:
    - general: General news (default)
    - world: International news
    - nation: National news
    - business: Business and finance
    - technology: Technology and innovation
    - entertainment: Entertainment and celebrity news
    - sports: Sports news
    - science: Scientific discoveries and research
    - health: Health and medical news
    
    Returns a structured response with trending article details.
    """
    
    # Validate parameters
    if category and category not in CATEGORIES:
        raise ValueError(f"Unsupported category '{category}'. Supported categories: {', '.join(CATEGORIES)}")
    
    if lang and lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language '{lang}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
    
    if country and country not in SUPPORTED_COUNTRIES:
        raise ValueError(f"Unsupported country '{country}'. Supported countries: {', '.join(SUPPORTED_COUNTRIES.keys())}")
    
    if max_articles and (max_articles < 1 or max_articles > 100):
        raise ValueError("Max articles must be between 1 and 100")
    
    if page and page < 1:
        raise ValueError("Page must be 1 or greater")
    
    # Build request parameters
    params = {}
    
    if category:
        params["category"] = category
    if lang:
        params["lang"] = lang
    if country:
        params["country"] = country
    if max_articles:
        params["max"] = max_articles
    if nullable:
        params["nullable"] = nullable
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    if q:
        params["q"] = q
    if page:
        params["page"] = page
    
    try:
        logger.info(f"Getting top headlines for category '{category}' with params: {params}")
        result = await make_gnews_request("top-headlines", params)
        return {
            "success": True,
            "category": category or "general",
            "totalArticles": result.get("totalArticles", 0),
            "articles": result.get("articles", []),
            "parameters_used": params
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": category or "general",
            "parameters_used": params
        }


@mcp.resource("gnews://supported-languages")
def get_supported_languages() -> str:
    """Get the list of supported languages for GNews API"""
    languages_list = []
    for code, name in SUPPORTED_LANGUAGES.items():
        languages_list.append(f"  {code}: {name}")
    
    return f"""Supported Languages for GNews API:

{chr(10).join(languages_list)}

Usage: Use the 2-letter language code in the 'lang' parameter.
Example: lang="en" for English, lang="es" for Spanish
"""


@mcp.resource("gnews://supported-countries")  
def get_supported_countries() -> str:
    """Get the list of supported countries for GNews API"""
    countries_list = []
    for code, name in SUPPORTED_COUNTRIES.items():
        countries_list.append(f"  {code}: {name}")
    
    return f"""Supported Countries for GNews API:

{chr(10).join(countries_list)}

Usage: Use the 2-letter country code in the 'country' parameter.
Example: country="us" for United States, country="gb" for United Kingdom
"""


@mcp.resource("gnews://query-syntax")
def get_query_syntax_help() -> str:
    """Get help on query syntax for GNews API searches"""
    return """GNews API Query Syntax Guide:

BASIC SEARCH:
- Simple keywords: Apple iPhone
- Space acts as AND operator: Apple iPhone = Apple AND iPhone

PHRASE SEARCH:
- Exact phrases: "Apple iPhone 15"
- Use quotes for exact keyword sequence

LOGICAL OPERATORS:
- AND: Apple AND iPhone (ensure both keywords appear)
- OR: Apple OR Microsoft (either keyword can appear)
- NOT: Apple NOT iPhone (exclude articles with "iPhone")

OPERATOR PRECEDENCE:
- OR has higher precedence than AND
- Use parentheses for clarity: (Apple AND iPhone) OR Microsoft

SPECIAL CHARACTERS:
- Must be quoted if used: "Hello!", "Left - Right", "Question?"

EXAMPLE QUERIES:
- Microsoft Windows 10
- Apple OR Microsoft  
- Apple AND NOT iPhone
- (Windows 7) AND (Windows 10)
- "Apple iPhone 13" AND NOT "Apple iPhone 14"
- Intel AND (i7 OR i9)
- (Intel AND (i7 OR "i9-14900K")) AND NOT AMD AND NOT "i7-14700K"

IMPORTANT NOTES:
- Query must be URL-encoded when sent
- Cannot use special characters without quotes
- Logical operators are case-sensitive (use uppercase)
"""


@mcp.prompt()
def create_news_search_prompt(topic: str, days_back: int = 7) -> str:
    """Create a comprehensive news search prompt for a specific topic"""
    return f"""You are a news research assistant. Search for comprehensive news coverage about "{topic}" from the last {days_back} days.

Please use the search_news tool with the following approach:

1. First, search for recent articles about "{topic}" using:
   - Query: "{topic}"
   - Time range: from the last {days_back} days
   - Sort by: "publishedAt" for most recent news

2. Then, search for different perspectives using varied keywords:
   - Main topic variations
   - Related industry terms
   - Impact and analysis angles

3. Finally, search for any breaking news or developments using:
   - Query: "{topic}" AND ("breaking" OR "latest" OR "update")

After gathering the articles, please:
- Summarize the key developments
- Identify different perspectives or viewpoints
- Highlight any breaking news or recent updates
- Note any patterns or trends in the coverage

Use the get_top_headlines tool if this topic might be trending in specific categories like business, technology, or world news."""


def main():
    """Run the GNews MCP server"""
    logger.info("Starting GNews MCP Server...")
    
    # Check if API key is available
    try:
        get_api_key()
        logger.info("GNews API key found")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}", file=os.sys.stderr)
        return
    
    # Run the server using stdio transport
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
