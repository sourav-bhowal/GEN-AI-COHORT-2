from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Define the text to be embedded
text = "Hello world!"

# Create an embedding for a given text string
response = client.embeddings.create(
    input=text,
    model="text-embedding-3-small"
)

# Print the embedding result
print("Vector embeddings", response.data[0].embedding)

# Print the length of the embedding
print ("Embedding length:", len(response.data[0].embedding))