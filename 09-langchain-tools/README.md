# 09 - LangChain Tools (AI Agent with Tools)

## What are LangChain Tools?

**LangChain Tools** are functions that AI agents can call to perform actions or retrieve information from external systems. They enable agents to:

- **Access External Data**: Databases, APIs, files
- **Perform Actions**: Create, update, delete records
- **Execute Tasks**: Send emails, make calculations
- **Interact with Systems**: Shell commands, web scraping

### Why Use Tools?

- **Extend LLM Capabilities**: Go beyond text generation
- **Real-World Integration**: Connect to actual systems
- **Stateful Operations**: Modify data, not just read
- **Personalization**: User-specific data and actions

---

## About This Implementation

This project builds a **personal AI assistant with persistent todos** using:
- **LangGraph**: Orchestration framework
- **MongoDB**: Store todos and conversation history
- **LangChain Tools**: Custom functions for todo management
- **Tool Calling**: Automatic tool selection by LLM

### Features:

1. **Add Todos**: Create new todo items
2. **View Todos**: List all your todos
3. **Delete Todos**: Remove specific items
4. **Clear All**: Delete all todos
5. **Weather**: Get weather information
6. **Math**: Perform calculations
7. **Session Management**: Resume previous conversations

---

## Project Structure

```
09-langchain-tools/
├── graph.py              # Main LangGraph orchestration
├── database/
│   └── db.py             # MongoDB connection & session management
├── tools/
│   └── tool.py           # Tool definitions
```

---

## Core Components

### 1. **Tool Definitions** (`tools/tool.py`)

Tools are defined using the `@tool` decorator:

```python
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated

@tool()
def add_todo(todo: str, state: Annotated[dict, InjectedState]):
    """
    This tool adds a todo item to the list of todos for the current user.
    Args:
        todo (str): The todo item to add.
        state: The current graph state containing the thread_id.
    Returns:
        str: A message confirming the addition of the todo item.
    """
    db = get_db_connection()
    thread_id = state["config"]["thread_id"]  # Get user session
    
    todo_doc = {
        "thread_id": thread_id,
        "todo": todo,
        "id": random.randint(1, 10000),
        "created_at": datetime.now(),
        "completed": False
    }
    
    db.todos.insert_one(todo_doc)
    return f"Todo '{todo}' added successfully."
```

#### Key Features:

**InjectedState**:
- Automatically injects graph state into the tool
- Access `thread_id` (user session) inside the tool
- No need to pass it manually

**Tool Decorator**:
- Converts function into LangChain tool
- Provides metadata for LLM
- Enables automatic tool calling

---

### 2. **Available Tools**

#### **Todo Management**:

```python
@tool()
def add_todo(todo: str, state: Annotated[dict, InjectedState]):
    """Add a todo item to the user's list."""
    # Stores in MongoDB with thread_id
    
@tool()
def get_todos(state: Annotated[dict, InjectedState]) -> str:
    """Retrieve all todos for the current user."""
    # Queries MongoDB by thread_id
    
@tool()
def delete_todo(todo: str, state: Annotated[dict, InjectedState]):
    """Delete a specific todo item."""
    # Removes from MongoDB
    
@tool()
def clear_all_todos(state: Annotated[dict, InjectedState]):
    """Delete all todos for the current user."""
    # Clears user's todo collection
```

#### **Utility Tools**:

```python
@tool()
def get_weather(location: str):
    """Get current weather for a location."""
    # Calls wttr.in API
    
@tool()
def add_numbers(a: float, b: float):
    """Add two numbers together."""
    # Simple calculation
```

---

### 3. **Graph with Tools** (`graph.py`)

```python
from langgraph.prebuilt import ToolNode, tools_condition

# State definition
class State(TypedDict):
    messages: Annotated[list, add_messages]
    config: dict

# Initialize LLM with tools
llm = init_chat_model("openai:gpt-4.1-mini")
llm_with_tools = llm.bind_tools(tools)  # Bind tools to LLM

# Chat node
def chat_bot_node(state: State) -> str:
    message = llm_with_tools.invoke(state['messages'])
    return {"messages": [message]}

# Create graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot_node)
graph_builder.add_node("tools", ToolNode(tools))  # Tool execution node

# Define edges with conditional routing
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges("chat_bot", tools_condition)  # Auto-route to tools
graph_builder.add_edge("tools", "chat_bot")  # Return to chat after tool use
graph_builder.add_edge("chat_bot", END)
```

#### **Key Concepts**:

**1. Bind Tools to LLM**:
```python
llm_with_tools = llm.bind_tools(tools)
```
- LLM can now "see" available tools
- LLM decides when to call tools
- Returns structured tool calls

**2. ToolNode**:
```python
graph_builder.add_node("tools", ToolNode(tools))
```
- Executes tool calls automatically
- Handles errors
- Returns results to chat node

