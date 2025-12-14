from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI()

SYSTEM_PROMPT= """
    You are an helpful AI assistant who is responsible for resolving user query.
    You work on start, plan, action, observe modes.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the appropriate tools and resources.
    Based on the tool selection you perform the actions.
    Wait for the observations and based on that from the tool call resolve the user query.

    
"""

response = openai_client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{
        "role": "user",
        "content": "Weather of jorhat?"
    }]
)

print(response.choices[0].message.content)