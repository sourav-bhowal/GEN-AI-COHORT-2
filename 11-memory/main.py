# flake8: noqa
from mem0 import Memory
from dotenv import load_dotenv
import os
# from datetime import datetime
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI()

# Get the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

# Check if the API key is set
if not OPENAI_API_KEY or not QDRANT_URL or not QDRANT_API_KEY or not NEO4J_URI or not NEO4J_USERNAME or not NEO4J_PASSWORD:
    raise ValueError(
        "OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in the environment variables.")

# Configuration for the memory client
config = {
    "version": "v0.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small",
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4.1-mini",
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": QDRANT_URL,
            "api_key": QDRANT_API_KEY,
            "collection_name": "memory_collection",
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        },
    }
}

# Initialize the memory client with the configuration
mem_client = Memory.from_config(config)

# Function to chat with the memory client
def chat_with_memory():
    """
    Function to chat with the memory client.
    """
    while True:
        user_input = input("You👤: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        # Search for relevant memories
        # print("Searching for relevant memories...")
        relevant_memories = mem_client.search(
            query=user_input,
            user_id="user_2",  # Example user ID, can be dynamic
            limit=10,  # Limit the number of memories returned
        )

        # Format the memories for the system prompt
        memories = [f"ID: {mem['id']}, Content: {mem['memory']}" for mem in relevant_memories.get(
            "results", [])]

        # Create the system prompt with memories
        SYSTEM_PROMPT = f"""
            You are a helpful AI assistant that can recall past conversations.
            Your task is to assist the user based on their input and relevant past conversations. 
            You have access to the following memories:
            {', '.join(memories) if memories else 'No relevant memories found.'}
        """

        # Call the OpenAI API to get a response
        result = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
        )

        # Extract the AI response
        response = result.choices[0].message.content.strip()
        print(f"AI🤖: {response}")

        # Prepare the messages for memory
        messages = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response}
        ]

        # Add the conversation to memory (do it in a queue or background task in production)
        # print("Adding conversation to memory...")
        mem_client.add(
            messages,
            user_id="user_2",  # Example user ID, can be dynamic
            # metadata={"timestamp": datetime.now().isoformat()}
        )


# Start the chat with memory
chat_with_memory()
