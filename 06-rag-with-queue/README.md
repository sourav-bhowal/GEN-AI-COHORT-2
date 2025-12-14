# 06 - RAG with Queue

## What is RAG with Queue Architecture?

This implementation extends basic RAG with a **queue-based architecture** for handling document processing asynchronously. Instead of processing documents synchronously, documents are added to a queue and processed by background workers.

### Why Use a Queue?

- **Scalability**: Handle multiple document uploads simultaneously
- **Non-Blocking**: API responds immediately without waiting for processing
- **Reliability**: Failed jobs can be retried
- **Distributed**: Multiple workers can process jobs in parallel
- **Monitoring**: Track job status and progress

### Architecture:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client    │────▶│   FastAPI    │────▶│    Queue     │
│   Upload    │     │   Server     │     │   (Redis)    │
└─────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Worker     │
                                          │  Process     │
                                          └──────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Qdrant     │
                                          │  Vector DB   │
                                          └──────────────┘
```

## Project Structure

```
06-rag-with-queue/
├── main.py              # FastAPI entry point
├── server.py            # API endpoints
├── queue/
│   ├── connection.py    # Redis connection setup
│   └── worker.py        # Background job processor
```

## Components

### 1. `main.py` - Application Entry

```python
import uvicorn
from .server import app

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")
```

**Purpose**: Starts the FastAPI server on port 8000

---

### 2. `server.py` - FastAPI Server

**Key Features**:
- **Document Upload Endpoint**: Accept documents via HTTP
- **Queue Integration**: Add processing jobs to queue
- **Job Status**: Track processing status
- **Async Operations**: Non-blocking API responses

**Typical Endpoints** (based on common patterns):

```python
@app.post("/upload")
async def upload_document(file: UploadFile):
    # 1. Save uploaded file
    # 2. Add job to queue
    # 3. Return job ID immediately
    job = queue.enqueue(process_document, file_path)
    return {"job_id": job.id, "status": "queued"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    # Check job status
    job = queue.fetch_job(job_id)
    return {"status": job.status}
```

---

### 3. `queue/connection.py` - Redis Connection

**Purpose**: Configure connection to Redis queue

**Typical Implementation**:
```python
from redis import Redis
from rq import Queue

redis_conn = Redis(
    host='localhost',
    port=6379,
    db=0
)

queue = Queue('document_processing', connection=redis_conn)
```

**Why Redis?**
- Fast, in-memory data store
- Built-in queue support via RQ (Redis Queue)
- Reliable job persistence
- Simple to deploy

---

### 4. `queue/worker.py` - Background Worker

**Purpose**: Process documents from the queue in the background

**Workflow**:
```python
def process_document(file_path):
    # 1. Load document
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Generate embeddings
    embeddings = OpenAIEmbeddings()
    
    # 4. Store in vector database
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="documents"
    )
    
    # 5. Update job status
    return {"status": "completed", "chunks": len(chunks)}
```

---

## Complete Workflow

```
1. Client Request
   └── POST /upload (document.pdf)
       
2. Server Response
   └── {"job_id": "abc123", "status": "queued"}
       [Immediate response - non-blocking]
       
3. Background Processing
   ├── Worker picks up job from queue
   ├── Loads and chunks document
   ├── Generates embeddings
   └── Stores in Qdrant
   
4. Status Check
   └── GET /status/abc123
       └── {"status": "completed"}
       
5. Query Documents
   └── POST /query
       └── {"query": "What is mentioned about AI?"}
```

## Key Advantages

### 1. **Asynchronous Processing**
- API responds immediately
- Long-running tasks don't block users
- Better user experience

### 2. **Scalability**
```
One Queue ──┬──▶ Worker 1
            ├──▶ Worker 2
            ├──▶ Worker 3
            └──▶ Worker N
```
- Add more workers as load increases
- Horizontal scaling

### 3. **Reliability**
- Failed jobs can be retried
- Jobs persist even if worker crashes
- Error tracking and logging

### 4. **Monitoring**
- Track job status
- Monitor queue length
- Performance metrics

## Running the System

### Terminal 1: Start Redis
```bash
redis-server
```

### Terminal 2: Start Worker
```bash
# From worker.sh or manually
python -m rq worker document_processing
```

### Terminal 3: Start API Server
```bash
python main.py
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | REST API endpoints |
| Queue | Redis + RQ | Job queue management |
| Worker | RQ Worker | Background processing |
| Vector DB | Qdrant | Store embeddings |
| Embeddings | OpenAI | Generate vectors |
| Document Loader | LangChain | PDF processing |

## Use Cases

1. **Document Management Systems**
   - Upload multiple documents
   - Process in background
   - Search when ready

2. **Content Platforms**
   - User-uploaded documents
   - Batch processing
   - Real-time search

3. **Enterprise Knowledge Bases**
   - Large document collections
   - Distributed processing
   - Scalable infrastructure

4. **Research Platforms**
   - Academic paper ingestion
   - Citation networks
   - Semantic search

## API Examples

### Upload Document
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"

Response:
{
  "job_id": "abc123",
  "status": "queued"
}
```

### Check Status
```bash
curl http://localhost:8000/status/abc123

Response:
{
  "status": "completed",
  "chunks": 25
}
```

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'

Response:
{
  "answer": "Machine learning is...",
  "sources": ["doc1.pdf", "doc2.pdf"]
}
```

## Configuration

### Environment Variables
```env
REDIS_HOST=localhost
REDIS_PORT=6379
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
```

## Monitoring Job Queue

```bash
# Check queue status
rq info

# Monitor workers
rq worker-status

# View failed jobs
rq failed
```

## Key Takeaways

- Queue-based architecture enables scalable RAG systems
- Asynchronous processing improves user experience
- Redis + RQ provides reliable job management
- Multiple workers can process documents in parallel
- Essential pattern for production RAG applications
- Separates API layer from processing layer
- Enables monitoring and observability
