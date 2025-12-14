# 04 - Agentic AI

## What is Agentic AI?

**Agentic AI** refers to AI systems that can autonomously make decisions, use tools, and take actions to achieve goals. Unlike simple chatbots that only respond to queries, agents can:

- **Plan**: Break down complex tasks into steps
- **Act**: Use external tools and APIs
- **Observe**: Process results and adjust strategy
- **Iterate**: Continue until goal is achieved

### Key Components of an AI Agent:

1. **Planning**: Reasoning about what steps to take
2. **Tools/Actions**: Functions the agent can call (APIs, databases, system commands)
3. **Observation**: Processing tool outputs
4. **Memory**: Context from previous interactions
5. **Decision Making**: Choosing which tool to use next

## About This Code

This implementation creates an AI agent that can:
- **Get Weather Information**: Fetch current weather from wttr.in API
- **Run System Commands**: Execute Windows PowerShell commands
- **Plan and Execute**: Use JSON-based reasoning to decide actions

### Architecture:

```
User Query → Agent Plans → Agent Selects Tool → Executes Tool → Agent Responds
```

### What the Code Does:

```python
# Available tools
available_tools = {
    "get_weather": get_weather,      # Fetches weather from API
    "run_command": run_command        # Runs system commands
}

# Agent reasoning loop:
1. "plan" step - Agent thinks about what to do
2. "action" step - Agent selects a tool and arguments
3. Execute the tool
4. "response" step - Agent provides final answer
```

### Key Features:

#### 1. **Weather Tool**
```python
def get_weather(location: str):
    url = f"https://wttr.in/{location}?format=%C+%t"
    response = requests.get(url)
    return f"The weather in {location} is {response.text.strip()}."
```

#### 2. **Command Execution Tool**
```python
def run_command(command: str):
    print(f"Running command: {command}")
    res = os.system(command)  # Executes Windows command
    return res
```

#### 3. **Agent Reasoning Loop**
```python
while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=conversation_history,
        response_format={"type": "json_object"}
    )
    
    # Agent decides: plan, action, or response
    if response_json.get("step") == "plan":
        # Agent is thinking
        continue
    
    elif response_json.get("step") == "action":
        # Agent chooses a tool
        tool = response_json["tool"]
        args = response_json["args"]
        # Execute tool
        result = available_tools[tool](**args)
        continue
    
    elif response_json.get("step") == "response":
        # Agent provides final answer
        break
```

### System Prompt Structure:

```python
SYSTEM_PROMPT = """
You are a helpful assistant that provides information about the weather.
You can answer questions about current weather conditions...

Rules:
1. Always provide accurate and up-to-date weather information.
2. Give in JSON format.
3. If you don't know the answer, say "I don't know".

Available tools:
- "get_weather": Fetch current weather data for a location
- "run_command": Execute system commands in Windows

Example:
User: What is the weather like in New York City today?
Output: {"step": "plan", "content": "I will use the 'get_weather' tool..."}
Output: {"step": "action", "tool": "get_weather", "args": {"location": "New York City"}}
Output: {"step": "response", "content": "The weather in New York City is sunny..."}
"""
```

## Example Interactions

### Weather Query:
```
User: What's the weather in London?
Agent Plan: I will fetch weather data for London
Agent Action: get_weather(location="London")
Agent Response: The weather in London is Cloudy with temperature 15°C
```

### System Command:
```
User: Create a new directory called "test_folder"
Agent Plan: I will use run_command to create the directory
Agent Action: run_command(command="mkdir test_folder")
Agent Response: Directory "test_folder" has been created
```

## Use Cases

1. **Weather Information**: Real-time weather queries
2. **System Automation**: File management, directory operations
3. **Multi-Step Tasks**: Complex queries requiring multiple tools
4. **Decision Making**: Agent decides which tool is appropriate

## Running the Code

```bash
python main.py
```

### Example Prompts:
- "What's the weather in Paris?"
- "Create a file called notes.txt"
- "What's the temperature in Tokyo?"
- "List files in the current directory"

## Key Concepts

### Agentic Loop:
```
┌─────────────────────────────────────────┐
│  1. User Input                          │
│  2. Agent Plans (step: "plan")          │
│  3. Agent Acts (step: "action")         │
│  4. Tool Executes                       │
│  5. Agent Observes Result               │
│  6. Agent Responds (step: "response")   │
└─────────────────────────────────────────┘
```

### JSON Response Format:
- **plan**: Agent's reasoning about what to do
- **action**: Tool selection and arguments
- **response**: Final answer to user

## Safety Considerations

⚠️ **Important**: The `run_command` tool can execute any system command, which poses security risks:
- Validate commands before execution
- Restrict to safe operations
- Consider sandboxing
- Never expose to untrusted users without restrictions

## Key Takeaways

- Agents can use external tools to accomplish tasks
- Planning and execution are separate steps
- JSON structured responses enable programmatic tool calling
- Agents iterate until the task is complete
- Tool availability defines agent capabilities
- Agentic AI is the foundation for autonomous systems
