# flake8: noqa
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage
from langchain.chat_models import init_chat_model
import os
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define a tool to run shell commands
@tool
def run_command(command: str):
    """
   executes command in the command line and returns the output.
    """
    result = os.system(command)
    return result

# List of available tools
available_tools = [run_command]

# Initialize the chat model and bind tools
chat_model = init_chat_model(model_provider="openai", model="gpt-5")
chat_model_with_tools = chat_model.bind_tools(available_tools)

# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Define the chatbot function
def chatbot_node(state: State):
    SYSTEM_PROMPT = SystemMessage(content="""
        You are an AI Coding assistant who takes an input from user and based on available tools 
        you choose the correct tool and execute the commands.
        Create a folder called "/test_folder" if it does not exist.
        You can create files for example "python.py", "main.cpp" and write the code created in a file called based on the user input.
        You can execute commands and help user with the output of the command.
        Always use the available tools to execute commands.
        If the user asks you to create a file, create the file in the "/test_folder" directory only.
        If the user asks you to create a folder, create the folder in the "/test_folder" directory only.
        If the user asks you to execute a command, execute the command in the "/test_folder" directory only.
        If the user asks you to write code, write the code in a file in the "/test_folder" directory only.
        If the user asks you to read a file, read the file from the "/test_folder" directory only.
        If the user asks you to delete a file, delete the file from the "/test_folder" directory only.
        If the user asks you to delete a folder, delete the folder from the "/test_folder" directory only.
        Always ensure that you are working within the "/test_folder" directory.
                                  
        Examples:
        User: Create a folder called "test_folder"
        AI: run_command("mkdir test_folder")
        User: Create a file called "hello.py" and write a python code to print "Hello, World!" in it.
        AI: run_command("echo 'print(\"Hello, World!\")' > test_folder/hello.py")
        User: Execute the file "hello.py"
        AI: run_command("python test_folder/hello.py")
        User: Delete the file "hello.py"
        AI: run_command("rm test_folder/hello.py")
        User: Delete the folder "test_folder"
        AI: run_command("rmdir test_folder")
    """)

    message = chat_model_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": message}

# Define the tool node with conditions
tool_node = ToolNode(tools=available_tools)

# Build the state graph
graph_builder = StateGraph(State)

# Define the flow of the graph
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)

# Add edges with conditions
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("chatbot", END)

# Compile the graph
graph = graph_builder.compile()