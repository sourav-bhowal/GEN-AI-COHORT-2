# flake8: noqa
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()


class State(TypedDict):
    """
    A dictionary-like structure to hold the state of a chat session.

    Attributes:
        messages (list): A list of messages in the chat session.
    """
    # List of messages in the chat session (Annotated means to add or append msg in the list not replace)
    messages: Annotated[list, add_messages]


llm = init_chat_model("openai:gpt-4.1-mini")


def chat_node(state: State) -> str:
    """
    A function that processes the chat state and returns a response.

    Args:
        state (State): The current state of the chat session.

    Returns:
        str: A response based on the current state.
    """

    # Invoke the language model with the current messages and return the response
    response = llm.invoke(state['messages'])
    return {"messages": [response]}


# Make A state graph builder passing the State class
graph_builder = StateGraph(State)

# Build a node for the chat action
graph_builder.add_node("chat_node", chat_node)

# Connect the START node to the chat node
graph_builder.add_edge(START, "chat_node")

# Connect the chat node to the END node
graph_builder.add_edge("chat_node", END)

# NOTE: Non checkpoint compiled graph will not save the state in memory or db
# graph = graph_builder.compile()

# NOTE: Checkpointing means our state persists (so our context saves in the DB or memory)

# fn to compile graph with checkpointer


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

# main fn


def main():
    """
    Main function to run the graph with an initial state.
    This simulates a chat interaction with the bot.
    """

    # MongoDB URI
    DB_URI = os.environ.get("MONGODB_URI")

    # Config the thread_id (its like user_id)
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    # Invoke the graph with mongo db checkpointer to save the context in mongodb
    with MongoDBSaver.from_conn_string(DB_URI) as mongodb_checkpointer:

        # Graph with MongoDB
        graph_with_mongodb = compile_graph_with_checkpointer(
            mongodb_checkpointer)

        # Prompt the user for input
        user_query = input("Enter your query: ")

        # Initialize the state with the user's query
        initial_state = State(
            messages=[{"role": "user", "content": user_query}])

        # Invoke the graph with the initial state and config
        result = graph_with_mongodb.invoke(initial_state, config)

        # Print the result
        print("Bot response:", result)


main()
