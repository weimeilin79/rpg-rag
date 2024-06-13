## Create the First Lambda Function 

The Python app is a Lambda function that integrates with Redpanda Serverless. It is responsible for processing messages received from the "npc2-request" topic and generating responses that are published to the "npc-response" topic.

The app starts by importing the necessary libraries, including boto3 for AWS service interactions and KafkaProducer for Kafka messaging. It retrieves the required secrets from AWS Secrets Manager and sets up the Kafka producer.

To deploy the Lambda function, a zip deployment package is created. The required dependencies are listed in the `requirements.txt` file, and a virtual environment is set up to install these dependencies. The installed libraries are then packaged into a zip file along with the `lambda_function.py` file.

The zip file is uploaded to the Lambda function through the AWS Management Console. The function's configuration is updated to include necessary environment variables and permissions. The timeout is set to 30 seconds to ensure the function has enough time to process messages. Test events can be created to verify the function's behavior.

The Lambda function is triggered by messages from the Kafka topic. It receives the event payload, which contains the message from the "npc2-request" topic. 


### Add Topics in Redpanda Serverless Platform  
-  Open the Redpanda Serverless platform in your web browser.
- Navigate to the "Topics" section.
- Click on the "Create Topic" button.
- Enter "npc2-request" as the topic name and click "Create".
- Repeat steps 4 and 5 to create another topic named "npc-response".
- Verify that both topics have been successfully created.

![Redpanda Serverless Topics](images/rp-npc2-topics.png)

Now you have added the necessary topics to Redpanda Serverless for your Lambda functions to communicate with.


### Create the Lambda Function
 -  Sign in to the AWS Management Console:
 -  Select Services and then choose Lambda under the "Compute" category.

### Create a New Lambda Function:
- Click the Create function button.
- Select: Author from scratch.
- Function name: askSorcerer
- Runtime: Choose Python 3.12
- Architecture : arm64
- Click Create function to create the function.
![Create lambda](images/askSorcerer-create.png)

### Add the Python Code:

- In your workspace, create a new directory `sorcerer` as the working directory for this section
```
cd ~
mkdir sorcerer
cd sorcerer
```

- In the workshop space, create a `lambda_function.py` file:
```
import boto3
import json
import base64 
from kafka import KafkaProducer

# Secret Manager setup
secret_name = "workshop/redpanda/npc"
region_name = "us-east-1"
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
session = boto3.Session(region_name='us-east-1')
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Set the model ID, e.g., Llama 3 Chat.
model_id = "meta.llama2-13b-chat-v1"


def prepare_prompt(input_query):
    # Embed the message in Llama 3's prompt format.
    prompt = f"""You must provide an answer in under 5 sentences."
                "context":  "You are a sorcerer who lives in the fantasy world, specialized in light magic, but you are familiar with other elements, you have been asked a question. You must provide an answer.
                Your have a hot-cold personality type, normally being sharp but at some prompt suddenly becoming lovestruck. You are in your 20s, and female."
    user: {input_query}
    """

    # Format the request payload using the model's native structure.
    request = {
        "prompt": prompt
    }

    return json.dumps(request)


def lambda_handler(event, context):
    print(f'event message: {event}')
    for topic_partition, records in event['records'].items():
        for record in records:
            question = base64.b64decode(record['value'])  # Adjust based on actual message format
            print(f"Received message: {prepare_prompt(question)}")

            # Encode and send the request.
            response_stream = boto3_bedrock.invoke_model_with_response_stream(
                body=prepare_prompt(question),
                modelId=model_id,
            )
            response_text = ""
            for event in response_stream["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "generation" in chunk:
                    response_text += chunk["generation"]
            message_data = {
                "who": "npc2",
                "msg": response_text
            }
            producer.send('rpg-response', message_data)
            producer.flush()
```
The function retrieves configuration data from AWS Secrets Manager, sets up a Kafka producer to connect to Redpanda with secure credentials, and configures a Bedrock client for model interactions. 

When receiving event, it decodes and formats them into prompts for the Bedrock model, processes the model's response, and sends the combined response back to a Kafka topic. The function ensures secure and efficient message processing, leveraging AWS infrastructure and machine learning capabilities.


### Creating a zip deployment package with dependencies
- Create a requirements.txt file with the following content and upload it using the Lambda function's code editor:
```
boto3==1.34.125
botocore==1.34.125
jmespath==1.0.1
kafka-python-ng==2.2.2
python-dateutil==2.9.0.post0
s3transfer==0.10.1
six==1.16.0
urllib3==2.2.1
```

- Create and activate a virtual environment in your project directory
```
python3 -m venv env
source env/bin/activate
source ./env/bin/activate
```

- Install the required libraries with pip. 
```
pip install -r requirements.txt 
```

