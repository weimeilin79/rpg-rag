## Start Cloud9 


# Building without Langchain
In this lab, we will show how to make a basic API call directly to Bedrock.

You can build the application code by copying the code snippets below and pasting into the indicated Python file.



```

```


```
git clone http://therepo
```

The langchain 

in the `lambda_function.py` 

```
import json
import os
import boto3
from kafka import KafkaProducer
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain_core.prompts import PromptTemplate
import boto3
from botocore.exceptions import ClientError



# Secret Manager setup
secret_name = "demo/redpanda/rpg"
region_name = "us-east-2"
    # Create a Secrets Manager client
sessionSM = boto3.session.Session()
client = sessionSM.client(
        service_name='secretsmanager',
        region_name=region_name
    )
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
```

LangChain and LLM setup
```
# LangChain setup
session = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id=bedrock_key,
                        aws_secret_access_key=bedrock_secret,)
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-1')

```

Prompt
```

prompt_template = """You must provide an answer."
                
                "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone ."

    user: {input_query}
    """

PROMPT = PromptTemplate(
        input_variables=["input_query"], template=prompt_template
)

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

Build the image

```
docker build --platform linux/arm64 -t redpanda-workshop .
```

Running locally

```
```

### Deploying lambda with images


### Building without langchain

