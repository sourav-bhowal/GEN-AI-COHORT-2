# 13 - Voice Agents

## What are Voice Agents?

**Voice agents** are AI systems that interact through speech instead of text. They combine:
- **Speech-to-Text (STT)**: Convert voice to text
- **AI Processing**: Understand and respond
- **Text-to-Speech (TTS)**: Convert response to voice
- **Tool Calling**: Execute actions based on voice commands

### Why Voice Agents?

- **Hands-Free**: Use while driving, cooking, etc.
- **Accessibility**: Easier for some users than typing
- **Natural**: Feels like talking to a person
- **Efficiency**: Faster than typing for many tasks

### Voice Agent Architecture:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Microphone │───▶│     STT     │───▶│   AI Agent │
│   (Audio)   │    │  (Google)   │    │ (LangGraph) │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │    Tools    │
                                       │  (Execute)  │
                                       └─────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Speaker   │◀───│     TTS     │◀───│  Response  │
│   (Audio)   │    │  (Optional) │    │    (Text)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## About This Implementation

This project creates a **voice-controlled coding assistant** that can:
- Listen to voice commands
- Create files and folders
- Write code
- Execute commands
- All through natural speech

### Features:

1. **Speech Recognition**: Google Speech API
2. **AI Agent**: LangGraph with tools
3. **Command Execution**: Shell command tool
4. **Coding Tasks**: File creation, code writing
5. **Directory Management**: Organized in `test_folder`

---

## Project Structure

```
13-voice-agents/
├── main.py              # Voice input handler
├── graph.py             # LangGraph agent with tools
├── harvard.wav          # Test audio file
```

---

## Implementation

### 1. **Voice Input** (`main.py`)

```python
import speech_recognition as sr
from graph import graph

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("Please say something...")
    
    # Capture audio from microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 2
        audio = recognizer.listen(source)
    
    try:
        # Convert speech to text
        stt = recognizer.recognize_google(audio)
        print(f"You said: {stt}")
        
        # Process with LangGraph agent
        for event in graph.stream(
            {"messages": [{"role": "user", "content": stt}]},
            stream_mode="values"
        ):
            if "messages" in event:
                event["messages"][-1].pretty_print()
    
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

main()
```

#### Key Components:

**Speech Recognizer**:
```python
recognizer = sr.Recognizer()
recognizer.adjust_for_ambient_noise(source)  # Filter background noise
recognizer.pause_threshold = 2               # Wait 2 seconds after speech ends
```

**Microphone Input**:
```python
with microphone as source:
    audio = recognizer.listen(source)
```

**Speech-to-Text**:
```python
text = recognizer.recognize_google(audio)  # Uses Google Speech API
```

---

### 2. **AI Agent** (`graph.py`)

```python
from langchain.tools import tool
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# Define command execution tool
@tool
def run_command(command: str):
    """Execute command in the command line and return the output."""
    result = os.system(command)
    return result

# Initialize LLM with tools
chat_model = init_chat_model(model_provider="openai", model="gpt-4")
chat_model_with_tools = chat_model.bind_tools([run_command])

# State definition
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Chatbot node
def chatbot_node(state: State):
    SYSTEM_PROMPT = SystemMessage(content="""
        You are an AI Coding assistant who executes commands based on user input.
        
        Rules:
        - Create all files/folders in "/test_folder" directory
        - Use available tools to execute commands
        - Support file creation, code writing, command execution
        
        Examples:
        User: "Create a folder called test_folder"
        AI: run_command("mkdir test_folder")
        
        User: "Create hello.py and write Hello World code"
        AI: run_command("echo 'print(\"Hello, World!\")' > test_folder/hello.py")
        
        User: "Run hello.py"
        AI: run_command("python test_folder/hello.py")
    """)
    
    message = chat_model_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": message}

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", ToolNode(tools=[run_command]))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
```

---

## Complete Workflow

```
┌─────────────────────────────────────────────────┐
│  1. User speaks: "Create a Python file that     │
│     prints Hello World"                         │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  2. Microphone captures audio                   │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  3. Google Speech API converts to text:         │
│     "Create a Python file that prints           │
│      Hello World"                               │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  4. LangGraph agent processes request           │
│     - Understands: Create file + Write code     │
│     - Decides: Use run_command tool             │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  5. Tool execution:                             │
│     run_command("echo 'print(\"Hello, World!\")'│
│                  > test_folder/hello.py")       │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  6. Agent responds (text):                      │
│     "I've created hello.py with Hello World     │
│      code in test_folder"                       │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  7. (Optional) TTS converts response to speech  │
└─────────────────────────────────────────────────┘
```