The folder in which pip installs the libraries may be named site-packages or dist-packages. This folder may be located in either the lib/python3.x or lib64/python3.x directory

- Deactivate the virtual environment
```
deactivate
```

- Navigate into the directory containing the dependencies you installed with pip and create a .zip file in your project directory with the installed dependencies at the root. 

```
cd env/lib/python3.12/site-packages
zip -r ../../../../askSorcerer.zip . -x "*__pycache__*" 
cd ../../../../
zip askSorcerer.zip lambda_function.py
```

Note: 

### Upload the Zip File to Lambda Function:
- Open the AWS Management Console and navigate to the Lambda service.
- Select the Lambda function you want to upload the zip file to.
- In the function's configuration, go to the "Code" tab.
- Scroll down to the "Function code" section and click on the "Upload" button.
- Choose the lambda_libs.zip file from your local machine and click on the "Open" button.
- Wait for the upload to complete, and then click on the "Save" button to apply the changes.

###  Update lambda configuration Permissions:

- In the function's configuration, click on the "Configuration" tab.
- Scroll down to the "Permissions" section, under Execution role section find the Role name, click on the `askSourcerer-role-xxxxxx` to configure the permission.
![Lambda Role in Config](images/askSorcerer-lambda-role.png)

- Add the necessary following policies
  - **SecretsManagerReadWrite** - allows read/write access to AWS Secrets Manager.
  - **AmazonS3ReadOnlyAccess** - if your Lambda needs to read from S3.
  - **AmazonEC2ContainerRegistryReadOnly** - for pulling Docker images from ECR .
- Click on the "Save" button to apply the changes. 

![Lambda role permission](images/askSorcerer-permission.png)

- Set the timeout for your Lambda function to 30 seconds, still in the "Configuration" tab.
- Scroll down to the "General configuration" section.
- In the "Timeout" field, enter "30" (without quotes) to set the timeout to 30 seconds.
- Click on the "Save" button to apply the changes.
![Lambda timeout](images/askSorcerer-timeout.png)
  
This will ensure that your Lambda function has a maximum execution time of 30 seconds before it times out and update the permissions for your Lambda function to include the required access to AWS services and resources.

### Test the Lambda Function
To test the Lambda function with a test event, 

- In the function's configuration, go to the "Test" tab.
- Enter a name for the test event (e.g., "MockEvent").
- In the event body, provide the test event JSON payload 

```
{
  "eventSource": "SelfManagedKafka",
  "bootstrapServers": "redpanda.example.com:9092",
  "records": {
    "npc2-request-0": [
      {
        "topic": "npc2-request",
        "partition": 0,
        "offset": 0,
        "timestamp": 1718237343835,
        "timestampType": "CREATE_TIME",
        "key": "",
        "value": "SG93J3MgeW91ciBkYXk/",
        "headers": []
      }
    ]
  }
}
```
- Click on the "Save" button to save the test event, and click "Test" to execute the Lambda function with the test event
![Lambda test](images/askSorcerer-test.png)

### Configure the Trigger for the Lambda Function
To configure the trigger for the Lambda function and connect to the topic in Redpanda Serverless using Kafka endpoint, follow these steps:

1. Open the AWS Management Console and navigate to the Lambda service.
2. Select the Lambda function you want to configure the trigger for (e.g., askSorcerer).
3. In the function's configuration, go to the "Triggers" tab.
4. Click on the "Add trigger" button.
5. For the trigger configuration, choose "Kafka".
6. Enter the required details:
    - **Bootstrap Server**: Provide the Kafka endpoint of your Redpanda Serverless cluster.
    - **Kafka topic**: Specify the name of the topic you want the Lambda function to subscribe to `npc2-request`.
    - **Batch size**: Set the batch size to 1 to retrieve one record at a time.
    - **Starting position**: Choose where to start reading messages, LATEST to start from the latest message.
    - **Authentication**: Select `SASL_SCRAM_256_AUTH` as the authentication mechanism.
    - **Secrets Manager key**: Enter the key **workshop/redpanda/lambda** for the Secrets Manager secret.

7. Click on the "Add" button to attach the trigger to your Lambda function.
![Lambda trigger](images/askSorcerer-trigger.png)

This configuration will enable your Lambda function to receive messages from the specified Kafka topic in Redpanda Serverless, with a batch size of 1 record at a time, using SASL/SCRAM authentication and retrieving messages starting from the specified position.

### Test the result
Use the Redpanda Serverless console to post a text message in the "npc2-request" topic. Enter the value "how's your day" as the message content.

![Redpanda question](images/rp-test-question.png)
![Redpanda question create](images/rp-test-value.png)

After the Lambda function is triggered, check the "npc-response" topic to see the result.
![Redpanda response](images/rp-topic-response.png)


