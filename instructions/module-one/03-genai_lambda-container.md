## Create the Second Lambda Function using Docker

AWS Lambda allows you to run code without provisioning or managing servers, and it supports different methods for deploying your functions. One powerful and flexible approach is to use container images for deploying Lambda functions. Containers enable you to package and deploy your application with all its dependencies, providing consistency across development, testing, and production environments.

Why Use Containers for Lambda Functions?

- Custom Runtime and Dependencies: Containers allow you to include custom runtimes, binaries, and other dependencies that might not be supported natively by Lambda’s built-in runtimes.
- Consistency: By packaging your code and dependencies together in a container, you ensure that your Lambda function runs consistently in any environment, reducing the "works on my machine" problem.
- Portability: Containers make it easier to port applications across different environments and cloud providers, providing greater flexibility in deployment.
- Complex Dependencies: When your application has complex dependencies or requires a specific environment setup, containers provide a straightforward way to package everything together.
- Increased Deployment Size: Lambda traditionally has a deployment package size limit of 50 MB (zipped) and 250 MB (unzipped). Using containers increases this limit to up to 10 GB, making it easier to include large dependencies and binaries.


### Add Topics in Redpanda Serverless Platform  
-  Open the Redpanda Serverless platform in your web browser.
- Navigate to the "Topics" section.
- Click on the "Create Topic" button.
- Enter `npc1-request` as the topic name and click "Create".
- Verify that thw topics have been successfully created.

### Setup a Container Registry
A container registry is a centralized repository that stores, manages, and distributes container images. It enables developers to push, pull, and organize container images, facilitating seamless deployment and version control across different environments. By using a container registry, teams can ensure consistency, security, and scalability in their containerized application deployments.

Amazon Elastic Container Registry (ECR) that integrates seamlessly with other AWS services, including Amazon ECS, EKS, and AWS Lambda, providing image management in AWS ecosystem.

- In the AWS Management Console, select Services.
- Under the "Containers" category, choose Elastic Container Registry.
- In the Amazon ECR dashboard, click on Repositories in the left-hand navigation pane.
- Click the Create repository button at the top of the page.

### Configure the Repository

**Repository name**: `redpanda-workshop`.
**Visibility settings**:  `Private`, The repository is only accessible to your AWS account.

![ACR config](../images/acr_create.png)

- Review your settings and click the Create repository button.
- Copy the URI and have it handy

![ACR config](../images/acr-uri.png)


### Building Langchain for Serverless

LangChain is a powerful framework designed to facilitate the development of applications powered by large language models (LLMs). It provides a structured and modular approach to integrating LLMs into various applications, enabling seamless interaction with natural language processing capabilities.By abstracting the complexities of model integration, LangChain accelerates development and enhances the functionality of applications leveraging advanced language models.

We are using 3 major libraries in this implementation

- **langchain_core** is the foundational library of the LangChain framework, offering core functionalities and tools necessary for building applications powered by large language models. It includes essential components such as prompt templates, model pipelines, and utility functions that streamline the development process. langchain_core provides a structured and modular approach to integrating language models into applications, enabling developers to create sophisticated and efficient AI-driven systems with ease. This library serves as the backbone of the LangChain ecosystem, supporting various extensions and integrations.

- **langchain_community** is a library within the LangChain framework that serves as a hub for community-contributed integrations and extensions. It allows developers to leverage and share various plugins, models, and connectors developed by the community, facilitating collaboration and innovation. This library helps expand the capabilities of LangChain by incorporating a wide range of tools and resources contributed by other developers, making it easier to integrate and utilize different language models and APIs in your applications.

- **langchain_aws** is a specialized library in the LangChain ecosystem that provides integration with AWS services. This library simplifies the process of connecting LangChain applications with AWS resources such as Amazon Bedrock, AWS Lambda, and other AI and machine learning services offered by AWS. 

Now, let's get started. 

- In your workspace, create a new directory hero as the working directory for this section. This directory will be used for building an AI inference app using LangChain for you Hero NPC.
  
