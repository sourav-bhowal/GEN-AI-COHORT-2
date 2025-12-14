# 08 - LangGraph 2 (Checkpointing & Memory)

## What is Checkpointing in LangGraph?

**Checkpointing** is the ability to save and restore the state of a LangGraph workflow. This enables:

- **Persistent Memory**: Conversations continue across sessions
- **State Recovery**: Resume after interruptions
- **Multi-Turn Conversations**: Maintain context over multiple interactions
- **Debugging**: Inspect state at any point
- **Time Travel**: Rewind to previous states

### Without Checkpointing:
```
User: "My name is John"
Bot: "Hello John!"

[New session]
User: "What's my name?"
Bot: "I don't know your name."  ❌
```

### With Checkpointing:
```
User: "My name is John"
Bot: "Hello John!"

[New session - same thread_id]
User: "What's my name?"
Bot: "Your name is John!"  ✅
```

---

## About This Implementation

This project demonstrates **persistent conversation memory** using:
- **LangGraph Checkpointing**: Save state across interactions
- **MongoDB**: Store conversation history
- **Message History**: Automatic context management

### Key Features:

1. **Persistent State**: Conversations saved in MongoDB
2. **Thread Management**: Each conversation has a unique `thread_id`
3. **Message History**: Automatic tracking of messages
4. **Context Preservation**: LLM remembers previous messages

---

## Code Architecture

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

# State with message history
class State(TypedDict):
    messages: Annotated[list, add_messages]  # Auto-append messages

# Chat node
def chat_node(state: State) -> dict:
    response = llm.invoke(state['messages'])
    return {"messages": [response]}

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

# Compile with checkpointer
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)
    
    # Config with thread_id (like user_id/session_id)
    config = {"configurable": {"thread_id": "1"}}
    
    # Invoke with config
    result = graph.invoke(initial_state, config)
```

---

## Core Concepts

### 1. **Annotated Messages**

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

**What it does**:
- `add_messages`: Special annotation that **appends** messages instead of replacing
- Maintains conversation history automatically

**Example**:
```python
# Initial state
state = {"messages": [{"role": "user", "content": "Hi"}]}

# Node returns new message
return {"messages": [{"role": "assistant", "content": "Hello!"}]}

# Final state (messages are appended)
state = {
    "messages": [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"}  # Added, not replaced
    ]
}
```

---

### 2. **Checkpointer (MongoDBSaver)**

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

with MongoDBSaver.from_conn_string(DB_URI) as mongodb_checkpointer:
    graph = graph_builder.compile(checkpointer=mongodb_checkpointer)
```

**Purpose**:
- Saves graph state to MongoDB after each step
- Automatically loads previous state when resuming
- Enables persistence across sessions

**MongoDB Storage**:
```json
{
  "_id": "thread_1",
  "checkpoint": {
    "messages": [
      {"role": "user", "content": "Hi"},
      {"role": "assistant", "content": "Hello!"}
    ]
  },
  "metadata": {...}
}
```

---

### 3. **Thread ID (Session Management)**

```python
config = {
    "configurable": {
        "thread_id": "1"  # Unique identifier for this conversation
    }
}

result = graph.invoke(initial_state, config)
```

**Think of `thread_id` as**:
- Session ID
- Conversation ID
- User ID
- Any unique identifier for context grouping

**Example**:
```python
# User 1's conversation
config_user1 = {"configurable": {"thread_id": "user_1"}}

# User 2's conversation (separate context)
config_user2 = {"configurable": {"thread_id": "user_2"}}
```

---

### 4. **LLM Initialization**

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4.1-mini")
```

**Purpose**: Universal LLM initialization for LangChain
- Supports multiple providers (OpenAI, Anthropic, etc.)
- Consistent interface

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────┐
│ Session 1 - thread_id: "user_123"                   │
├─────────────────────────────────────────────────────┤
│ User: "My favorite color is blue"                   │
│ Bot: "Great! I'll remember that."                   │
│                                                     │
│ [State saved to MongoDB]                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Session 2 - thread_id: "user_123" (same user)       │
├─────────────────────────────────────────────────────┤
│ [State loaded from MongoDB]                         │
│                                                     │
│ User: "What's my favorite color?"                   │
│ Bot: "Your favorite color is blue!"                 │
│                                                     │
│ [Updated state saved to MongoDB]                    │
└─────────────────────────────────────────────────────┘
```

