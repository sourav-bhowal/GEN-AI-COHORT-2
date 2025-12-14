# 14 - MCP (Model Context Protocol) - Python

## What is MCP?

**Model Context Protocol (MCP)** is an open standard developed by Anthropic that enables AI applications to seamlessly connect to external data sources, tools, and services. It provides a universal protocol for:

- **Standardized Integration**: Single protocol for all tools
- **Tool Discovery**: Automatic detection of available capabilities  
- **Context Sharing**: Provide models with relevant external data
- **Bidirectional Communication**: Server-client architecture
- **Extensibility**: Easy to add new tools and data sources

### Why MCP?

Before MCP, each tool integration required custom code. MCP standardizes:
- How AI models discover available tools
- How tools are invoked
- How results are returned
- How context is shared

### MCP Architecture:

```
┌─────────────────┐
│   AI Client     │  (Claude, ChatGPT, Custom Apps)
│  (LLM + Chat)   │
└────────┬────────┘
         │
         │ MCP Protocol
         │ (stdio/HTTP)
         │
┌────────▼────────┐
│   MCP Server    │  (Your Custom Server)
│   - Tools       │
│   - Resources   │
│   - Prompts     │
└─────────────────┘
         │
         │
┌────────▼────────┐
│  External APIs  │  (Databases, APIs, File Systems)
│  Data Sources   │
└─────────────────┘
```

---

## MCP vs Regular APIs

| Aspect | Regular API | MCP |
|--------|-------------|-----|
| **Discovery** | Manual documentation | Automatic tool listing |
| **Integration** | Custom per tool | Standardized protocol |
| **Context** | Stateless | Context-aware |
| **AI-Friendly** | No | Yes (designed for LLMs) |
| **Multiple Tools** | Separate integrations | Single server, many tools |

---

## About This Implementation

This folder demonstrates MCP concepts, though the actual implementation is in `14-mcp-js` (TypeScript).

### Why TypeScript for MCP?

The official MCP SDK is primarily developed for TypeScript/JavaScript because:
- Native stdio transport support
- Better async handling
- npm ecosystem
- Official Anthropic support

However, Python MCP servers can be built using the Python SDK.

---

## MCP Components

### 1. **MCP Server**

The server exposes capabilities to AI clients:

```python
# Conceptual Python MCP server
from mcp import Server

server = Server(name="my-tools", version="1.0.0")

@server.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@server.tool()
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return fetch_weather(city)

# Start server
server.run()
```

### 2. **MCP Client**

AI applications connect to MCP servers:

```python
# Conceptual client usage
from mcp import Client

client = Client()
client.connect("my-tools-server")

# Discover available tools
tools = client.list_tools()
# [{"name": "add_numbers", ...}, {"name": "get_weather", ...}]

# Call a tool
result = client.call_tool("add_numbers", {"a": 5, "b": 3})
# result = 8
```

---

## MCP Server Capabilities

### 1. **Tools**

Functions that the AI can call:

```python
@server.tool()
def search_database(query: str) -> list:
    """Search the database with a query."""
    return db.search(query)
```

**Use Cases**:
- Database queries
- API calls
- File operations
- Calculations
- System commands

---

### 2. **Resources**

Data that the AI can access:

```python
@server.resource("file://documents/report.pdf")
def get_report():
    """Provide access to company report."""
    return read_file("report.pdf")
```

**Use Cases**:
- Documents
- Configuration files
- Knowledge bases
- Real-time data feeds

---

### 3. **Prompts**

Predefined prompts with context:

```python
@server.prompt("code_review")
def code_review_prompt(code: str):
    """Generate a code review prompt."""
    return f"Review this code:\n{code}\n\nProvide feedback on:"
           "\n- Code quality\n- Best practices\n- Security issues"
```

**Use Cases**:
- Templates
- Structured queries
- Context injection
- Guided interactions

---

## MCP Communication

### Transport Methods:

#### 1. **Stdio** (Standard Input/Output)
```python
# Server communicates via stdin/stdout
# Used for local processes
server.transport = StdioTransport()
```

**Best for**:
- Local tools
- CLI applications
- Desktop integrations

---

#### 2. **HTTP/SSE** (Server-Sent Events)
```python
# Server runs as HTTP endpoint
server.transport = HTTPTransport(port=3000)
```

**Best for**:
- Remote servers
- Web applications
- Cloud services

---

## Example: Building a Python MCP Server

