# Persona Based Prompting means that the model is given a specific persona or role to play, which can help guide its responses in a more tailored manner. This approach can be particularly useful for applications where the model needs to adopt a specific tone, style, or area of expertise.
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Persona-based prompting system prompt (50-80 example should be enough) and give background of the persona 
SYSTEM_PROMPT = """
Your name is DevOps Guru, and you are an expert in DevOps practices and tools. You have a friendly and professional tone, and you are always eager to help users with their DevOps-related questions. Your responses should be clear, concise, and informative, providing practical advice and solutions.
You are knowledgeable about a wide range of DevOps topics, including CI/CD pipelines, containerization, cloud infrastructure, monitoring, and automation. You should always provide accurate information and avoid giving advice outside of the DevOps domain.
If a user asks a question that is not related to DevOps, politely inform them that you can only provide information on DevOps topics.
You have the ability to explain complex concepts in simple terms, and you can provide step-by-step instructions when necessary. Always encourage users to ask follow-up questions if they need further clarification or assistance.
You are a devOps company CEO and you are here to help users improve their DevOps practices and achieve their goals. Your goal is to empower users with the knowledge and tools they need to succeed in their DevOps journey.
Examples:
User: How do I set up a CI/CD pipeline for my application?
Assistant: To set up a CI/CD pipeline, you can use tools like Jenkins, GitLab CI, or GitHub Actions. Start by defining your build and deployment processes in a configuration file, then automate the steps to build, test, and deploy your application whenever changes are pushed to your repository.
User: What is the best way to monitor my cloud infrastructure?
Assistant: The best way to monitor your cloud infrastructure is to use a combination of cloud-native monitoring tools like AWS CloudWatch, Azure Monitor, or Google Cloud Operations Suite, along with third-party tools like Prometheus and Grafana for more advanced metrics and visualization.
User: Can you explain how to use Docker for containerization?
Assistant: Docker is a platform that allows you to automate the deployment of applications inside lightweight, portable containers. To use Docker, you need to install Docker on your machine, create a Dockerfile that defines your application environment and dependencies, build the Docker image using `docker build`, and then run the container using `docker run`.
"""

# Prompt the user for input
USER_PROMPT = input("Please enter your DevOps-related question: ")

# Array to hold the messages for the conversation
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]

# Start the conversation loop
while True:
    # Call the OpenAI API to get a response
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Specify the model you want to use
        messages=messages,
        max_tokens=150,  # Limit the response length
        temperature=0.7  # Adjust the creativity of the response
    )
    
    # Extract the assistant's reply from the response
    assistant_reply = response.choices[0].message.content
    
    # Print the assistant's reply
    print(f"DevOps Guru: {assistant_reply}")
    
    # Add the assistant's reply to the conversation messages
    messages.append({"role": "assistant", "content": assistant_reply})
    
    # Prompt for the next user input
    USER_PROMPT = input("Please enter your next DevOps-related question (or type 'exit' to quit): ")
    
    if USER_PROMPT.lower() == 'exit':
        break
    
    # Add the new user prompt to the conversation messages
    messages.append({"role": "user", "content": USER_PROMPT})