```
cd ~
mkdir environment/hero
cd environment/hero
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
    prompt_template = """
        Context: You are a hero who lives in a fantasy world. You have just defeated a monster and are in high spirits. 
        Instruction: Please answer the following question in less than 5 sentences and in an upbeat tone. Don't provide a note in the answer.
        
        Question: {input_query}
    """


    PROMPT = PromptTemplate(input_variables=["input_query"], template=prompt_template)
    return PROMPT

def lambda_handler(event, context):
    for topic_partition, records in event['records'].items():
        for record in records:
            question = base64.b64decode(record['value'])  
            print(f"Received message: {question}")
            response_msg = query_data(prepare_prompt(),question)
            
            # Convert response_msg to string and print ASCII values for debugging
            response_msg = str(response_msg)
            print(f"Raw response message: {response_msg}")
            print(f"ASCII values: {[ord(c) for c in response_msg[:20]]}")

            # Manually remove "Answer:" including any potential leading/trailing whitespace
            prefix = "Answer:"
            stripped_response = response_msg.strip()
            if stripped_response.startswith(prefix):
                response_msg = stripped_response[len(prefix):].strip()
            
            print(f'Response message after stripping: {response_msg}')



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

The function retrieves necessary credentials from AWS Secrets Manager to securely connect to a Redpanda Serverless Kafka instance using the KafkaProducer. And sets up an AI language model (Llama 2) via LangChain via AWS Bedrock, which processes input queries and generates responses. 

When triggered by incoming Kafka messages from the "npc1-request" topic, the function decodes the message, formats it into a prompt for the AI model, invokes the model to generate a response, and sends the response back to the "rpg-response" Kafka topic. 


### Package LangChain Application in container

Package the LangChain application in a Docker container to ensure consistent and reliable deployment across different environments. Here it will be used to deploy in Lambda.

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

- By running this command, the Docker image built in the previous steps will be pushed to the your ECR repository, making it available for deployment and use in AWS Lambda service.

```
docker push <your-ecr-repository-uri>
```

### Create the Lambda Function from the Docker Image

- Navigate to Lambda
- Click the Create function button.
- Select Container image.
- Function name: `askhero`

![Create lambda](../images/askHero-create.png)

- Container image URI: Enter the URI of your Docker image in ECR.

![Select image](../images/askHero-container-select.png)

Click Create function to create the function.


###  Update lambda configuration Permissions:

- In the function's configuration, click on the "Configuration" tab.
- Scroll down to the "Permissions" section, under Execution role section find the Role name, click on the `askHero-role-xxxxxx` to configure the permission.
![Lambda Role in Config](../images/askHero-lambda-role.png)

- Add the necessary following policies
  - **SecretsManagerReadWrite** - allows read/write access to AWS Secrets Manager.
  - **AmazonBedrockFullAccess** - allow access to Bedrock models.
- Click on the "Save" button to apply the changes. 

![Lambda role permission](../images/askHero-permission.png)

- Set the timeout for your Lambda function to 30 seconds, still in the "Configuration" tab.
- Scroll down to the "General configuration" section.
- In the "Timeout" field, enter "30" (without quotes) to set the timeout to 30 seconds.
- Click on the "Save" button to apply the changes.
![Lambda timeout](../images/askHero-timeout.png)
  
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
![Lambda test](../images/askSorcerer-test.png)

### Configure the Trigger for the Lambda Function
To configure the trigger for the Lambda function and connect to the topic in Redpanda Serverless using Kafka endpoint, follow these steps:

- In the function's configuration, go to the "Triggers" tab.
- Click on the "Add trigger" button.
- For the trigger configuration, choose "Kafka".
- Enter the required details:
    - **Bootstrap Server**: Provide the Kafka endpoint of your Redpanda Serverless cluster.
    - **Kafka topic**: Specify the name of the topic you want the Lambda function to subscribe to `npc1-request`.
    - **Batch size**: Set the batch size to 1 to retrieve one record at a time.
    - **Starting position**: Choose where to start reading messages, LATEST to start from the latest message.
    - **Authentication**: Select `SASL_SCRAM_256_AUTH` as the authentication mechanism.
    - **Secrets Manager key**: Enter the key **workshop/redpanda/lambda** for the Secrets Manager secret.

- Click on the "Add" button to attach the trigger to your Lambda function.
![Lambda trigger](../images/askHero-trigger.png)

This configuration will enable your Lambda function to receive messages from the specified Kafka topic in Redpanda Serverless, with a batch size of 1 record at a time, using SASL/SCRAM authentication and retrieving messages starting from the specified position.

### Test the result
Use the Redpanda Serverless console to post a text message in the "npc1-request" topic. Enter the value "Have you seen monster before?" as the message content.

![Redpanda hero question](../images/rp-test-question-hero.png)

After the Lambda function is triggered, check the "npc-response" topic to see the result.
![Redpanda response](../images/rp-topic-response-hero.png)


### Conclusion
By following these steps, you have successfully created and deployed another Lambda function that integrates with Redpanda Serverless using container. This function processes incoming messages from the "npc1-request" topic, generates intelligent responses using AWS Bedrock, and publishes the responses to the "npc-response" topic. 