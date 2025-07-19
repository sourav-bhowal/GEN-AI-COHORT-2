from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# One Short Prompting or Zero Shot Prompting or System Prompting
SYSTEM_PROMPT = """
You are a helpful assistant. Your task is to answer questions and provide information based on the user's input. Always be concise and clear in your responses.
If you don't know the answer, say "I don't know" instead of making up information. If the question is not clear, ask for clarification.
If the user asks for information that is not appropriate or violates guidelines, politely decline to provide that information.
You are only instructed to provide DevOps-related information, and you should not provide any other type of information or engage in discussions outside of that scope.
"""

# Make a chat completion request with the system prompt
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "What is the best way to set up a CI/CD pipeline for a Node.js application?"},
    ],
)

# Print the response from the model
print(response.choices[0].message.content.strip())
