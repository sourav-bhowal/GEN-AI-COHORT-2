# 10 - Human-in-the-Loop (HITL)

## What is Human-in-the-Loop?

**Human-in-the-Loop (HITL)** is a pattern where AI agents pause execution to request human approval or input before proceeding. This enables:

- **Critical Decisions**: Human approval for important actions
- **Safety**: Prevent autonomous errors
- **Compliance**: Regulatory requirements for human oversight
- **Expert Input**: Domain knowledge when AI is uncertain
- **Debugging**: Inspect and modify agent behavior

### Why Use HITL?

- **Risk Mitigation**: Humans review before irreversible actions
- **Quality Control**: Verify agent decisions
- **Learning**: Collect human feedback for improvement
- **Trust**: Users feel in control
- **Flexibility**: Handle edge cases

---

## About This Implementation

This project demonstrates a **support ticket system** where:
1. User submits a query
2. Agent realizes it needs human help
3. Graph execution **interrupts** and saves state
4. Admin reviews and provides solution
5. Graph **resumes** with admin's input
6. Response delivered to user

### Architecture:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   User      │────▶│   AI Agent   │───▶│  Interrupt  │
│   Query     │     │ (Needs help) │     │ Save State  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Final     │◀───│  AI Agent    │◀───│   Admin    │
│  Response   │     │  (Resume)    │     │  Provides   │
└─────────────┘     └──────────────┘     └─────────────┘
```

---

## Core Concept: `interrupt()`

```python
from langgraph.types import interrupt, Command

@tool
def human_assistance(query: str) -> str:
    """
    Request human help for complex queries.
    This PAUSES the graph and saves state to database.
    """
    # Interrupt execution and wait for human input
    human_response = interrupt({"query": query})
    
    # After resume, return human's input
    return human_response["data"]
```

### What `interrupt()` Does:

1. **Pauses Execution**: Graph stops immediately
2. **Saves State**: Current state persisted to MongoDB
3. **Returns Control**: Graph exits (doesn't hang)
4. **Waits for Resume**: Human provides input later
5. **Continues Execution**: Graph picks up where it left off

---

## Implementation

### 1. **Tool Definition**

```python
@tool
def human_assistance(query: str) -> str:
    """
    A tool that simulates human assistance by interrupting the graph.
    """
    # Interrupt and save state
    human_response = interrupt({"query": query})
    
    # This line executes AFTER resume
    return human_response["data"]
```

### 2. **Graph Setup**

```python
# Bind tool to LLM
llm_with_tools = llm.bind_tools([human_assistance])

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("tools", ToolNode([human_assistance]))

graph_builder.add_edge(START, "chat_node")
graph_builder.add_conditional_edges("chat_node", tools_condition)
graph_builder.add_edge("tools", "chat_node")
graph_builder.add_edge("chat_node", END)

# Compile with MongoDB checkpointer (REQUIRED for HITL)
graph = graph_builder.compile(checkpointer=mongodb_checkpointer)
```

---

## Two-Part Workflow

### Part 1: User Mode (`user_main()`)

```python
def user_main():
    """
    User submits a query that requires human assistance.
    Graph will interrupt and wait.
    """
    config = {"configurable": {"thread_id": "12"}}
    
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        
        user_query = input("Enter your query: ")
        
        initial_state = State(
            messages=[{"role": "user", "content": user_query}]
        )
        
        # This will interrupt when agent calls human_assistance
        for event in graph.stream(initial_state, config):
            if "messages" in event:
                event["messages"][-1].pretty_print()
        
        # Graph pauses here - state saved to MongoDB
        print("⏸️ Waiting for admin response...")
```

---

### Part 2: Admin Mode (`admin_main()`)

```python
def admin_main():
    """
    Admin retrieves interrupted state and provides solution.
    Graph resumes with admin's input.
    """
    config = {"configurable": {"thread_id": "12"}}  # Same thread!
    
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        
        # Get current state
        current_state = graph.get_state(config)
        
        # Extract the user's query from interrupted state
        last_message = current_state.values['messages'][-1]
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        
        for call in tool_calls:
            if call["function"]["name"] == "human_assistance":
                args = json.loads(call["function"]["arguments"])
                user_query = args["query"]
                break
        
        print(f"User Query: {user_query}")
        
        # Admin provides solution
        solution = input("Enter your solution: ")
        
        # Resume graph with admin's input
        resume_command = Command(resume={"data": solution})
        
        # Graph continues from where it left off
        for event in graph.stream(resume_command, config):
            if "messages" in event:
                event["messages"][-1].pretty_print()
```

---

## Complete Example Flow

### Step 1: User Submits Query
```bash
python graph.py  # (user_main)

