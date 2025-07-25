import os
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Vector Embeddings using OpenAI
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# Create a Qdrant Vector Store from an existing collection
vector_db = QdrantVectorStore.from_existing_collection(
    url=os.environ.get("QDRANT_URL"),
    collection_name="genai-rag",
    embedding=embedding_model,
    prefer_grpc=True,
    api_key = os.environ.get("QDRANT_API_KEY")
)

# Take user query
query = input("> ")

# Perform a similarity search in the vector store
results = vector_db.similarity_search(query)

# Print the results
# print("Search Results:", results)

context = "\n\n\n".join([result.page_content for result in results])

# Define the system prompt for the assistant
SYSTEM_PROMPT = f"""
    You are a helpful assistant that provides information based on the resume provided.
    You will be given a query and you should respond with relevant information from the resume.
    If the query is not related to the resume, you should respond with "I don't know".
    You should always provide a response based on the information available in the resume.
    Give precise and concise answers based on the context of the query.
    Here is the resume context:
    {context}
"""

# Create a chat completion using the OpenAI client
chat_completion  = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ],
    max_tokens=1000,
    temperature=0.0
)

# Print the chat completion response
print("Chat Response:", chat_completion.choices[0].message.content)