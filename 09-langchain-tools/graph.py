# flake8: noqa
import os
import time
import random
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver

# Import our custom modules
from .database.db import choose_session
from .tools.tool import tools

# Load environment variables from .env file
load_dotenv()


class State(TypedDict):
    """
    State for the graph.
    Attributes:
        messages (list): A list of messages in the chat session.
    """
    messages: Annotated[list, add_messages]
    config: dict

# Initialize the chat model
llm = init_chat_model("openai:gpt-4.1-mini")  

# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)   


def chat_bot_node(state: State) -> str:
    """
    A node that processes the chat state and returns a response.
    Args:
        state (State): The current state of the chat session.
    Returns:
        str: A response based on the current state.
    """
    message = llm_with_tools.invoke(state['messages'])
    return {"messages": [message]}


# ToolNode to handle the tools
tool_node = ToolNode(tools)

# Create the graph builder
graph_builder = StateGraph(State)

# Add nodes to the graph
graph_builder.add_node("chat_bot", chat_bot_node)
graph_builder.add_node("tools", tool_node)

# Add edges to the graph
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges("chat_bot", tools_condition)
graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)


def compile_graph_with_checkpointer(checkpointer):
    """
    Compile the graph with a checkpointer to save the state of the graph.
    Args:
        checkpointer: The checkpointer to use for saving the state.
    Returns:
        The compiled graph with the checkpointer.
    """
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def main():
    """Run the graph."""

    # MongoDB URI
    DB_URI = os.environ.get("MONGODB_URI")

    if not DB_URI:
        raise ValueError("MONGODB_URI environment variable is not set.")

    # Welcome message
    print("=" * 60)
    print("🤖 Welcome to the AI Assistant with Personal Todos!")
    print("=" * 60)
    print("Available commands:")
    print("📝 Add todos: 'add a todo to buy groceries'")
    print("📋 View todos: 'show my todos' or 'list my tasks'")
    print("🗑️  Delete todo: 'delete the todo buy groceries'")
    print("🧹 Clear all: 'clear all my todos'")
    print("🌤️  Get weather: 'what's the weather in New York?'")
    print("🧮 Math: 'add 5 and 3'")
    print("=" * 60)

    # Choose or create session
    existing_session = choose_session()

    if existing_session:
        thread_id = existing_session
        print(f"\n✅ Resumed session: {thread_id}")
    else:
        # Create new session
        user_input = input(
            "\nEnter your name for the new session (or press Enter for auto-generated): ").strip()

        if user_input:
            # Use user's name as thread_id (sanitized)
            thread_id = user_input.replace(" ", "_").lower()
        else:
            # Generate a unique session ID using timestamp
            timestamp = int(time.time())
            random_num = random.randint(100, 999)
            thread_id = f"user_{timestamp}_{random_num}"

        print(f"✅ Created new session: {thread_id}")

    print(f"\n💬 Chat started! Type 'exit' or 'quit' to end the session.")
    print("-" * 50)

    # Configure the state with thread_id (session identifier)
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Use MongoDBSaver to save the state of the graph
    with MongoDBSaver.from_conn_string(
        DB_URI, 
        db_name="ai_agent",  # Use the database name 'ai_agent' for consistency
        collection_name="chat_checkpoints"  # Use a specific collection for chat history
    ) as mongodb_checkpointer:

        # Compile the graph with the MongoDB checkpointer
        graph_with_mongodb = compile_graph_with_checkpointer(
            mongodb_checkpointer)

        while True:
            try:
                # Start the graph with an initial state
                user_input = input("You: ")

                # Exit condition
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting the chat. Goodbye!")
                    break
                
                # Create the initial state with user input and thread_id
                initial_state = State(
                    messages=[{"role": "user", "content": user_input}],
                    config=config["configurable"]
                )

                # Stream the graph events
                for event in graph_with_mongodb.stream(initial_state, config, stream_mode="values"):
                    if "messages" in event:
                        event["messages"][-1].pretty_print()
            except KeyboardInterrupt:
                print("\nExiting the chat. Goodbye!")
                break


main()
