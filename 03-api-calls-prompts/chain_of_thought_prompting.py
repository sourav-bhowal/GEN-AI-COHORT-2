import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Chain of thought prompting system prompt
SYSTEM_PROMPT = """
You are a helpful assistant that provides detailed explanations and reasoning for your answers. When responding to questions, please follow these steps:
1. **Understand the Question**: Carefully read the question to ensure you understand what is being asked.
2. **Break Down the Problem**: If the question is complex, break it down into smaller parts to analyze each component.
3. **Provide a Step-by-Step Explanation**: Offer a detailed explanation of your reasoning process, including any relevant information or context.
4. **Conclude with the Answer**: After thorough reasoning, provide a clear and concise answer to the question.
5. **Example**: If applicable, provide an example to illustrate your explanation.
6. **Clarify Uncertainties**: If there are any uncertainties or assumptions, clarify them in your response.
This prompt is designed to encourage the model to think critically and provide comprehensive answers, rather than just short responses.

Output Format:
You will respond in a structured JSON format with the following keys:
- "step": A string indicating the current step in the reasoning process (e.g., "analyze", "think", "validate", "result").
- "content": A string containing the content of your response for that step.

Example Question:
Input: What is 2 + 4 / 6 * 4
Output: {{
    "step": "analyze",
    "content": "To solve the expression 2 + 4 / 6 * 4, we need to follow the order of operations (PEMDAS/BODMAS). First, we perform division and multiplication from left to right, then addition.",
}}
Output: {{
    "step": "think",
    "content": "Calculating 4 / 6 gives us approximately 0.6667. Next, we multiply this by 4, which results in approximately 2.6667. Finally, we add this to 2.",
}}
Output: {{
    "step": "validate",
    "content": "2 + 2.6667 equals approximately 4.6667.",
}}
Output: {{
    "step": "think",
    "content": "Therefore, the final answer is approximately 4.6667.",
}}
and so on...
"""

# Prompt the user for input
USER_PROMPT = input("Please enter your question: ")


# Array to hold the conversation
conversation = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]

# Start the conversation loop
while True:
    # Call the OpenAI API to get a response
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=conversation,
        response_format={"type": "json_object"},
    )

    # Append the assistant's response to the conversation
    conversation.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })

    # Parse the response to check the step
    parsed_response = json.loads(response.choices[0].message.content)

    # Check if the response indicates a step other than "result"
    if parsed_response.get("step") != "result":
        print(f"Step: {parsed_response['step']}, Content: {parsed_response['content']}")
        continue

    # If the step is "result", print the final answer and break the loop
    print(f"Final Answer: {parsed_response['content']}")
    break