Enter your query: How do I configure SSL certificates for nginx?

🤖 Agent: "This requires specialized knowledge. Let me get human assistance."

[Calls human_assistance tool]
[Graph interrupts and saves state]

⏸️ Waiting for admin response...
```

**At this point:**
- Graph execution is **paused**
- State saved in MongoDB with `thread_id: "12"`
- Tool call recorded with user's query

---

### Step 2: Admin Reviews and Responds
```bash
python graph.py  # (admin_main)

[Loads state from MongoDB for thread_id: "12"]

User Query: How do I configure SSL certificates for nginx?

Enter your solution: To configure SSL in nginx:
1. Generate certificates: certbot --nginx
2. Edit /etc/nginx/sites-available/default
3. Add ssl_certificate and ssl_certificate_key directives
4. Run: sudo nginx -t && sudo systemctl reload nginx

[Graph resumes from interrupt point]

🤖 Agent: "Here's the solution from our expert:
To configure SSL in nginx:
1. Generate certificates: certbot --nginx
2. Edit /etc/nginx/sites-available/default
3. Add ssl_certificate and ssl_certificate_key directives
4. Run: sudo nginx -t && sudo systemctl reload nginx"
```

---

## Key Concepts

### 1. **Interrupt vs Pause**

```python
# ❌ This doesn't work (blocks forever)
response = input("Admin help: ")

# ✅ This works (saves state, exits cleanly)
response = interrupt({"query": query})
```

### 2. **Resume Command**

```python
# Resume with data
resume_command = Command(resume={"data": "admin's response"})

# The interrupted tool receives this data
graph.stream(resume_command, config)
```

### 3. **State Inspection**

```python
# Get current graph state
current_state = graph.get_state(config)

# Check if interrupted
if current_state.next:  # Has pending tasks
    print("Graph is interrupted")

# Access messages
messages = current_state.values['messages']

# Get pending tool calls
last_message = messages[-1]
tool_calls = last_message.additional_kwargs.get("tool_calls")
```

---

## MongoDB State Structure

When interrupted, MongoDB stores:

```javascript
{
  "_id": "thread_12",
  "checkpoint": {
    "values": {
      "messages": [
        {"role": "user", "content": "User query"},
        {
          "role": "assistant",
          "tool_calls": [{
            "function": {
              "name": "human_assistance",
              "arguments": "{\"query\": \"User query\"}"
            }
          }]
        }
      ]
    },
    "next": ["tools"],  // Indicates pending tool execution
    "tasks": [...]
  }
}
```

---

## Use Cases

1. **Customer Support**: Escalate complex queries to human agents
2. **Financial Approvals**: Human approval for transactions
3. **Medical Diagnosis**: Doctor review before final diagnosis
4. **Legal Review**: Lawyer approval for contracts
5. **Content Moderation**: Human review of flagged content
6. **Quality Assurance**: Expert validation of AI outputs

---

## Safety Patterns

### 1. **Approval Before Action**
```python
@tool
def delete_database(db_name: str):
    # Interrupt for approval
    approval = interrupt({"action": f"Delete {db_name}?"})
    
    if approval["data"] == "approved":
        # Perform deletion
        return "Database deleted"
    return "Action cancelled"
```

### 2. **Multi-Step Approval**
```python
# Approve plan
plan = agent.create_plan()
approved_plan = interrupt({"plan": plan})

# Execute approved steps
for step in approved_plan["data"]:
    execute(step)
```

---

## Configuration

```env
MONGODB_URI=mongodb+srv://...
OPENAI_API_KEY=your_key
```

---

## Running the System

### Terminal 1: User Mode
```bash
python graph.py
# Runs user_main()
# Submits query and waits
```

### Terminal 2: Admin Mode
```bash
python graph.py
# Runs admin_main()
# Reviews and responds
```

---

## Key Advantages

✅ **Non-Blocking**: User doesn't wait for admin  
✅ **Asynchronous**: Admin responds when available  
✅ **Persistent**: State saved in database  
✅ **Resumable**: Graph continues exactly where it stopped  
✅ **Auditable**: Full history of human interventions  

---

## Key Takeaways

- `interrupt()` pauses graph execution and saves state
- Requires checkpointer (MongoDB, Redis, etc.)
- `Command(resume={...})` provides data to interrupted tool
- Same `thread_id` used for submit and resume
- State inspection with `graph.get_state(config)`
- Essential for safety-critical applications
- Enables human oversight in autonomous systems
- Production-ready pattern for AI agents

---

## Next Steps

This HITL pattern enables:
- **11-memory**: Long-term memory with mem0
- **Multi-agent systems**: Agents requesting help from other agents
- **Approval workflows**: Chain multiple human reviews
