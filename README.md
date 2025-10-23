# Vertex AI Search Python Integration

A comprehensive Python client for Google Cloud Vertex AI Search API that supports search queries, SOW analysis, and document discovery with session management.

## Features

- 🔍 **Basic Search**: Perform search queries with full document metadata extraction
- 📊 **SOW Analysis**: Intelligent Statement of Work (SOW) detection and analysis
- 📄 **Document Discovery**: Find and analyze documents with Google Drive integration
- 🔗 **Session Management**: Track conversation context across queries
- 🛠️ **REST API Integration**: Reliable REST API implementation (gRPC has known issues)
- 📈 **Real Results**: Working with actual data from your Checkers data store

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud project with Vertex AI Search enabled
- Authenticated Google Cloud credentials

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd agent-search
   ./setup.sh
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv-312/bin/activate
   ```

3. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

4. **Configure your environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your project details if needed
   ```

### Basic Usage

```python
from vertex_search import VertexSearchClient

# Initialize the client
client = VertexSearchClient()

# Basic search
results = client.search("SOW")
for result in results:
    print(f"Title: {result.title}")
    print(f"Link: {result.uri}")
    print(f"Content: {result.content}")

# SOW Analysis
sow_analysis = client.search_and_analyze_sows(query="SOW", page_size=50)
analysis = sow_analysis['analysis']
print(f"Found {analysis['total_sows']} unique SOWs")

for sow_key, sow_info in analysis['sows'].items():
    print(f"{sow_key}: {sow_info['primary_title']}")
    print(f"  Documents: {len(sow_info['documents'])}")
    print(f"  Link: {sow_info['documents'][0]['link']}")

# Search for specific SOW
results = client.search("CHR_SOW#1")
print(f"Found {len(results)} documents for SOW#1")
```

## Examples

### 1. Basic Search

Run the basic search example:

```bash
python examples/basic_search.py
```

This example demonstrates:
- Simple search queries
- Document metadata extraction
- Google Drive link access

### 2. SOW Analysis

Run the SOW analysis test:

```bash
python test_sow_analysis.py
```

This example demonstrates:
- SOW detection and counting
- Document grouping by SOW
- Link extraction and previews

### 3. Conversational Search

Run the conversational search example:

```bash
python examples/conversational_search.py
```

This example demonstrates:
- "How many SOWs are there?" - SOW counting and analysis
- "Can you summarize CHR_SOW#1...?" - Specific SOW document discovery
- "Can you summarize another SOW?" - Available SOW listing

## API Reference

### VertexSearchClient

The main client class for interacting with Vertex AI Search.

#### Constructor

```python
VertexSearchClient(
    project_id: Optional[str] = None,
    engine_id: Optional[str] = None,
    location: str = "global",
    api_version: str = "v1alpha"
)
```

#### Methods

##### `search(query, **kwargs) -> List[SearchResult]`

Perform a basic search query using REST API.

**Parameters:**
- `query` (str): The search query
- `page_size` (int): Number of results to return (default: 10)
- `query_expansion` (bool): Enable query expansion (default: True)
- `spell_correction` (bool): Enable spell correction (default: True)
- `language_code` (str): Language code (default: "en-US")
- `time_zone` (str): User timezone (default: "America/Denver")
- `user_pseudo_id` (str, optional): User identifier
- `session_id` (str, optional): Session ID for conversational search

**Returns:** List of `SearchResult` objects with titles, links, content, and metadata

##### `search_and_analyze_sows(query, page_size) -> Dict[str, Any]`

Search for SOWs and provide detailed analysis.

**Parameters:**
- `query` (str): Search query (defaults to "SOW")
- `page_size` (int): Number of results to retrieve (default: 50)

**Returns:** Dictionary with SOW analysis including count, details, and document links

##### `extract_sows_from_results(results) -> Dict[str, Any]`

Extract and analyze SOW information from search results.

**Parameters:**
- `results` (List[SearchResult]): List of search results

**Returns:** Dictionary with SOW analysis including count and details

**Example:**
```python
# Get SOW analysis
sow_analysis = client.search_and_analyze_sows(query="SOW", page_size=50)
analysis = sow_analysis['analysis']

print(f"Found {analysis['total_sows']} unique SOWs")
for sow_key, sow_info in analysis['sows'].items():
    print(f"{sow_key}: {sow_info['primary_title']}")
    print(f"  Documents: {len(sow_info['documents'])}")
    print(f"  Link: {sow_info['documents'][0]['link']}")
```

