# 14-mcp-js - Model Context Protocol Server

## What is MCP?

**Model Context Protocol (MCP)** is an open standard developed by Anthropic that enables seamless integration between AI applications and external data sources. It provides a universal protocol for AI models to access tools, databases, APIs, and other resources in a standardized way.

### Key Benefits of MCP:
- **Standardized Communication**: Single protocol for connecting AI models to various data sources
- **Tool Integration**: Allow AI models to use external tools and services
- **Context Sharing**: Provide models with relevant context from multiple sources
- **Extensibility**: Easy to add new capabilities without modifying the core application
- **Interoperability**: Works across different AI platforms and applications

## About This Server

This project implements a simple MCP server with an addition tool that demonstrates the core concepts of MCP.

### Features:
- **Addition Tool**: A basic tool that adds two numbers together
- **Stdio Transport**: Uses standard input/output for communication
- **Type-Safe**: Built with TypeScript and Zod for runtime validation

### How It Works:

The server registers a tool called `add` that:
1. Accepts two numbers as input (`a` and `b`)
2. Returns their sum as text output
3. Can be invoked by any MCP-compatible client (like Claude Desktop)

```typescript
// Example from our server
server.registerTool(
  "add",
  {
    title: "Addition Tool",
    description: "Add two numbers",
    inputSchema: {
      a: z.number(),
      b: z.number(),
    },
  },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }],
  })
);
```

## Installation

To install dependencies:

```bash
bun install
```

## Running the Server

To run:

```bash
bun run index.ts
```

## Connecting to Claude Desktop

Add this to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "bun",
      "args": ["run", "d:\\ALL PROJECTS\\GEN AI COHORT 2\\14-mcp-js\\index.ts"]
    }
  }
}
```

Once connected, you can ask Claude to use the addition tool:
- "Can you add 25 and 17 using the add tool?"
- "Use the addition tool to calculate 100 + 250"

## MCP Server Components

1. **Server Instance**: Created with `McpServer` - defines the server name and version
2. **Tools**: Functions that the AI can call (like our `add` tool)
3. **Transport**: Communication layer (we use `StdioServerTransport` for stdin/stdout)
4. **Input Schema**: Defines and validates tool parameters using Zod

This project was created using `bun init` in bun v1.2.3. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
