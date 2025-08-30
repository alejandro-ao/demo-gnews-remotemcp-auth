# GNews API MCP Server

A Model Context Protocol (MCP) server built on [FastAPI](https://fastapi.tiangolo.com/) that provides access to the [GNews API](https://gnews.io/) for fetching news articles and headlines. The server now runs as a remote MCP server on top of a FastAPI app, supporting HTTP transport and modern authentication middleware. This enables AI applications to search for news, get trending headlines, and access comprehensive news data through a standardized interface with robust security.

## Features

### 🔧 Tools
- **`search_news`** - Search for news articles using keywords with advanced filtering
- **`get_top_headlines`** - Get trending news articles by category


## Installation & Setup

1. **Clone or download this repository**
  ```bash
  git clone <repository-url>
  cd gnews-server
  ```

2. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  # or using uv
  uv sync
  ```

3. **Get a GNews API key**
  - Visit [gnews.io](https://gnews.io/) 
  - Sign up for a free account
  - Get your API key from the dashboard

4. **Set up environment variables**
  ```bash
  export GNEWS_API_KEY="your_api_key_here"
  ```

5. **Configure authentication**
  - The server uses OAuth2 Bearer token authentication via ScaleKit. See `auth.py` for details.
  - Set required ScaleKit environment variables in your config (see `config.py`).

## Usage

### Running the Server

The server now runs as a FastAPI application with MCP protocol support and authentication middleware.

**Development mode:**
```bash
python main.py
```

**Using uv:**
```bash
uv run main.py
```

The server exposes MCP endpoints over HTTP, including a well-known OAuth-protected resource metadata endpoint at:
```
/.well-known/oauth-protected-resource/mcp
```


### Integration with Claude Desktop & Other MCP Clients

Add to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gnews": {
      "command": "python",
      "args": ["/absolute/path/to/gnews-server/main.py"],
      "env": {
        "GNEWS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

The server supports the standard MCP protocol and can be used with any MCP-compatible client. Use HTTP transport for remote connections, or stdio for local development.

### Integration with Other MCP Clients

The server supports the standard MCP protocol and can be used with any MCP-compatible client. Use the stdio transport for local connections.


## Authentication

The server uses OAuth2 Bearer token authentication via ScaleKit. All requests (except for well-known endpoints) require a valid token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Token validation and required scopes are handled by the `AuthMiddleware` (see `auth.py`). Unauthorized requests will receive a structured error response.

## API Reference

### Tools

#### `search_news`

Search for news articles using specific keywords.

**Parameters:**
- `q` (required): Search keywords with support for logical operators
- `lang` (optional): Language code (2 letters, e.g., "en", "es")
- `country` (optional): Country code (2 letters, e.g., "us", "gb") 
- `max` (optional): Number of articles to return (1-100, default: 10)
- `in` (optional): Search in specific fields: "title", "description", "content"
- `nullable` (optional): Allow null values for: "description", "content", "image"
- `from` (optional): Filter from date (ISO 8601 format)
- `to` (optional): Filter until date (ISO 8601 format)
- `sortby` (optional): Sort by "publishedAt" or "relevance"
- `page` (optional): Page number for pagination

**Example queries:**
```
- "Apple iPhone"
- "Apple AND iPhone"
- "Apple OR Microsoft" 
- "(Apple AND iPhone) OR Microsoft"
- "Apple NOT iPhone"
- "Apple iPhone 15" AND NOT "Apple iPhone 14"
```

**Returns:**
```json
{
  "success": true,
  "query": "search terms",
  "totalArticles": 150,
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description...",
      "content": "Full article content...",
      "url": "https://example.com/article",
      "image": "https://example.com/image.jpg",
      "publishedAt": "2024-01-01T12:00:00Z",
      "source": {
        "name": "Source Name",
        "url": "https://source.com"
      }
    }
  ],
  "parameters_used": {...}
}
```

#### `get_top_headlines`

Get current trending news articles by category.

**Parameters:**
- `category` (optional): News category (default: "general")
  - Available: "general", "world", "nation", "business", "technology", "entertainment", "sports", "science", "health"
- `lang` (optional): Language code
- `country` (optional): Country code
- `max` (optional): Number of articles (1-100, default: 10)
- `nullable` (optional): Allow null values
- `from` (optional): Filter from date
- `to` (optional): Filter until date  
- `q` (optional): Additional search keywords
- `page` (optional): Page number

**Returns:** Similar structure to `search_news` with category-specific trending articles.

### Resources

#### `gnews://supported-languages`
Returns a formatted list of all supported language codes and names.

