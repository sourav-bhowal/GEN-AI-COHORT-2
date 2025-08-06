# flake8: noqa
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
# similar to 'zod' but more commonly used in Python projects
from pydantic import BaseModel
from typing import Literal

# This code is part of a language graph that processes user queries
# and routes them to appropriate chat bots based on whether they are coding-related or not.
#  Its a multi model chat bot system that uses OpenAI's API to classify and respond to queries.

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI()

# Define the response model for classification messages
class ClassifyMesaageResponse(BaseModel):
    """
    Represents the response structure for the classification of queries.
    This is a Pydantic model to ensure structured output.
    """
    is_coding_question: bool  # Indicates if the query is related to coding

# Define the response model for code accuracy validation
class CodeAccuracyResponse(BaseModel):
    """
    Represents the response structure for code accuracy validation.
    This is a Pydantic model to ensure structured output.
    """
    accuracy: float  # The accuracy of the code response, as a percentage


# Create State class to define the structure of the state
class State(TypedDict):
    """
    Represents the state of the graph.
    This is a placeholder for the actual state structure.
    """
    user_query: str  # The input query for the chat bot
    llm_code: str | None  # The response from the language model, initially None
    accuracy: float | None  # The accuracy of the response, initially None
    is_coding_question: bool | None  # Whether the query is coding-related, initially None
    retry_count: int | None  # Count of retries, initially None


def classify_query(state: State) -> State:
    """
    Classifies the user's query to determine if it is coding-related.
    This function updates the state with the classification result.
    """
    print("Classifying query...")
    # Get the user query from the state
    query = state['user_query']

    SYSTEM_MESSAGE = """
    You are a classifier that determines if a user's query is related to coding.
    Classify the query as 'coding' or 'non-coding'.
    Return the response in specificed JSON boolean format only.
    """
    # Structed Outputs / Responses
    # This will help in structuring the response

    # Call the OpenAI API to classify the query
    llm_res = openai_client.beta.chat.completions.parse(
        model="gpt-4.1-nano",  # Use a suitable model for classification
        response_format=ClassifyMesaageResponse,    # Define the expected response structure 
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query}
        ],
    )

    # Extract the classification result from the OpenAI API result
    # This assumes the response is structured as per ClassifyMesaageResponse
    is_coding_question = llm_res.choices[0].message.parsed.is_coding_question
    
    # Update the state with the classification result
    state['is_coding_question'] = is_coding_question
    
    # Return the updated state
    return state


def route_query(state: State) -> Literal["general_chat_bot", "coding_chat_bot"]:
    """
    Routes the query based on whether it is coding-related or not.
    Returns the name of the next node to process the query.
    """
    print("Routing query...")
    is_coding_question = state['is_coding_question']
    
    # Determine the next node based on the classification result
    if is_coding_question:
        return "coding_chat_bot"
    else:
        return "general_chat_bot"


def general_chat_bot(state: State) -> State:
    """
    A general chat bot function that simulates a response based on the input state.
    It updates the state with a response to the query.
    """
    print("Processing general chat bot...")
    # Get the query from the state
    query = state['user_query']

    # Call the OpenAI API to process the query
    llm_res = openai_client.chat.completions.create(
        model="gpt-4.1-mini", # Use a suitable model for general chat
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        max_tokens=1000,  # Limit the response length
        temperature=0.5  # Control the randomness of the response
    )

    # Extract the response from the OpenAI API result
    result = llm_res.choices[0].message.content

    # Update the state with the response
    state['llm_code'] = result

    # Return the updated state
    return state


def coding_chat_bot(state: State) -> State:
    """
    A coding-specific chat bot function that simulates a response based on the input state.
    It updates the state with a response to the coding-related query.
    """
    print("Processing coding chat bot...")
    # Get the query from the state
    query = state['user_query']
    
    # Define a system message for the coding chat bot
    SYSTEM_MESSAGE = """
    You are a coding assistant that helps users with programming-related queries.
    Provide detailed explanations and code snippets when necessary.
    Ensure your responses are clear and concise.
    """

    # Call the OpenAI API to process the query
    llm_res = openai_client.chat.completions.create(
        model="gpt-4.1", # Use a suitable model for coding-related queries
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query}
        ],
        max_tokens=1000,  # Limit the response length
        temperature=0.5  # Control the randomness of the response
    )

    # Extract the response from the OpenAI API result
    result = llm_res.choices[0].message.content

    # Update the state with the response
    state['llm_code'] = result

    # Return the updated state
    return state