### Data Models

#### SearchResult

Represents a search result from Vertex AI Search.

```python
@dataclass
class SearchResult:
    title: str
    content: str
    uri: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
```

#### AnswerResponse

Represents an answer generated by Vertex AI Search.

```python
@dataclass
class AnswerResponse:
    answer: str
    related_questions: List[str]
    search_results: List[SearchResult]
    session_id: Optional[str] = None
    query_id: Optional[str] = None
```

#### SessionInfo

Represents session information for conversational search.

```python
@dataclass
class SessionInfo:
    session_id: str
    user_pseudo_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    state: str = "IN_PROGRESS"
    turns: List[Dict[str, Any]] = None
```

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
# .env file
PROJECT_ID=your-project-id
ENGINE_ID=your-engine-id
LOCATION=global
API_VERSION=v1alpha
```

### Default Configuration

The client uses these defaults:
- **Project ID**: `622273141210`
- **Engine ID**: `checkers_1761176786564`
- **Location**: `global`
- **API Version**: `v1alpha`

## Error Handling

The client includes comprehensive error handling:

```python
try:
    results = client.search("your query")
except Exception as e:
    print(f"Search failed: {e}")
```

Common error scenarios:
- Authentication failures
- API quota exceeded
- Invalid query parameters
- Network connectivity issues

## Session Management

The client includes a built-in session manager for conversational search:

```python
# Create a new session
session_id = client.session_manager.create_session("user123")

# Get session information
session_info = client.get_session_info(session_id)

# List active sessions
sessions = client.list_sessions()

# List sessions for a specific user
user_sessions = client.list_sessions(user_pseudo_id="user123")
```

## Advanced Usage

### Custom Search Parameters

```python
# Custom search with specific parameters
results = client.search(
    query="machine learning",
    page_size=20,
    query_expansion=False,
    spell_correction=True,
    language_code="en-GB",
    time_zone="Europe/London",
    user_pseudo_id="user123"
)
```

### Answer Generation with Custom Settings

```python
# Custom answer generation
answer = client.get_answer(
    query="What is AI?",
    enable_related_questions=True,
    session_id="existing-session-id"
)
```

### Multi-turn Conversations

```python
# Start a conversation
session_id = None
queries = ["What is machine learning?", "Give me examples", "How do I get started?"]

for query in queries:
    response = client.conversational_search(
        query=query,
        session_id=session_id,
        start_new_session=(session_id is None)
    )
    session_id = response.session_id
    print(f"Answer: {response.answer}")
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   gcloud auth application-default login
   ```

2. **No Results Found**
   - Check that your data store has been populated
   - Verify your search query is appropriate
   - Ensure you're using the correct project/engine IDs

3. **gRPC vs REST API**
   - This implementation uses REST API (more reliable)
   - gRPC API has known issues with empty results
   - If you see 0 results, the REST API approach should work

4. **SOW Pattern Matching**
   - SOW detection uses regex pattern: `(CHR_)?SOW[_\s#]*([0-9X]+)`
   - Documents must have SOW references in titles
   - Some documents might not be detected if titles don't match pattern

### Debug Mode

Test your setup:

```bash
# Test basic functionality
python test_sow_analysis.py

# Test conversational search
python examples/conversational_search.py

# Debug search responses
python debug_search_clean.py
```

### Performance Notes

- **REST API**: More reliable, works with your data store
- **gRPC API**: Has issues with empty results (avoid for now)
- **SOW Analysis**: Processes 50+ documents efficiently
- **Google Drive Links**: All documents include working Google Drive URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [Google Cloud Vertex AI Search documentation](https://cloud.google.com/generative-ai-app-builder/docs)
- Open an issue in this repository
- Contact the maintainers

## Changelog

### Version 1.0.0
- Initial release with REST API implementation
- SOW analysis and document discovery
- Google Drive integration with working links
- Conversational search with SOW-specific queries
- Comprehensive examples and documentation

### Key Features
- ✅ **Working Search**: REST API implementation (gRPC has known issues)
- ✅ **SOW Analysis**: Intelligent SOW detection and grouping
- ✅ **Real Data**: Tested with Checkers data store (5 SOWs, 45+ documents)
- ✅ **Google Drive Links**: All documents include working URLs
- ✅ **Document Previews**: Content snippets and metadata extraction
