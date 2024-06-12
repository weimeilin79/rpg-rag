## Create the First Lambda Function using the AWS Lambda UI

### Create the Lambda Function
 -  Sign in to the AWS Management Console:
 -  Select Services and then choose Lambda under the "Compute" category.

### Create a New Lambda Function:
- Click the Create function button.
- Select Author from scratch.
- Function name: askSorcerer
- Runtime: Choose Python 3.12
- Click Create function to create the function.

### Add the Python Code:

- In the Lambda function editor, replace the default code with the provided lambda_function.py code:
```
import boto3
import json
from kafka import KafkaProducer

# Secret Manager setup
secret_name = "demo/redpanda/rpg"
region_name = "us-east-2"
sessionSM = boto3.session.Session()
client = sessionSM.client(service_name='secretsmanager', region_name=region_name)
get_secret_value_response = client.get_secret_value(SecretId=secret_name)
secret = get_secret_value_response['SecretString']
secret_data = json.loads(secret)
bedrock_key = secret_data['BEDROCK_KEY']
bedrock_secret = secret_data['BEDROCK_SECRET']
broker = secret_data['REDPANDA_SERVER']
rp_user = secret_data['REDPANDA_USER']
rp_pwd = secret_data['REDPANDA_PWD']

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers=[broker],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=rp_user,
    sasl_plain_password=rp_pwd,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializer to convert to JSON
)

# LangChain setup
session = boto3.Session(region_name='us-east-1', aws_access_key_id=bedrock_key, aws_secret_access_key=bedrock_secret)
boto3_bedrock = session.client(service_name="bedrock-runtime")

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
    "prompt": prompt
}

# Encode and send the request.
response_stream = boto3_bedrock.invoke_model_with_response_stream(
    body=json.dumps(request),
    modelId=model_id,
)

def lambda_handler(event, context):
    print(f'event message: {event}')
    for record in event['Records']:
        question = record['value']  # Adjust based on actual message format
        print(f"Received message: {question}")
        for event in response_stream["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "generation" in chunk:
                message_data = {
                    "who": "npc1",
                    "msg": chunk["generation"]
                }
                producer.send('rpg-response', message_data)
        producer.flush()
        producer.close()
```
### Add Requirements:
- Create a requirements.txt file with the following content and upload it using the Lambda function's code editor:
```
boto3
kafka-python-ng
```

### Configure the Lambda Function
- Click on the Configuration tab.
- Choose Environment variables from the left-hand menu.
- Click Edit and add the following environment variables if necessary:

### Set Up Permissions:

Ensure the Lambda function has the necessary IAM role with permissions to access Setting Up Permissions for Lambda Functions

- In the AWS Management Console, select Services and then choose IAM under the "Security, Identity, & Compliance" category.

- In the IAM dashboard, click on Roles in the left-hand navigation pane.
Click the Create role button at the top of the page.
Select the Lambda Service:

- Under Select type of trusted entity, choose AWS service.
- In the Use case section, select Lambda.
- Click the Next: Permissions button.
Attach Policies:

In the Attach permissions policies section, search for and select the following policies:
- **AWSLambdaBasicExecutionRole** - provides basic logging permissions to CloudWatch.
- **SecretsManagerReadWrite** - allows read/write access to AWS Secrets Manager.
- **AmazonS3ReadOnlyAccess** - if your Lambda needs to read from S3.
- **AmazonEC2ContainerRegistryReadOnly** - for pulling Docker images from ECR .

## Create the Second Lambda Function using Docker
Create Docker Image for Lambda
```
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install langchain_community
RUN pip install langchain
RUN pip install langchain_aws
RUN pip install boto3
RUN pip install botocore
RUN pip install kafka-python-ng

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["lambda_function.lambda_handler"]

```

Create lambda_function.py:

```
import json
import os
import boto3
from kafka import KafkaProducer
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain_core.prompts import PromptTemplate

# Secret Manager setup
secret_name = "demo/redpanda/rpg"
region_name = "us-east-2"
sessionSM = boto3.session.Session()
client = sessionSM.client(service_name='secretsmanager', region_name=region_name)
get_secret_value_response = client.get_secret_value(SecretId=secret_name)
secret = get_secret_value_response['SecretString']
secret_data = json.loads(secret)
bedrock_key = secret_data['BEDROCK_KEY']
bedrock_secret = secret_data['BEDROCK_SECRET']
broker = secret_data['REDPANDA_SERVER']
rp_user = secret_data['REDPANDA_USER']
rp_pwd = secret_data['REDPANDA_PWD']

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers=[broker],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username=rp_user,
    sasl_plain_password=rp_pwd,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializer to convert to JSON
)

# LangChain setup
session = boto3.Session(region_name='us-east-1', aws_access_key_id=bedrock_key, aws_secret_access_key=bedrock_secret)
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-1')

prompt_template = """You must provide an answer."
                "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone ."
    user: {input_query}
    """

PROMPT = PromptTemplate(input_variables=["input_query"], template=prompt_template)
chain = PROMPT | llm

def lambda_handler(event, context):
    print(f'event message: {event}')
    for record in event['Records']:
        question = record['value']  # Adjust based on actual message format
        print(f"Received message: {question}")
        response_msg = query_data(question)
        print(f'Response message: {response_msg}')
        # Send response back via Kafka
        message_data = {
            "who": "npc1",
            "msg": response_msg
        }
        producer.send('rpg-response', message_data)
        producer.flush()
        producer.close()

def query_data(query):
    response_msg = chain.invoke({"input_query": query})
    return response_msg
```

### Build and Push the Docker Image to Amazon ECR

- Build the Docker Image:
Open a terminal and navigate to the directory containing your Dockerfile.
Build the Docker image:
```
docker build -t <your-image-name> .
```

Tag the Docker Image:
```
docker tag <your-image-name> <your-ecr-repository-uri>
```

- Push the Docker Image to ECR:
```
# Authenticate Docker to your Amazon ECR registry
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-ecr-repository-uri>
```

```
docker push <your-ecr-repository-uri>
```

###  Create the Lambda Function from the Docker Image
- Navigate to Lambda
- Click the Create function button.
- Select Container image.
- Function name: Enter a name for your Lambda function (e.g., LangChainFunction).
- Container image URI: Enter the URI of your Docker image in ECR.
- Configure Function Settings:

Click Create function to create the function.
##  Add Redpanda as a Trigger to Lambda Functions
- In the Lambda dashboard, click on Functions in the left-hand navigation pane.
- Select the Lambda function you created (e.g., 
  - askSFunction
  - LangChainFunction

### Add a Trigger
- In the Configuration tab, choose Triggers from the left-hand menu.
- Click the Add trigger button.

### Deploy the pipeline
- For Trigger configuration, choose Kafka.
- Enter the required details:
- Boostrap Server: Provide the ARN of your Kafka cluster.
- Kafka topic: Specify the topic your Lambda function should subscribe to.
- Batch size: Set the number of records to retrieve in each batch.
- Starting position: Choose where to start reading messages (e.g., TRIM_HORIZON to start from the beginning or LATEST to start from the latest message).
- Add Security Manager
- Click Add to attach the trigger to your Lambda function.