def coding_validate_chat_bot(state: State) -> State:
    """
    A coding validation chat bot function that checks the correctness of code-related queries.
    It updates the state with the accuracy of the code response.
    """
    print("Validating coding response...")
    # Get the query from the state
    query = state['user_query']
    llm_code = state['llm_code']
    
    # Define a system message for the coding validation chat bot
    SYSTEM_MESSAGE = f"""
    You are a coding validation assistant that checks the correctness of code-related queries.
    Provide feedback on the code, suggest improvements, and ensure best practices are followed.
    Return the percentage accuracy of the code response.
    User query: {query}
    Code to validate: {llm_code}
    """

    # Call the OpenAI API to process the query
    llm_res = openai_client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=CodeAccuracyResponse,  # Define the expected response structure for code validation
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query}
        ],
    )

    # Extract the response from the OpenAI API result
    result = llm_res.choices[0].message.parsed.accuracy

    # Update the state with the response
    state['accuracy'] = result

    # Return the updated state
    return state

# If coding accuracy less than 80% then route to coding chat bot
def coding_accuracy_check(state: State) -> Literal[END, "increment_retry_count"]:
    """
    Checks the accuracy of the coding response.
    Routes based on accuracy and retry count without modifying state.
    """
    print(f"Checking coding accuracy... Accuracy: {state['accuracy']}, Retry count: {state['retry_count']}")
    accuracy = state['accuracy']
    retry_count = state['retry_count']
    
    # Check both accuracy AND retry count
    if accuracy < 95 and retry_count < 3:
        print(f"Accuracy too low ({accuracy}%), routing to increment retry count...")
        return "increment_retry_count"
    else:
        if retry_count >= 3:
            print(f"Maximum retry limit reached ({retry_count}). Ending with current response.")
        else:
            print(f"Accuracy acceptable ({accuracy}%). Ending.")
        return END
    
# Conditional nodes can't modify state, they can only route based on conditions

def increment_retry_count(state: State) -> State:
    """
    Increments the retry count and returns updated state.
    This is a regular node that can modify state.
    """
    print("Incrementing retry count...")
    state['retry_count'] += 1
    print(f"Retry count incremented to: {state['retry_count']}")
    return state

# Create a state graph builder by passing the State class
# This will help in constructing the graph with nodes and edges
graph_builder = StateGraph(State)

# Add a node for classifying the query
graph_builder.add_node("classify_query", classify_query)
# Add a node for routing the query
graph_builder.add_node("route_query", route_query)
# Add a node for the general chat bot
graph_builder.add_node("general_chat_bot", general_chat_bot)
# Add a node for the coding chat bot
graph_builder.add_node("coding_chat_bot", coding_chat_bot)
# Add a node for the coding validation chat bot
graph_builder.add_node("coding_validate_chat_bot", coding_validate_chat_bot)
# Add a node for checking coding accuracy
graph_builder.add_node("coding_accuracy_check", coding_accuracy_check)
# Add a node for incrementing the retry count
graph_builder.add_node("increment_retry_count", increment_retry_count)



# Define the edges between the nodes
# Add an edge from the start to the classification node
graph_builder.add_edge(START, "classify_query")
# Add a conditional edge based on the classification result to route the query
graph_builder.add_conditional_edges("classify_query", route_query)
# Edge for general chat bot
graph_builder.add_edge("general_chat_bot", END)
# Edge for routing the query to the appropriate chat bot
graph_builder.add_edge("coding_chat_bot", "coding_validate_chat_bot")
# Edge for coding validation chat bot
graph_builder.add_conditional_edges("coding_validate_chat_bot", coding_accuracy_check)
# Edge to check retry count
graph_builder.add_edge("increment_retry_count", "coding_chat_bot")


# Compile the graph to finalize its structure
graph = graph_builder.compile()

def main():
    """
    Main function to run the state graph.
    This function initializes the state and runs the graph.
    """

    user_query = input("Enter your query: ")
    
    # Initialize the state with a user query
    initial_state: State = {
        "user_query": user_query, # The input query for the chat bot
        "llm_code": None,  # Initially, there is no code response
        "accuracy": None,  # Initially, there is no accuracy
        "is_coding_question": None,  # Initially, the classification is unknown
        "retry_count": 0  # Initialize retry count to 0
    }

    # Invoke the graph with the initial state (direct output)
    # res = graph.invoke(initial_state)
    
    # Print the final state
    # print("Final State:", res)
    
    # We can also stream the graph (streaming output)
    for event in graph.stream(initial_state, stream_mode="messages"):
        print("Event", event)


main()