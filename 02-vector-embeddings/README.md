# 02 - Vector Embeddings

## What are Vector Embeddings?

**Vector embeddings** are numerical representations of text (or other data) in a multi-dimensional space. They capture the semantic meaning of text, allowing machines to understand and compare content based on meaning rather than just exact word matches.

### Why are Embeddings Important?

- **Semantic Search**: Find similar content based on meaning, not just keywords
- **RAG Systems**: Essential for Retrieval-Augmented Generation
- **Similarity Detection**: Compare documents, sentences, or words mathematically
- **Machine Learning**: Convert text into features that ML models can process
- **Clustering**: Group similar content together

### How Embeddings Work

Text is converted into a vector (array of numbers) where:
- Similar meanings produce similar vectors
- The distance between vectors represents semantic similarity
- Typical dimensions: 384, 768, 1536, or more

**Example:**
```
"Hello world" → [0.123, -0.456, 0.789, ..., 0.234]
"Hi there"    → [0.134, -0.443, 0.801, ..., 0.221]  (close to "Hello world")
"Car engine"  → [-0.892, 0.234, -0.123, ..., 0.567] (far from greetings)
```

## About This Code

This implementation uses OpenAI's **text-embedding-3-small** model to generate vector embeddings from text.

### What the Code Does:

```python
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
print("Embedding length:", len(response.data[0].embedding))
```

### Key Features:

1. **OpenAI Embeddings**: Uses OpenAI's state-of-the-art embedding model
2. **text-embedding-3-small**: Efficient model with 1536 dimensions
3. **API Integration**: Simple REST API call for embedding generation
4. **Vector Output**: Returns a numerical vector representing the text

### Example Output:

```
Vector embeddings [0.123456, -0.234567, 0.345678, ..., 0.456789]
Embedding length: 1536
```

### Common Embedding Models:

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| text-embedding-3-small | 1536 | Cost-effective, general purpose |
| text-embedding-3-large | 3072 | Higher accuracy, more expensive |
| text-embedding-ada-002 | 1536 | Legacy model, still effective |

## Use Cases

1. **Semantic Search**: 
   ```
   Query: "How to cook pasta?"
   Matches: "Pasta cooking instructions", "Boiling noodles guide"
   ```

2. **Document Similarity**:
   - Compare resumes to job descriptions
   - Find duplicate content
   - Recommend similar articles

3. **Clustering**:
   - Group customer feedback by topic
   - Organize documents by theme

4. **RAG (Retrieval-Augmented Generation)**:
   - Store document embeddings in vector DB
   - Retrieve relevant context for LLM queries

## Running the Code

```bash
# Ensure OPENAI_API_KEY is set in .env file
python main.py
```

## Key Takeaways

- Embeddings convert text into mathematical representations
- Similar meanings have similar vectors (measured by cosine similarity or distance)
- Essential for building intelligent search and RAG systems
- OpenAI's embedding models are powerful and easy to use
- Embeddings enable semantic understanding beyond keyword matching
