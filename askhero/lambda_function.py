import json
import os
import boto3
#from kafka import KafkaProducer
from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

# Environment variables for Kafka configuration
#REDPANDA_SERVER = os.environ['KAFKA_SERVER']  # Set this in your Lambda environment variables

# Kafka Producer setup
#producer = KafkaProducer(
#    bootstrap_servers=REDPANDA_SERVER,
#    value_serializer=lambda v: json.dumps(v).encode('utf-8')
#)

# LangChain setup
session = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id='x',
                        aws_secret_access_key='x/bnz074MrTvv7y3W',)
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-1')

prompt_template = """You must provide an answer."
                
                "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone ."

    user: {input_query}
    """

PROMPT = PromptTemplate(
        input_variables=["input_query"], template=prompt_template
)

llmChain = LLMChain(llm=llm, prompt=PROMPT)

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
        #producer.send('rpg-response', message_data)


def do_test():
    event = {
        "Records": [
            {
                "value": "how's your day?"
            }
        ]
    }
    lambda_handler(event, None)

def query_data(query):
    response_msg = llmChain.invoke({"input_query": query})
    return response_msg

do_test()