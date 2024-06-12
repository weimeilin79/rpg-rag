# Send a prompt to Meta Llama 3 and print the response stream in real-time.

import boto3
import json
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


host = 'x' # NB without HTTPS prefix, without a port - be sure to substitute your region again
region = 'us-east-1' # substitute your region here
service = 'aoss'

index_name = 'hero_index'
session = boto3.Session(region_name = 'us-east-1',
                        aws_access_key_id='x',
                        aws_secret_access_key='x',)


session_creds = session.get_credentials()
auth = AWSV4SignerAuth(session_creds, region, service)

aoss_client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Define the user message to send.
input_query = "Hero Corin's life"


embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
# Generate the embedding for the query
query_embedding = embedding_model.encode(input_query).tolist()

# Define the k-NN search query
knn_query = {
    "size": 5,  # Number of similar documents to retrieve
    "query": {
        "knn": {
            "embedding": {
                "vector": query_embedding,
                "k": 5  # Number of nearest neighbors
            }
        }
    }
}

# Perform the k-NN search
response = aoss_client.search(
    index=index_name,
    body=knn_query
)


# Extract the relevant documents
retrieved_docs = [hit['_source']['text'] for hit in response['hits']['hits']]
retrieved_context = " ".join(retrieved_docs)

# Query text
input_query = "How do you defeat the dragon?"

# Embed the retrieved documents in the prompt for Llama 2
prompt = f"""
    You must provide an answer based on the following context.

    You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone .

    Context: {retrieved_context}

    User: {input_query}
"""

# Format the request payload using the model's native structure.
request = {
    "prompt": prompt
}

# Set the model ID, 
model_id = "meta.llama2-13b-chat-v1"

sessionAnother = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id='x',
                        aws_secret_access_key='x',)

boto3_bedrock = sessionAnother.client(service_name="bedrock-runtime")

# Encode and send the request.
response = boto3_bedrock.invoke_model(
    modelId=model_id,
    body=json.dumps(request),
    contentType='application/json'
)

# Read the response
response_body = response['body'].read().decode('utf-8')
print(response_body)