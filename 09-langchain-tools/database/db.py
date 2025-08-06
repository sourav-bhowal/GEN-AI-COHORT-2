# flake8: noqa
"""
Database connection and configuration module.
Handles MongoDB connections and session management.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get MongoDB connection."""
    DB_URI = os.environ.get("MONGODB_URI")
    if not DB_URI:
        raise ValueError("MONGODB_URI environment variable is not set.")
    client = MongoClient(DB_URI)
    return client.ai_agent  # Use the database name 'ai_agent' for consistency


def get_user_sessions():
    """Get all unique thread_ids (user sessions) from both todos and chat history."""
    sessions = set()
    
    try:
        db = get_db_connection()
        
        # Get sessions from todos collection
        if 'todos' in db.list_collection_names():
            todo_sessions = db.todos.distinct("thread_id")
            sessions.update(todo_sessions)
        
        # Get sessions from MongoDB checkpointer collection
        # The checkpointer typically stores in 'checkpoints' collection
        if 'checkpoints' in db.list_collection_names():
            checkpoint_sessions = db.checkpoints.distinct("thread_id")
            sessions.update(checkpoint_sessions)
        
        # Also check for 'chat_checkpoints' if using custom collection name
        if 'chat_checkpoints' in db.list_collection_names():
            chat_sessions = db.chat_checkpoints.distinct("thread_id")
            sessions.update(chat_sessions)
            
        return list(sessions)
        
    except Exception as e:
        print(f"Error retrieving sessions: {str(e)}")
        return []


def choose_session():
    """Allow user to choose between new session or existing session."""
    sessions = get_user_sessions()

    if not sessions:
        print("No previous sessions found. Creating a new session...")
        return None

    print("Found previous sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session}")

    print(f"{len(sessions) + 1}. Create new session")

    try:
        choice = input("\nSelect a session number or press Enter for new session: ").strip()

        if not choice:
            return None

        choice_num = int(choice)
        if 1 <= choice_num <= len(sessions):
            return sessions[choice_num - 1]
        elif choice_num == len(sessions) + 1:
            return None
        else:
            print("Invalid choice. Creating new session...")
            return None
    except ValueError:
        print("Invalid input. Creating new session...")
        return None