## Create the Second Lambda Function using Docker


### Add Topics in Redpanda Serverless Platform  
-  Open the Redpanda Serverless platform in your web browser.
- Navigate to the "Topics" section.
- Click on the "Create Topic" button.
- Enter "npc2-request" as the topic name and click "Create".
- Repeat steps 4 and 5 to create another topic named "npc-response".
- Verify that both topics have been successfully created.


### Building Langchain App

In your workspace, create a new directory hero as the working directory for this section. This directory will be used for building an AI inference app using LangChain for you Hero NPC.
  
```
cd ~
mkdir hero
cd hero
```

- Create a file named `lambda_function.py`:

```
import json
import base64 
import boto3
from kafka import KafkaProducer
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain_core.prompts import PromptTemplate

# Secret Manager setup
secret_name = "workshop/redpanda/npc"
region_name = "us-east-1"
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
session = boto3.Session(region_name='us-east-1')
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-1')

def prepare_prompt():
    prompt_template = """You must provide an answer in under 5 sentences."
                    "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone ."
        user: {input_query}
        """

    PROMPT = PromptTemplate(input_variables=["input_query"], template=prompt_template)
    return PROMPT

def lambda_handler(event, context):
    for topic_partition, records in event['records'].items():
        for record in records:
            question = base64.b64decode(record['value'])  
            print(f"Received message: {question}")
            response_msg = query_data(prepare_prompt(),question)
            print(f'Response message: {response_msg}')
            # Send response back via Kafka
            message_data = {
                "who": "npc1",
                "msg": response_msg
            }
            producer.send('rpg-response', message_data)
            producer.flush()


def query_data(prompt, query):
    chain = prompt | llm
    response_msg = chain.invoke({"input_query": query})
    return response_msg
```

### Package LangChain Application in container

Package the LangChain application in a Docker container to ensure consistent and reliable deployment across different environments. Here it will be used to deploy in Lambda

- Create a file name `Dockerfile` 
  
```
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
# COPY requirements.txt ${LAMBDA_TASK_ROOT}

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

### Build and Push the Docker Image to Amazon ECR

- Build the Docker Image:
Open a terminal and navigate to the directory containing your Dockerfile.
Build the Docker image:

```
docker build -t askhero .
```

Tag the Docker Image:
```
docker tag askhero <your-ecr-repository-uri>
```

- Push the Docker Image to ECR:
  
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-ecr-repository-uri>
```

- By running this command, the Docker image built in the previous steps will be pushed to the specified ECR repository, making it available for deployment and use in other services or environments.

```
docker push <your-ecr-repository-uri>
```

### Create the Lambda Function from the Docker Image

- Navigate to Lambda
- Click the Create function button.
- Select Container image.
- Function name: `askhero`
- Container image URI: Enter the URI of your Docker image in ECR.

![Create lambda](images/askHero-create.png)

Click Create function to create the function.
###  Update lambda configuration Permissions:

- In the function's configuration, click on the "Configuration" tab.
- Scroll down to the "Permissions" section, under Execution role section find the Role name, click on the `askHero-role-xxxxxx` to configure the permission.
![Lambda Role in Config](images/askHero-lambda-role.png)

- Add the necessary following policies
  - **SecretsManagerReadWrite** - allows read/write access to AWS Secrets Manager.
  - **AmazonBedrockFullAccess** - allow access to Bedrock models.
- Click on the "Save" button to apply the changes. 

![Lambda role permission](images/askHero-permission.png)

- Set the timeout for your Lambda function to 30 seconds, still in the "Configuration" tab.
- Scroll down to the "General configuration" section.
- In the "Timeout" field, enter "30" (without quotes) to set the timeout to 30 seconds.
- Click on the "Save" button to apply the changes.
![Lambda timeout](images/askHero-timeout.png)
  
This will ensure that your Lambda function has a maximum execution time of 30 seconds before it times out and update the permissions for your Lambda function to include the required access to AWS services and resources.

### Test the Lambda Function
To test the Lambda function with a test event, 

- In the function's configuration, go to the "Test" tab.
- Enter a name for the test event (e.g., "MockEvent").
- In the event body, provide the test event JSON payload 

```
{
  "eventSource": "SelfManagedKafka",
  "bootstrapServers": "redpanda.example.com:9092",
  "records": {
    "npc2-request-0": [
      {
        "topic": "npc1-request",
        "partition": 0,
        "offset": 0,
        "timestamp": 1718237343835,
        "timestampType": "CREATE_TIME",
        "key": "",
        "value": "SG93J3MgeW91ciBkYXk/",
        "headers": []
      }
    ]
  }
}
```
- Click on the "Save" button to save the test event, and click "Test" to execute the Lambda function with the test event
![Lambda test](images/askSorcerer-test.png)

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