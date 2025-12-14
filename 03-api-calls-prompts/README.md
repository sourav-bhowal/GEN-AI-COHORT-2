# 03 - API Calls & Prompting Techniques

## What is Prompt Engineering?

**Prompt engineering** is the practice of crafting effective inputs (prompts) to get desired outputs from Large Language Models. Different prompting strategies can dramatically improve model performance, reasoning ability, and output quality.

## Prompting Techniques Implemented

### 1. Chain of Thought Prompting (`chain_of_thought_prompting.py`)

**What it is**: Encourages the model to break down complex problems into step-by-step reasoning before providing the final answer.

**Benefits**:
- Improved accuracy on complex tasks
- Transparent reasoning process
- Better handling of multi-step problems
- Easier to debug and validate

**How it works in the code**:
```python
# The system prompt instructs the model to follow these steps:
1. Understand the Question
2. Break Down the Problem
3. Provide Step-by-Step Explanation
4. Conclude with the Answer

# Output format: JSON with "step" and "content" keys
{
    "step": "analyze",
    "content": "Breaking down the mathematical expression..."
}
{
    "step": "think",
    "content": "Calculating 4 / 6 gives 0.6667..."
}
{
    "step": "result",
    "content": "The final answer is 4.6667"
}
```

**Use Cases**:
- Mathematical problem solving
- Complex reasoning tasks
- Decision-making processes
- Multi-step instructions

---

### 2. Few-Shot Prompting (`few_shot_prompting.py`)

**What it is**: Provides the model with a few examples of the desired input-output pattern before the actual task.

**Benefits**:
- Teaches specific response formats
- Improves consistency
- Reduces ambiguity
- Better task understanding

**How it works in the code**:
```python
# System prompt includes examples:
Examples:
User: How do I set up a Docker container?
Assistant: [Docker setup instructions...]

User: What is the best way to deploy a web application?
Assistant: [Deployment methods...]

# The model learns from these patterns
# Specialized behavior: Only answers DevOps questions, "roasts" others
```

**Use Cases**:
- Teaching specific response styles
- Domain-specific chatbots
- Format standardization
- Task-specific assistants

---

### 3. One-Shot Prompting (`one_shot_prompting.py`)

**What it is**: Similar to few-shot, but provides only one example to demonstrate the desired behavior.

**Benefits**:
- Simpler than few-shot
- Still provides clear guidance
- Cost-effective (fewer tokens)
- Good for straightforward tasks

**Use Cases**:
- Simple pattern matching
- Format demonstration
- Basic task guidance

---

### 4. Persona-Based Prompting (`persona_based_prompting.py`)

**What it is**: Assigns a specific role or personality to the model to influence response style and content.

**Benefits**:
- Consistent tone and style
- Domain expertise simulation
- Engaging interactions
- Context-appropriate responses

**Examples of Personas**:
- "You are a senior DevOps engineer..."
- "You are a friendly teacher explaining to a 10-year-old..."
- "You are a formal business consultant..."
- "You are a creative writer with a poetic style..."

**Use Cases**:
- Customer service bots
- Educational assistants
- Domain experts (legal, medical, technical)
- Creative writing assistants

---

### 5. Self-Consistency Prompting (`self_consistency_prompting.py`)

**What it is**: Generates multiple reasoning paths for the same problem and selects the most consistent answer.

**Benefits**:
- Improved accuracy
- Reduced hallucinations
- Confidence estimation
- Error detection

**How it works**:
1. Generate multiple independent solutions
2. Compare the reasoning paths
3. Select the most common answer
4. Increase confidence in results

**Use Cases**:
- Critical decision-making
- Mathematical verification
- Fact-checking
- High-stakes applications

## About the Implementation

All scripts use:
- **OpenAI GPT-4.1-mini** model
- **Environment variables** for API keys (`.env` file)
- **JSON response format** for structured outputs
- **Conversation loops** for interactive experiences

### Common Code Pattern:

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """[Technique-specific instructions]"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    response_format={"type": "json_object"}  # For structured outputs
)
```

## Running the Code

```bash
# Chain of Thought
python chain_of_thought_prompting.py

# Few-Shot
python few_shot_prompting.py

# One-Shot
python one_shot_prompting.py

# Persona-Based
python persona_based_prompting.py

# Self-Consistency
python self_consistency_prompting.py
```

## Choosing the Right Technique

| Technique | Best For | Complexity |
|-----------|----------|------------|
| Chain of Thought | Complex reasoning, math problems | Medium |
| Few-Shot | Pattern learning, specific formats | Low |
| One-Shot | Simple demonstrations | Low |
| Persona-Based | Consistent tone, domain expertise | Low |
| Self-Consistency | Critical accuracy, verification | High |

## Key Takeaways

- Different tasks require different prompting strategies
- Proper prompt engineering can dramatically improve results
- Structured outputs (JSON) make processing easier
- System prompts set the context and behavior
- Experimentation is key to finding the best approach
