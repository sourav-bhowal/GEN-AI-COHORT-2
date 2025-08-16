# flake8: noqa
from json import tool
import json
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from dotenv import load_dotenv
from langchain_core.tools import tool
import os

# Load environment variables from .env file
load_dotenv()


@tool
def human_assistance(query: str) -> str:
    """
    A tool that simulates human assistance by returning the query.

    Args:
        query (str): The query to be processed.

    Returns:
        str: The processed query.
    """
    human_response = interrupt(
        {"query": query})  # This saves the state in DB and kills the graph
    return human_response["data"]


tools = [human_assistance]


class State(TypedDict):
    """
    A dictionary-like structure to hold the state of a chat session.

    Attributes:
        messages (list): A list of messages in the chat session.
    """
    # List of messages in the chat session (Annotated means to add or append msg in the list not replace)
    messages: Annotated[list, add_messages]


llm = init_chat_model("openai:gpt-4.1-mini")
llm_with_tools = llm.bind_tools(tools)


def chat_node(state: State) -> str:
    """
    A function that processes the chat state and returns a response.

    Args:
        state (State): The current state of the chat session.

    Returns:
        str: A response based on the current state.
    """

    # Invoke the language model with the current messages and return the response
    response = llm_with_tools.invoke(state['messages'])
    return {"messages": [response]}


# Make A state graph builder passing the State class
graph_builder = StateGraph(State)


# Build a node for the chat action
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "chat_node")
graph_builder.add_conditional_edges("chat_node", tools_condition)
graph_builder.add_edge("tools", "chat_node")
graph_builder.add_edge("chat_node", END)


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def user_main():
    """
    Main function to run the graph with an initial state.
    This simulates a chat interaction with the bot.
    """

    # MongoDB URI
    DB_URI = os.environ.get("MONGODB_URI")

    # Config the thread_id (its like user_id)
    config = {
        "configurable": {
            "thread_id": "12"
        }
    }

    # Invoke the graph with mongo db checkpointer to save the context in mongodb
    with MongoDBSaver.from_conn_string(DB_URI, db_name="human_in_the_loop") as mongodb_checkpointer:
        # Graph with MongoDB
        graph_with_mongodb = compile_graph_with_checkpointer(
            mongodb_checkpointer)

        # Prompt the user for input
        user_query = input("Enter your query: ")

        # Initialize the state with the user's query
        initial_state = State(
            messages=[{"role": "user", "content": user_query}])

        for event in graph_with_mongodb.stream(initial_state, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


user_main()


def admin_main():
    """
    Main function to run the graph in admin mode.
    This simulates a scenario where the admin can provide a solution to a user's query.
    It retrieves the last message from the graph state and allows the admin to input a solution.
    It then resumes the graph with the provided solution.
    """

    # MongoDB URI
    DB_URI = os.environ.get("MONGODB_URI")

    # Config the thread_id (its like user_id)
    config = {
        "configurable": {
            "thread_id": "12"
        }
    }

    # Invoke the graph with mongo db checkpointer to save the context in mongodb
    with MongoDBSaver.from_conn_string(DB_URI, db_name="human_in_the_loop") as mongodb_checkpointer:
        # Graph with MongoDB
        graph_with_mongodb = compile_graph_with_checkpointer(
            mongodb_checkpointer)

        # Get the current state of the graph
        current_state = graph_with_mongodb.get_state(config)

        # Retrieve the last message from the current state
        last_message = current_state.values['messages'][-1]

        # Extract the user query from the last message's tool calls
        tool_call = last_message.additional_kwargs.get("tool_calls", [])

        # Initialize user_query to None
        user_query = None

        # Check if the last message contains a tool call for human assistance
        for call in tool_call:
            if call.get("function", {}).get("name") == "human_assistance":
                args = call["function"].get("arguments", {}).get("query")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Error decoding JSON from user query.")

        print(f"User Query: {user_query}")

        # Prompt the admin for a solution
        solution = input("Enter your solution: ")

        # Resume the graph with the solution
        resume_command = Command(resume={"data": solution})

        # Stream the graph with the provided solution
        for event in graph_with_mongodb.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


admin_main()
