# flake8: noqa
"""
Tool definitions for the AI Assistant.
Contains all the tools that can be used by the chat bot.
"""
from datetime import datetime
import random
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from ..database.db import get_db_connection
import math
from typing_extensions import Annotated


@tool()
def add_todo(todo: str, state: Annotated[dict, InjectedState]):
    """
    This tool adds a todo item to the list of todos for the current user.
    Args:
        todo (str): The todo item to add.
        state: The current graph state containing the thread_id.
    Returns:
        str: A message confirming the addition of the todo item.
    """
    if not todo:
        return "Please provide a valid todo item."

    try:
        db = get_db_connection()
        # Get thread_id from the injected state
        thread_id = state["config"]["thread_id"]

        # Ensure we have a valid thread_id
        if not thread_id or thread_id == "default":
            return "Error: No active user session found."

        # Insert the todo with the current thread_id
        todo_doc = {
            "thread_id": thread_id,
            "todo": todo,
            "id": math.floor(random.random() * 10000),  # Simple unique ID for the todo
            "created_at": datetime.now(),
            "completed": False
        }

        db.todos.insert_one(todo_doc)
        return f"Todo '{todo}' added successfully for user {thread_id}."

    except Exception as e:
        return f"Error adding todo: {str(e)}"


@tool()
def get_todos(state: Annotated[dict, InjectedState]) -> str:
    """
    This tool retrieves the list of todos for the current user and returns them as a string.
    Args:
        state: The current graph state containing the thread_id.
    Returns:
        str: A string containing all the todo items for the current user.
    """
    try:
        db = get_db_connection()
        # Get thread_id from the injected state
        thread_id = state["config"]["thread_id"]

        # Ensure we have a valid thread_id
        if not thread_id or thread_id == "default":
            return "Error: No active user session found."

        # Find todos for the current thread_id
        todos_cursor = db.todos.find({"thread_id": thread_id})
        todos_list = [doc["todo"] for doc in todos_cursor]

        if not todos_list:
            return f"No todos found for user {thread_id}."

        return f"Your todos for {thread_id}:\n" + "\n".join(f"- {todo}" for todo in todos_list)

    except Exception as e:
        return f"Error retrieving todos: {str(e)}"


@tool()
def delete_todo(todo: str, state: Annotated[dict, InjectedState]):
    """
    This tool deletes a specific todo item from the current user's list.
    Args:
        todo (str): The exact todo item to delete.
        state: The current graph state containing the thread_id.
    Returns:
        str: A message confirming the deletion or indicating if the todo wasn't found.
    """
    if not todo:
        return "Please provide a valid todo item to delete."

    try:
        db = get_db_connection()
        # Get thread_id from the injected state
        thread_id = state["config"]["thread_id"]

        # Ensure we have a valid thread_id
        if not thread_id or thread_id == "default":
            return "Error: No active user session found."

        # Delete the specific todo for this thread_id
        result = db.todos.delete_one({
            "thread_id": thread_id,
            "todo": todo
        })

        if result.deleted_count > 0:
            return f"Todo '{todo}' deleted successfully for user {thread_id}."
        else:
            return f"Todo '{todo}' not found in your list."

    except Exception as e:
        return f"Error deleting todo: {str(e)}"


@tool()
def clear_all_todos(state: Annotated[dict, InjectedState]):
    """
    This tool deletes all todos for the current user.
    Args:
        state: The current graph state containing the thread_id.
    Returns:
        str: A message confirming how many todos were deleted.
    """
    try:
        db = get_db_connection()
        # Get thread_id from the injected state
        thread_id = state["config"]["thread_id"]

        # Ensure we have a valid thread_id
        if not thread_id or thread_id == "default":
            return "Error: No active user session found."

        # Delete all todos for this thread_id
        result = db.todos.delete_many({"thread_id": thread_id})

        if result.deleted_count > 0:
            return f"Cleared {result.deleted_count} todos successfully for user {thread_id}."
        else:
            return f"No todos found to clear for user {thread_id}."

    except Exception as e:
        return f"Error clearing todos: {str(e)}"


@tool()
def mark_todo_completed(todo: str, state: Annotated[dict, InjectedState]):
    """
    This tool marks a specific todo item as completed for the current user.
    Args:
        todo (str): The exact todo item to mark as completed.
        state: The current graph state containing the thread_id.
    Returns:
        str: A message confirming the completion or indicating if the todo wasn't found.
    """
    if not todo:
        return "Please provide a valid todo item to mark as completed."

    try:
        db = get_db_connection()
        # Get thread_id from the injected state
        thread_id = state["config"]["thread_id"]

        # Ensure we have a valid thread_id
        if not thread_id or thread_id == "default":
            return "Error: No active user session found."

        # Update the specific todo for this thread_id
        result = db.todos.update_one(
            {"thread_id": thread_id, "todo": todo},
            {"$set": {"completed": True}}
        )

        if result.modified_count > 0:
            return f"Todo '{todo}' marked as completed successfully for user {thread_id}."
        else:
            return f"Todo '{todo}' not found in your list."

    except Exception as e:
        return f"Error marking todo as completed: {str(e)}"


@tool()
def get_weather(location: str):
    """
    This tool fetches the weather for a given location and returns a string describing the weather.
    Args:
        location (str): The location for which to get the weather.
    Returns:
        str: A string describing the weather in the specified location.
    """
    if not location:
        return "I don't know the weather for that location."

    url = f"https://wttr.in/{location}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {location} is {response.text.strip()}."

    return "I don't know the weather for that location."


@tool()
def add_numbers(a: int, b: int) -> int:
    """
    This tool adds two numbers and returns the result.
    Args:
        a (int): The first number.
        b (int): The second number.
    Returns:
        int: The sum of the two numbers.
    """
    return a + b


# Define the tools available for the chat bot
tools = [
    get_weather, 
    add_numbers, 
    add_todo, 
    get_todos, 
    delete_todo, 
    clear_all_todos, 
    mark_todo_completed
]
