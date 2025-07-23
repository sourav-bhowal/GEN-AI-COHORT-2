import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the PDF file
pdf_path = Path(__file__).parent / "resume.pdf"

# Load the PDF document
loader = PyPDFLoader(file_path=pdf_path)

# Read the PDF
documents = loader.load()

# Chunk the document into smaller pieces (1000 characters each with 200 characters overlap)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Split the documents into chunks
split_docs = text_splitter.split_documents(documents)

# Vector Embeddings using OpenAI
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# Create a Qdrant Vector Store
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url=os.environ.get("QDRANT_URL"),
    collection_name="genai-rag",
    embedding=embedding_model,
    prefer_grpc=True,
    api_key = os.environ.get("QDRANT_API_KEY")
)

print("Vector store created and documents indexed successfully.")