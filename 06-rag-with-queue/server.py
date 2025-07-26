# flake8: noqa
from fastapi import FastAPI, Path, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG with Queue server!"}


# Async endpoint for chat functionality using Queue
@app.post("/chat")
def chat(
    query: str = Query(..., description="The user's chat query"),
):
    """
    Endpoint to handle chat queries.
    This endpoint accepts a query string and enqueues it for processing.
    """
    # Enqueue the query for processing (asynchronously) it takes 2 parameters (query and process_query function)
    job = queue.enqueue(process_query, query)

    # Return a response indicating the query has been received
    return {"message": "Your query has been received and is being processed.", "job_id": job.id}


# Endpoint to retrieve the result of a processed query
@app.get("/result/{job_id}")
def get_result(job_id: str = Path(..., description="The ID of the job to retrieve the result for")):
    """
    Endpoint to retrieve the result of a processed query.
    This endpoint checks the status of the job and returns the result if available.
    """
    job = queue.fetch_job(job_id)
    
    if job is None:
        return {"error": "Job not found."}
    
    if job.is_finished:
        return {"job_id": job.id, "result": job.result}
    
    return {"job_id": job.id, "status": "Processing, please check back later."}
    