# Send a prompt to Meta Llama 3 and print the response stream in real-time.

import boto3
import json

# Create a Bedrock Runtime client in the AWS Region of your choice.
session = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id='',
                        aws_secret_access_key='',)
client = session.client(service_name="bedrock-runtime")

# Set the model ID, e.g., Llama 3 Chat.
model_id = "meta.llama2-13b-chat-v1"

# Define the user message to send.
input_query = "How are you?"

# Embed the message in Llama 3's prompt format.
prompt = f"""You must provide an answer."
                
                "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone ."

    user: {input_query}
    """

# Format the request payload using the model's native structure.
request = {
    "prompt": prompt,
    # Optional inference parameters:
    "max_gen_len": 512,
    "temperature": 0.5,
    "top_p": 0.9,
}

# Encode and send the request.
response_stream = client.invoke_model_with_response_stream(
    body=json.dumps(request),
    modelId=model_id,
)

# Extract and print the response text in real-time.
for event in response_stream["body"]:
    chunk = json.loads(event["chunk"]["bytes"])
    if "generation" in chunk:
        print(chunk["generation"], end="")

