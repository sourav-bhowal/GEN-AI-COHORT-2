# 07 - LangGraph (Introduction)

## What is LangGraph?

**LangGraph** is a framework for building stateful, multi-actor applications with Large Language Models (LLMs). It extends LangChain with graph-based orchestration, allowing you to create complex AI workflows with:

- **State Management**: Track conversation and application state
- **Graph Structure**: Define nodes (actions) and edges (flow)
- **Conditional Logic**: Route based on state or conditions
- **Cycles**: Support iterative workflows
- **Persistence**: Save and restore state across sessions

### Why Use LangGraph?

- **Structured Workflows**: Define clear execution paths
- **State Persistence**: Maintain context across interactions
- **Complex Logic**: Handle multi-step reasoning
- **Visual Design**: Think in terms of graphs and flows
- **Debuggability**: Clear execution trace

### LangGraph Architecture:

```
START ──▶ [Node 1] ──▶ [Node 2] ──▶ END
              │            │
              │            ▼
              └────▶ [Node 3]
```

---

## About This Implementation

This is a **simple chatbot** built with LangGraph that demonstrates core concepts:
1. Defining state structure
2. Creating action nodes
3. Building a graph
4. Executing the workflow

### Code Structure:

```python
# 1. Define State
class State(TypedDict):
    query: str                    # User input
    llm_response: str | None      # Bot response

# 2. Define Action (Node)
def chat_bot(state: State) -> State:
    query = state['query']
    # Call OpenAI API
    llm_res = openai_client.chat.completions.create(...)
    state['llm_response'] = result
    return state

# 3. Build Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot_node", chat_bot)
graph_builder.add_edge(START, "chat_bot_node")
graph_builder.add_edge("chat_bot_node", END)

# 4. Compile and Run
graph = graph_builder.compile()
result = graph.invoke(initial_state)
```

---

## Core Concepts

### 1. **State (TypedDict)**

```python
class State(TypedDict):
    """
    Represents the state of the graph.
    """
    query: str              # The input query
    llm_response: str | None    # The response, initially None
```

**Purpose**:
- Holds data that flows through the graph
- Shared across all nodes
- Each node can read and modify state

**Think of it as**: A shared data object passed between functions

---

### 2. **Nodes (Actions/Functions)**

```python
def chat_bot(state: State) -> State:
    """
    A node that processes the query and returns a response.
    """
    query = state['query']
    
    # Call LLM
    llm_res = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ]
    )
    
    result = llm_res.choices[0].message.content
    state['llm_response'] = result
    
    return state  # Return updated state
```

**Key Points**:
- **Input**: Current state
- **Processing**: Perform action (LLM call, database query, etc.)
- **Output**: Updated state

---

### 3. **Graph Builder**

```python
# Create builder
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chat_bot_node", chat_bot)

# Define flow with edges
graph_builder.add_edge(START, "chat_bot_node")
graph_builder.add_edge("chat_bot_node", END)

# Compile into executable graph
graph = graph_builder.compile()
```

**Graph Flow**:
```
START ──▶ chat_bot_node ──▶ END
```

---

### 4. **Execution**

```python
# Initialize state
_state = {
    "query": "What is AI?",
    "llm_response": None
}

# Execute graph
result = graph.invoke(_state)

# Access results
print(result['llm_response'])
```

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────┐
│ 1. User enters query: "What is machine learning?"   │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 2. Initialize State:                                │
│    {                                                │
│      "query": "What is machine learning?",          │
│      "llm_response": None                           │
│    }                                                │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 3. Graph Execution:                                 │
│    START ──▶ chat_bot_node ──▶ END                 │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 4. chat_bot_node:                                   │
│    - Extracts query from state                      │
│    - Calls OpenAI API                               │
│    - Updates llm_response in state                  │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ 5. Final State:                                     │
│    {                                                │
│      "query": "What is machine learning?",          │
│      "llm_response": "Machine learning is..."       │
│    }                                                │
└─────────────────────────────────────────────────────┘
```

---

## System Message

```python
system_message = """
You are a helpful chat bot that answers user queries based on the input provided.
You will receive a query from the user and respond with relevant information.
Your responses should be concise and directly address the user's question.
"""
```

This defines the bot's behavior and personality.

---

## Running the Code

```bash
python graph.py
```

### Example Interaction:

```
Enter your query: What is LangGraph?

Response: LangGraph is a framework for building stateful, 
multi-actor applications with LLMs...
```

---

## Key Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **State** | Data structure | `{"query": "...", "llm_response": None}` |
| **Node** | Action/Function | `chat_bot(state)` |
| **Edge** | Flow connection | `START → node → END` |
| **Graph** | Complete workflow | Compiled executable |

---

## Advantages Over Simple Functions

### Traditional Approach:
```python
def chat(query):
    response = openai.chat.completions.create(...)
    return response
```

### LangGraph Approach:
```python
# ✅ State management built-in
# ✅ Can add more nodes easily
# ✅ Visual graph structure
# ✅ Supports complex flows
# ✅ Enables persistence (next lesson)
```

---

## Extending This Example

### Add Multiple Nodes:
```python
graph_builder.add_node("sentiment_node", analyze_sentiment)
graph_builder.add_node("chat_bot_node", chat_bot)
graph_builder.add_node("log_node", log_interaction)

graph_builder.add_edge(START, "sentiment_node")
graph_builder.add_edge("sentiment_node", "chat_bot_node")
graph_builder.add_edge("chat_bot_node", "log_node")
graph_builder.add_edge("log_node", END)
```

### Add Conditional Logic:
```python
def route_based_on_sentiment(state):
    if state['sentiment'] == 'negative':
        return "support_node"
    return "chat_bot_node"

graph_builder.add_conditional_edges(
    "sentiment_node",
    route_based_on_sentiment
)
```

---

## Use Cases

1. **Simple Chatbots**: Basic Q&A (as implemented)
2. **Multi-Step Workflows**: Research → Analyze → Summarize
3. **Conditional Flows**: Route based on user intent
4. **Agent Loops**: Plan → Execute → Validate → Repeat
5. **State Tracking**: Maintain conversation context

---

## Key Takeaways

- LangGraph provides structure for LLM applications
- **State** flows through **Nodes** connected by **Edges**
- Clear separation of data (State) and logic (Nodes)
- Easy to visualize and debug
- Foundation for complex agentic workflows
- Next steps: Add persistence, conditional routing, multi-agent systems

---

## Comparison

| Feature | Simple Function | LangGraph |
|---------|----------------|-----------|
| State Management | Manual | Built-in |
| Complex Flows | Difficult | Easy |
| Visualization | No | Yes |
| Persistence | Manual | Built-in |
| Scalability | Limited | High |

---

This implementation is the **foundation** for more advanced LangGraph patterns covered in subsequent lessons (checkpointing, tools, conditional edges, etc.).
