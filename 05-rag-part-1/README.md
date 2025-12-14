# 05 - RAG Part 1 (Retrieval-Augmented Generation)

## What is RAG?

**RAG (Retrieval-Augmented Generation)** is a technique that enhances LLM responses by retrieving relevant information from external knowledge bases before generating answers. Instead of relying solely on training data, RAG systems:

1. **Retrieve**: Find relevant documents from a knowledge base
2. **Augment**: Add retrieved context to the prompt
3. **Generate**: LLM produces informed responses

### Why Use RAG?

- **Up-to-date Information**: Access current data beyond training cutoff
- **Domain-Specific Knowledge**: Use private documents and data
- **Reduced Hallucinations**: Ground responses in actual documents
- **Citations**: Track which documents informed the answer
- **Cost-Effective**: No need to fine-tune models

### RAG Architecture:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   User      │───▶│   Vector      │───▶│    LLM      │
│   Query     │     │   Search     │     │  Response   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Vector DB  │
                    │  (Qdrant)    │
                    └──────────────┘
```

## About This Implementation

This project implements a complete RAG pipeline using:
- **LangChain**: Framework for RAG applications
- **Qdrant**: Vector database for storing embeddings
- **OpenAI Embeddings**: text-embedding-3-small model
- **PDF Processing**: Load and chunk PDF documents

### Two-Part System:

#### Part 1: Indexing (`main.py`)
Loads documents, creates embeddings, and stores in vector database

#### Part 2: Querying (`chat.py`)
Retrieves relevant context and generates answers

---

## File 1: `main.py` - Document Indexing

### What it Does:

```python
# 1. Load PDF document
loader = PyPDFLoader(file_path=pdf_path)
documents = loader.load()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Each chunk is 1000 characters
    chunk_overlap=200     # 200 character overlap between chunks
)
split_docs = text_splitter.split_documents(documents)

# 3. Create embeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# 4. Store in Qdrant vector database
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url=os.environ.get("QDRANT_URL"),
    collection_name="genai-rag",
    embedding=embedding_model,
    prefer_grpc=True,
    api_key=os.environ.get("QDRANT_API_KEY")
)
```

### Key Concepts:

#### 1. **Document Chunking**
- **Why**: LLMs have token limits; large documents must be split
- **chunk_size=1000**: Maximum characters per chunk
- **chunk_overlap=200**: Overlap ensures context isn't lost at boundaries

Example:
```
Document: "...end of chunk 1... middle text ...start of chunk 2..."
Chunk 1: "...end of chunk 1... middle text..."
Chunk 2: "...middle text ...start of chunk 2..."  (overlap preserved)
```

#### 2. **Vector Database (Qdrant)**
- Stores document embeddings
- Enables fast similarity search
- Scalable for large document collections

---

## File 2: `chat.py` - Query & Response

### What it Does:

```python
# 1. Connect to existing vector database
vector_db = QdrantVectorStore.from_existing_collection(
    url=os.environ.get("QDRANT_URL"),
    collection_name="genai-rag",
    embedding=embedding_model
)

# 2. Take user query
query = input("> ")

# 3. Perform similarity search
results = vector_db.similarity_search(query)

# 4. Combine retrieved contexts
context = "\n\n\n".join([result.page_content for result in results])

# 5. Create system prompt with context
SYSTEM_PROMPT = f"""
    You are a helpful assistant that provides information based on the resume provided.
    Here is the resume context:
    {context}
"""

# 6. Generate response
chat_completion = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
)
```

### Key Features:

#### 1. **Similarity Search**
```python
results = vector_db.similarity_search(query)
```
- Converts query to embedding
- Finds most similar document chunks
- Returns top matches (typically 3-5)

#### 2. **Context Augmentation**
```python
context = "\n\n\n".join([result.page_content for result in results])
```
- Combines retrieved chunks
- Provides relevant information to LLM
- Grounds the response in actual documents

#### 3. **Precise Responses**
```python
temperature=0.0  # Deterministic, factual responses
```

## Complete RAG Workflow

```
Step 1: Indexing (main.py)
├── Load resume.pdf
├── Split into chunks (1000 chars, 200 overlap)
├── Generate embeddings for each chunk
└── Store in Qdrant collection "genai-rag"

Step 2: Querying (chat.py)
├── User asks: "What is the candidate's experience?"
├── Convert query to embedding
├── Search vector DB for similar chunks
├── Retrieve top matching resume sections
├── Add retrieved context to system prompt
└── LLM generates informed response
```

## Example Interaction

### Indexing Phase:
```bash
python main.py
# Output: Vector store created and documents indexed successfully.
```

### Query Phase:
```bash
python chat.py
> What programming languages does the candidate know?

Chat Response: Based on the resume, the candidate is proficient in 
Python, JavaScript, TypeScript, and SQL. They have experience with 
frameworks like React, Node.js, and Django.
```

## Use Cases

1. **Resume Q&A**: Ask questions about a resume (as implemented)
2. **Documentation Search**: Query technical documentation
3. **Knowledge Bases**: Company policies, procedures
4. **Research Papers**: Scientific literature search
5. **Legal Documents**: Contract and legal text analysis

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| PDF Loader | PyPDFLoader | Extract text from PDF |
| Text Splitter | RecursiveCharacterTextSplitter | Chunk documents |
| Embeddings | OpenAI text-embedding-3-small | Convert text to vectors |
| Vector DB | Qdrant | Store and search embeddings |
| LLM | GPT-4.1-mini | Generate responses |
| Framework | LangChain | Orchestrate RAG pipeline |

## Running the Code

### Step 1: Index the Resume
```bash
python main.py
```

### Step 2: Query the System
```bash
python chat.py
```

## Configuration Requirements

Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

## Key Advantages

✅ **Accurate**: Responses based on actual documents  
✅ **Current**: Update knowledge base without retraining  
✅ **Traceable**: Can cite source documents  
✅ **Flexible**: Works with any document type  
✅ **Scalable**: Handle thousands of documents  

## Limitations

⚠️ **Retrieval Quality**: Depends on good chunking strategy  
⚠️ **Context Window**: Limited by LLM token limits  
⚠️ **Latency**: Additional time for retrieval step  
⚠️ **Cost**: Embedding + vector DB + LLM costs  

## Key Takeaways

- RAG combines retrieval with generation for informed responses
- Document chunking is critical for effective retrieval
- Vector databases enable fast semantic search
- Context augmentation grounds LLM responses in facts
- Suitable for dynamic, domain-specific knowledge
- Essential technique for production AI applications