---

## Example Voice Commands

### File Creation:
```
🎤 "Create a file called main.py"
🤖 Creates: test_folder/main.py
```

### Code Writing:
```
🎤 "Write a Python script that adds two numbers"
🤖 Creates: test_folder/add_numbers.py with code:
   def add(a, b):
       return a + b
   print(add(5, 3))
```

### Code Execution:
```
🎤 "Run the main.py file"
🤖 Executes: python test_folder/main.py
   Returns: Output of the script
```

### Folder Management:
```
🎤 "Create a folder called utils"
🤖 Creates: test_folder/utils/
```

### File Operations:
```
🎤 "Delete the file hello.py"
🤖 Executes: rm test_folder/hello.py
```

---

## Speech Recognition Library

### speech_recognition Features:

```python
import speech_recognition as sr

# Supported engines:
recognizer.recognize_google(audio)        # Google Speech API (Free)
recognizer.recognize_sphinx(audio)        # Offline (CMU Sphinx)
recognizer.recognize_whisper(audio)       # OpenAI Whisper (Local)
recognizer.recognize_google_cloud(audio)  # Google Cloud (Paid)
recognizer.recognize_azure(audio)         # Microsoft Azure (Paid)
```

### Configuration Options:

```python
# Adjust for ambient noise
recognizer.adjust_for_ambient_noise(source, duration=1)

# Energy threshold (sensitivity)
recognizer.energy_threshold = 4000

# Pause threshold (seconds of silence)
recognizer.pause_threshold = 2

# Phrase time limit (max recording time)
audio = recognizer.listen(source, phrase_time_limit=5)
```

---

## Testing with Audio File

```python
# Instead of microphone, use audio file
with sr.AudioFile('harvard.wav') as source:
    audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    print(f"Transcription: {text}")
```

---

## Running the System

### Prerequisites:
```bash
pip install SpeechRecognition pyaudio
```

### Run Voice Agent:
```bash
python main.py
```

### Example Session:

```
Please say something...

[User speaks: "Create a Python file that prints my name"]

You said: Create a Python file that prints my name

🤖 Agent: I'll create a Python file for you.

Tool Call: run_command("echo 'print(\"Your Name\")' > test_folder/print_name.py")

✅ File created: test_folder/print_name.py
```

---

## Adding Text-to-Speech (TTS)

To make the agent speak responses:

```python
from gtts import gTTS
import os

def text_to_speech(text: str):
    """Convert text to speech and play."""
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("start response.mp3")  # Windows
    # os.system("afplay response.mp3")  # macOS
    # os.system("mpg123 response.mp3")  # Linux

# In main.py after agent response:
response_text = event["messages"][-1].content
text_to_speech(response_text)
```

---

## Use Cases

1. **Coding Assistants**: Voice-controlled development
2. **Accessibility Tools**: Help for vision-impaired developers
3. **Hands-Free Development**: Code while doing other tasks
4. **Meeting Assistants**: Voice-activated note-taking
5. **Smart Home Integration**: Control development environment
6. **Voice-Activated Debugging**: Debug by speaking

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Background Noise** | `adjust_for_ambient_noise()` |
| **Accents** | Use Whisper (better multilingual) |
| **Network Dependency** | Use offline Sphinx or local Whisper |
| **Latency** | Local speech models (Whisper) |
| **Privacy** | Offline speech recognition |

---

## Advanced Features

### 1. **Wake Word Detection**:
```python
# Listen for "Hey Agent" before activating
def listen_for_wake_word():
    while True:
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        if "hey agent" in text.lower():
            return True
```

### 2. **Continuous Listening**:
```python
def continuous_listen():
    with sr.Microphone() as source:
        while True:
            audio = recognizer.listen(source)
            process_command(audio)
```

### 3. **Multi-Language Support**:
```python
# Detect language and respond accordingly
text = recognizer.recognize_google(audio, language='es-ES')  # Spanish
```

---

## Configuration

```env
OPENAI_API_KEY=your_key
```

---

## Key Takeaways

- Voice agents enable hands-free AI interaction
- **Speech Recognition**: Convert voice to text (Google, Whisper)
- **LangGraph**: Process commands and execute tools
- **Tool Calling**: Execute system commands via voice
- Natural interface for coding and development tasks
- Combine STT + AI Agent + TTS for full voice experience
- Essential for accessibility and convenience
- Production-ready with proper error handling

---

## Next Steps

- **14-mcp**: Model Context Protocol servers
- Add TTS for voice responses
- Implement wake word detection
- Multi-language support
- Voice authentication
- Emotion detection from voice