#### `gnews://supported-countries`  
Returns a formatted list of all supported country codes and names.

#### `gnews://query-syntax`
Returns comprehensive documentation on search query syntax including logical operators, phrase search, and examples.

### Prompts

#### `create_news_search_prompt`
Creates a structured prompt for comprehensive news research on a specific topic.

**Parameters:**
- `topic` (required): The topic to research
- `days_back` (optional): Number of days to look back (default: 7)

## Advanced Query Syntax

The GNews API supports sophisticated search queries:

### Logical Operators
- **AND**: `Apple AND iPhone` (both terms must appear)
- **OR**: `Apple OR Microsoft` (either term can appear)  
- **NOT**: `Apple NOT iPhone` (exclude articles with "iPhone")

### Phrase Search
- **Exact phrases**: `"Apple iPhone 15"` (exact sequence)

### Operator Precedence
- OR has higher precedence than AND
- Use parentheses for grouping: `(Apple AND iPhone) OR Microsoft`

### Complex Examples
```
- Intel AND (i7 OR i9)
- (Windows 7) AND (Windows 10)
- "breaking news" AND NOT "rumor"
- (Tesla OR "electric vehicle") AND NOT "stock price"
```

## Supported Languages

Arabic (ar), Chinese (zh), Dutch (nl), English (en), French (fr), German (de), Greek (el), Hindi (hi), Italian (it), Japanese (ja), Malayalam (ml), Marathi (mr), Norwegian (no), Portuguese (pt), Romanian (ro), Russian (ru), Spanish (es), Swedish (sv), Tamil (ta), Telugu (te), Ukrainian (uk)

## Supported Countries

Australia (au), Brazil (br), Canada (ca), China (cn), Egypt (eg), France (fr), Germany (de), Greece (gr), Hong Kong (hk), India (in), Ireland (ie), Italy (it), Japan (jp), Netherlands (nl), Norway (no), Pakistan (pk), Peru (pe), Philippines (ph), Portugal (pt), Romania (ro), Russian Federation (ru), Singapore (sg), Spain (es), Sweden (se), Switzerland (ch), Taiwan (tw), Ukraine (ua), United Kingdom (gb), United States (us)


## Error Handling & Security

- **Authentication**: All endpoints (except well-known) require a valid OAuth2 Bearer token. Invalid or missing tokens result in a 401 Unauthorized response.
- **API Key Validation**: Checks for required environment variable
- **Parameter Validation**: Validates language codes, country codes, and numeric ranges
- **Network Error Handling**: Graceful handling of connection issues
- **API Error Responses**: Clear error messages from GNews API

Error responses include:
```json
{
  "success": false,
  "error": "Error description",
  "query": "original query",
  "parameters_used": {...}
}
```

## Rate Limits

GNews API has rate limits based on your subscription plan:
- **Free Plan**: 100 requests per day
- **Paid Plans**: Higher limits available

The server will return appropriate error messages if rate limits are exceeded.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **GNews API Documentation**: https://docs.gnews.io/
- **MCP Specification**: https://modelcontextprotocol.io/
- **Issues**: Please report bugs and feature requests through the repository's issue tracker


## Example Usage in Claude

After setting up the server, you can use it in Claude Desktop or any MCP client:

```
"Search for recent news about artificial intelligence developments in the last 3 days"
"Get the top technology headlines from the United States"
"Find news articles about climate change, but exclude articles about politics"
"Show me breaking news about electric vehicles from European sources"
```

The server will automatically use the appropriate tools and provide structured, comprehensive news results, with authentication and security enforced.