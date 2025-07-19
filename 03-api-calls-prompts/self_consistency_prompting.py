# Ask to every ai model (gemini, claude, gpt-4) the same question and return the most common answer
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

# Initialize Gemini client
gemini_client = genai.Client()

# Initialize Anthropic client
anthropic_client = Anthropic()

# Self consistency prompting system prompt
SYSTEM_PROMPT = """
You are a helpful AI assistant. Your task is to provide accurate and consistent answers to user questions. When responding, consider the following guidelines:
1. Provide clear and concise answers.
2. If the question is ambiguous, ask for clarification.
3. If you are unsure about an answer, acknowledge it and suggest possible alternatives.
4. Always strive to provide the most relevant and accurate information based on your training data.
5. If you encounter conflicting information, present the most common or widely accepted answer.
6. If a question is outside your knowledge base, politely inform the user.
7. Encourage users to ask follow-up questions for further clarification.
Examples:
User: What is the capital of France?
Assistant: The capital of France is Paris.
User: How do I implement a binary search algorithm?
Assistant: A binary search algorithm can be implemented by repeatedly dividing the search interval in half. If the value of the search key is less than the item in the middle of the interval, narrow the interval to the lower half. Otherwise, narrow it to the upper half. Repeat until the value is found or the interval is empty.
"""

# Function to get responses from different AI models
def get_responses(user_prompt):
    # Prepare messages for OpenAI
    openai_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    # Get response from OpenAI
    openai_response = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=openai_messages,
        max_tokens=150,
        temperature=0.7
    )
    openai_answer = openai_response.choices[0].message.content.strip()

    # Get response from Gemini
    gemini_response = gemini_client.models.generate_content(
        contents=f"{SYSTEM_PROMPT}\nUser: {user_prompt}\nAssistant:",
        model="gemini-2.5-flash",
    )
    gemini_answer = gemini_response.text.strip()

    # Get response from Anthropic
    anthropic_response = anthropic_client.messages.create(
        model="claude-2.0",
        max_tokens=150,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    anthropic_answer = anthropic_response.content

    return openai_answer, gemini_answer, anthropic_answer

# Main function to run the self-consistency prompting
def main():
    user_prompt = input("Please enter your question: ")
    
    # Get responses from different AI models
    openai_answer, gemini_answer, anthropic_answer = get_responses(user_prompt)
    
    # Print the answers from each model
    print("\nResponses from different AI models:")
    print(f"OpenAI: {openai_answer}")
    print(f"Gemini: {gemini_answer}")
    print(f"Anthropic: {anthropic_answer}")

    # Collect answers from all models and make a list
    answers = [openai_answer, gemini_answer, anthropic_answer]

    # Count the most common answer by using max with set and count
    most_common_answer = max(set(answers), key=answers.count)

    # Print the most common answer
    print("\nMost common answer:")
    print(most_common_answer)