**3. tools_condition**:
```python
graph_builder.add_conditional_edges("chat_bot", tools_condition)
```
- Checks if LLM wants to call a tool
- Routes to `tools` node if yes
- Routes to `END` if no

---

## Workflow Visualization

```
┌──────────────────────────────────────────────────┐
│  User: "Add a todo to buy groceries"             │
└──────────────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │   START             │
        └─────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │   chat_bot node     │
        │ (LLM with tools)    │
        └─────────────────────┘
                    │
              [LLM decides]
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│ Call Tool?   │   NO   │     END      │
│     YES      │───────▶│              │
└──────────────┘        └──────────────┘
        │
        ▼
┌──────────────────────┐
│   tools node         │
│ (Execute add_todo)   │
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│   chat_bot node      │
│ (Format response)    │
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│       END            │
│ "Todo added!"        │
└──────────────────────┘
```

---

## Database Schema (`database/db.py`)

### MongoDB Collections:

#### **todos**:
```javascript
{
  "_id": ObjectId("..."),
  "thread_id": "user_123",
  "todo": "Buy groceries",
  "id": 4523,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "completed": false
}
```

#### **checkpoints** (from LangGraph):
```javascript
{
  "_id": "user_123",
  "checkpoint": {
    "messages": [
      {"role": "user", "content": "Add todo: buy milk"},
      {"role": "assistant", "content": "Todo added!"}
    ]
  }
}
```

### Session Management:

```python
def get_user_sessions():
    """Get all unique thread_ids from todos and checkpoints."""
    sessions = set()
    
    # Get sessions from todos
    todo_sessions = db.todos.distinct("thread_id")
    sessions.update(todo_sessions)
    
    # Get sessions from checkpoints
    checkpoint_sessions = db.checkpoints.distinct("thread_id")
    sessions.update(checkpoint_sessions)
    
    return list(sessions)

def choose_session():
    """Allow user to choose or create a session."""
    sessions = get_user_sessions()
    
    print("Found previous sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session}")
    
    print(f"{len(sessions) + 1}. Create new session")
    
    choice = input("Select: ").strip()
    # Return selected session or None for new
```

---

## Running the System

```bash
python graph.py
```

### Example Session:

```
==========================================================
🤖 Welcome to the AI Assistant with Personal Todos!
==========================================================
Available commands:
📝 Add todos: 'add a todo to buy groceries'
📋 View todos: 'show my todos' or 'list my tasks'
🗑️  Delete todo: 'delete the todo buy groceries'
🧹 Clear all: 'clear all my todos'
🌤️  Get weather: 'what's the weather in New York?'
🧮 Math: 'add 5 and 3'
==========================================================

Found previous sessions:
1. alice_2024
2. bob_work
3. Create new session

Select: 3
Enter your name: john_personal

✅ Created new session: john_personal

💬 Chat started! Type 'exit' to end.
--------------------------------------------------

You: add a todo to call dentist
🤖: Todo 'call dentist' added successfully!

You: what are my todos?
🤖: Your todos for john_personal:
- call dentist

You: what's the weather in London?
🤖: The weather in London is Cloudy with temperature 12°C.

You: add 25 and 17
🤖: The sum of 25 and 17 is 42.
```

---

## Key Features

### 1. **Automatic Tool Selection**

The LLM automatically decides which tool to use based on user intent:

```
User: "Add a todo"        → add_todo tool
User: "Show my todos"     → get_todos tool
User: "Weather in Paris"  → get_weather tool
User: "What is 5 + 3?"    → add_numbers tool
```

### 2. **Session Persistence**

- Each user has a unique `thread_id`
- Todos are stored per user
- Conversation history maintained
- Resume previous sessions

### 3. **Tool Chaining**

Multiple tools can be called in sequence:

```
User: "Add todo to buy milk, then show me all my todos"

1. Calls add_todo("buy milk")
2. Calls get_todos()
3. Returns combined response
```

---

## Configuration

```env
MONGODB_URI=mongodb+srv://...
OPENAI_API_KEY=your_key
```

---

## Use Cases

1. **Personal Task Manager**: Todo lists per user
2. **Customer Service**: User-specific data retrieval
3. **Automation**: Execute actions based on conversation
4. **Information Retrieval**: Weather, calculations, searches
5. **Workflow Automation**: Multi-step processes

---

## Key Takeaways

- Tools extend LLM capabilities beyond text generation
- `@tool` decorator makes functions callable by LLMs
- `InjectedState` provides access to graph state
- `ToolNode` + `tools_condition` enable automatic tool routing
- Session management (`thread_id`) enables personalization
- MongoDB stores both todos and conversation history
- LLMs intelligently select appropriate tools
- Essential pattern for production AI assistants

---

## Next Steps

This implementation demonstrates **basic tool use**. Advanced patterns include:
- **10-human-in-the-loop**: User approval before tool execution
- **11-memory**: Long-term memory beyond conversation
- **12-advance-rags**: Multi-query and advanced retrieval