---

## Execution Flow

```python
def main():
    DB_URI = os.environ.get("MONGODB_URI")
    
    config = {
        "configurable": {
            "thread_id": "1"  # Conversation identifier
        }
    }
    
    with MongoDBSaver.from_conn_string(DB_URI) as mongodb_checkpointer:
        # Compile graph with MongoDB persistence
        graph = graph_builder.compile(checkpointer=mongodb_checkpointer)
        
        # Get user input
        user_query = input("Enter your query: ")
        
        # Create initial state
        initial_state = State(
            messages=[{"role": "user", "content": user_query}]
        )
        
        # Invoke graph with config (saves to MongoDB)
        result = graph.invoke(initial_state, config)
        
        # Bot response is now saved
        # Next invocation with same thread_id will load this history
```

---

## Running the Code

```bash
python chat.py
```

### Multi-Turn Conversation Example:

```
Session 1:
> Enter your query: My name is Alice and I love Python
Bot: Nice to meet you, Alice! Python is a great language.

Session 2 (same thread_id):
> Enter your query: What's my name?
Bot: Your name is Alice!

Session 3:
> Enter your query: What language do I like?
Bot: You love Python!
```

---

## Comparison: With vs Without Checkpointing

### Without Checkpointing:
```python
graph = graph_builder.compile()  # No checkpointer

# Each call is independent
result1 = graph.invoke({"messages": [{"role": "user", "content": "Hi"}]})
result2 = graph.invoke({"messages": [{"role": "user", "content": "What did I say?"}]})
# Bot doesn't remember "Hi" ❌
```

### With Checkpointing:
```python
graph = graph_builder.compile(checkpointer=mongodb_checkpointer)
config = {"configurable": {"thread_id": "1"}}

result1 = graph.invoke({"messages": [...]}, config)
result2 = graph.invoke({"messages": [...]}, config)
# Bot remembers previous messages ✅
```

---

## Key Advantages

| Feature | Without Checkpoint | With Checkpoint |
|---------|-------------------|-----------------|
| Memory | None | Persistent |
| Multi-turn | ❌ | ✅ |
| Resume | ❌ | ✅ |
| State inspection | ❌ | ✅ |
| Production-ready | ❌ | ✅ |

---

## MongoDB Schema

```javascript
// checkpoints collection
{
  "_id": "thread_1",
  "checkpoint": {
    "v": 1,
    "id": "checkpoint_id",
    "ts": "2024-01-01T00:00:00Z",
    "channel_values": {
      "messages": [
        {
          "role": "user",
          "content": "Hello"
        },
        {
          "role": "assistant",
          "content": "Hi there!"
        }
      ]
    }
  }
}
```

---

## Configuration Requirements

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
OPENAI_API_KEY=your_openai_key
```

---

## Use Cases

1. **Customer Support Chatbots**: Remember customer history
2. **Personal Assistants**: Long-term user preferences
3. **Multi-Session Workflows**: Resume incomplete tasks
4. **A/B Testing**: Compare different conversation paths
5. **Debugging**: Inspect exact state at any point

---

## Advanced Features (Not in this implementation)

- **Time Travel**: Go back to previous checkpoints
- **Branching**: Fork conversations at any point
- **Shared State**: Multiple threads accessing shared data
- **Custom Checkpointers**: Redis, PostgreSQL, etc.

---

## Key Takeaways

- Checkpointing enables persistent conversation memory
- `thread_id` identifies unique conversation contexts
- `add_messages` annotation automatically manages message history
- MongoDB stores all conversation state
- Essential for production chatbots and agents
- Foundation for complex multi-turn interactions
- Next steps: Add tools, conditional logic, and human-in-the-loop

---

## Next Steps

This checkpointing pattern is the **foundation** for:
- **09-langchain-tools**: Add tools with persistent memory
- **10-human-in-the-loop**: Interrupt and resume workflows
- **11-memory**: Advanced memory management with mem0
