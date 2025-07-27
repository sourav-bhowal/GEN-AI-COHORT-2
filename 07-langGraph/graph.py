# flake8: noqa
# langGraph is a simple graph-based framework for building language models.
# It allows you to define states and actions, and connect them to create a graph.
# This is a basic example of how to create a graph with a state and an action.
# Steps to create a langGraph:
# 1. Define State (data).
# 2. Define Action (function). Input is State, output is State.
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI()

# System message to set the context for the chat bot
system_message = """
You are a helpful chat bot that answers user queries based on the input provided.
You will receive a query from the user and respond with relevant information.
Your responses should be concise and directly address the user's question.
"""


class State(TypedDict):
    """
    Represents the state of the graph.
    This is a placeholder for the actual state structure.
    """
    query: str  # The input query for the chat bot
    llm_response: str | None    # The response from the language model, initially None


def chat_bot(state: State) -> State:
    """
    A simple chat bot function that simulates a response based on the input state.
    It updates the state with a response to the query.
    """
    # Get the query from the state
    query = state['query']

    # Call the OpenAI API to process the query
    llm_res = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        max_tokens=1000,  # Limit the response length
        temperature=0.5  # Control the randomness of the response
    )

    # Extract the response from the OpenAI API result
    result = llm_res.choices[0].message.content

    # Update the state with the response
    state['llm_response'] = result

    # Return the updated state
    return state


# Create a state graph builder
# This will help in constructing the graph with nodes and edges
graph_builder = StateGraph(State)

# Build a node for the chat bot action
graph_builder.add_node("chat_bot_node", chat_bot)

# Connect the START node to the chat bot node
graph_builder.add_edge(START, "chat_bot_node")

# Connect the chat bot node to the END node
graph_builder.add_edge("chat_bot_node", END)

# Create the graph from the builder
# This compiles the defined nodes and edges into a usable graph
graph = graph_builder.compile()


def main():
    """
    Main function to run the graph with an initial state.
    This simulates a chat interaction with the bot.
    """
    # Get user input for the query
    user_query = input("Enter your query: ")

    # Initialize the state with the user's query
    _state = {
        "query": user_query,
        "llm_response": None  # Initialize the response as None
    }

    # Invoke the graph with the initial state
    graph_result = graph.invoke(_state)

    # Print the response from the chat bot
    print("Chat Bot Response:", graph_result)


main()
