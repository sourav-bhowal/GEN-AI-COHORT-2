import json
from dotenv import load_dotenv
from openai import OpenAI
import requests
import os

load_dotenv()

client = OpenAI()


def run_command(command: str):
    print(f"Running command: {command}")
    res = os.system(command)
    print(f"Command exited with status: {res}")
    return res


def get_weather(location: str):
    url = f"https://wttr.in/{location}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {location} is {response.text.strip()}."

    return "I don't know the weather for that location."


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

SYSTEM_PROMPT = """
You are a helpful assistant that provides information about the weather.
You can answer questions about current weather conditions, forecasts, and related topics.

You should provide accurate and concise information based on the user's queries.
Select the most relevant information from your knowledge base and present it clearly.
You can also ask follow-up questions to clarify the user's needs or provide additional context.

Rules:
1. Always provide accurate and up-to-date weather information.
2. Give in JSON format.
3. If you don't know the answer, say "I don't know".

Available tools:
- "get_weather": Use this tool to fetch current weather data for a specific location.
- "run_command": Use this tool to execute system commands in windows. Use double quotes for the command string.

Example user query:
User Query: What is the weather like in New York City today?
Output: {{"step": "plan", "content": "The user is asking about the current weather in New York City. I will use the 'get_weather' tool to fetch this information."}}
Output: {{"step": "action", "tool": "get_weather", "args": {{"location": "New York City"}}}}
Output: {{"step": "response", "content": "The weather in New York City is sunny with a temperature of 75°F."}}
"""

USER_PROMPT = input("Enter your query about the weather: ")

# Array to hold the conversation history
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]


# Call the OpenAI API to get a response
while True:

    # Create a chat completion request with the conversation history
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=conversation_history,
        response_format={
            "type": "json_object",
        },
    )

    # Extract the response content
    response_content = response.choices[0].message.content

    # Append the response to the conversation history
    conversation_history.append(
        {"role": "assistant", "content": response_content})

    # Parse the response
    try:
        response_json = json.loads(response_content)
    except json.JSONDecodeError:
        print("Error parsing response JSON.")
        continue

    # Check the step in the response
    if response_json.get("step") == "plan":
        print(f"🧠 Planning: {response_json['content']}")
        continue

    # Check if the response indicates an action to be taken
    if response_json.get("step") == "action":
        tool = response_json["tool"]   # Extract the tool name
        args = response_json["args"]   # Extract the arguments for the tool

        print(f"🔧 Action: {tool} with args {args}")

        # Call the appropriate tool based on the action
        if tool == "get_weather":
            location = args["location"]
            weather_info = get_weather(location)
            conversation_history.append({"role": "assistant", "content": json.dumps(
                {"step": "response", "content": weather_info})})
            continue

        elif tool == "run_command":
            command = args["command"]
            run_command(command)
            conversation_history.append({
                "role": "assistant",
                "content": json.dumps({"step": "response", "content": f"The command `{command}` was executed."})
            })
            continue

    if response_json.get("step") == "response":
        print(f"Response: {response_json['content']}")

        # Append the final response to the conversation history
        conversation_history.append(
            {"role": "assistant", "content": response_json["content"]})
        break