```python
# example_mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

# Create server
app = Server("example-server")

@app.tool()
async def calculate_sum(numbers: list[int]) -> int:
    """Sum a list of numbers."""
    return sum(numbers)

@app.tool()
async def fetch_user_data(user_id: str) -> dict:
    """Fetch user data from database."""
    # Simulate database query
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }

@app.resource("config://app-settings")
async def get_app_settings():
    """Provide application settings."""
    return {
        "theme": "dark",
        "language": "en",
        "notifications": True
    }

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Connecting MCP Server to Claude Desktop

### 1. **Configure Claude Desktop**

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "python",
      "args": ["path/to/example_mcp_server.py"]
    }
  }
}
```

### 2. **Claude Auto-Discovers Tools**

When you open Claude Desktop:
```
Claude: "I can now use these tools from my-python-server:
- calculate_sum: Sum a list of numbers
- fetch_user_data: Fetch user data from database"
```

### 3. **Use Tools in Conversation**

```
You: "What's the sum of 1, 2, 3, 4, and 5?"

Claude: [Calls calculate_sum([1, 2, 3, 4, 5])]
       "The sum is 15."

You: "Get user data for user_123"

Claude: [Calls fetch_user_data("user_123")]
       "Here's the user data:
       Name: John Doe
       Email: john@example.com"
```

---

## MCP vs LangChain Tools

| Feature | LangChain Tools | MCP |
|---------|----------------|-----|
| **Scope** | Application-level | System-level |
| **Discovery** | Manual registration | Automatic |
| **Reusability** | Per-app | Cross-application |
| **Standard** | Framework-specific | Universal protocol |
| **Client Support** | LangChain only | Any MCP client |

---

## Use Cases

### 1. **Development Tools**
```python
@server.tool()
def run_tests(test_path: str):
    """Run unit tests and return results."""
    return subprocess.run(["pytest", test_path])
```

### 2. **Database Access**
```python
@server.tool()
def query_database(sql: str):
    """Execute SQL query safely."""
    return db.execute(sanitize(sql))
```

### 3. **File System**
```python
@server.tool()
def search_files(pattern: str):
    """Search files matching pattern."""
    return glob.glob(pattern)
```

### 4. **API Integration**
```python
@server.tool()
def call_external_api(endpoint: str, params: dict):
    """Make API request."""
    return requests.get(f"https://api.example.com/{endpoint}", params=params)
```

---

## Security Considerations

### 1. **Input Validation**
```python
@server.tool()
def delete_file(path: str):
    # Validate path
    if not path.startswith("/safe/directory/"):
        raise SecurityError("Invalid path")
    os.remove(path)
```

### 2. **Authentication**
```python
@server.tool()
async def access_sensitive_data(api_key: str):
    if not verify_api_key(api_key):
        raise AuthenticationError()
    return sensitive_data
```

### 3. **Rate Limiting**
```python
@server.tool()
@rate_limit(calls=10, period=60)
def expensive_operation():
    return perform_operation()
```

---

## MCP Server Examples

### Database Server:
```python
# mcp_database_server.py
@server.tool()
async def query(sql: str) -> list:
    """Execute SELECT query."""
    
@server.tool()
async def insert(table: str, data: dict) -> str:
    """Insert data into table."""
    
@server.resource("schema://tables")
async def list_tables() -> list:
    """List all database tables."""
```

### File System Server:
```python
# mcp_filesystem_server.py
@server.tool()
async def read_file(path: str) -> str:
    """Read file contents."""
    
@server.tool()
async def write_file(path: str, content: str):
    """Write content to file."""
    
@server.resource("directory://*")
async def list_directory(path: str) -> list:
    """List directory contents."""
```

---

## Python MCP Resources

- **Official SDK**: `mcp` Python package
- **Documentation**: https://modelcontextprotocol.io
- **Examples**: https://github.com/modelcontextprotocol/servers
- **Community**: Discord, GitHub Discussions

---

## Key Takeaways

- MCP is a universal protocol for AI tool integration
- Standardizes tool discovery, invocation, and responses
- Works with any MCP-compatible client (Claude, custom apps)
- Python SDK available for building servers
- Supports tools, resources, and prompts
- Transport via stdio or HTTP
- Essential for building reusable AI integrations
- See `14-mcp-js` folder for working TypeScript implementation

---

## Next Steps

- Implement Python MCP server
- Create custom tools for your use case
- Connect to Claude Desktop or custom clients
- Explore community MCP servers
- Build multi-server architectures
- Add authentication and security
- Deploy to production environments
