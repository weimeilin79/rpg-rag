import json
import os
import boto3

from langchain_community.llms import Bedrock
from langchain_aws import BedrockLLM
from langchain_core.prompts import PromptTemplate
import boto3
from botocore.exceptions import ClientError

# LangChain setup
session = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id='x',
                        aws_secret_access_key='x',)
boto3_bedrock = session.client(service_name="bedrock-runtime")

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-1')
input_query = "どこから来たのか、何をしているのか教えてください"
prompt_template = """

What language is the sentence "{input_query}" written in? and Translate the sentence below to English. Return in JSON format with language field that it is written in and the field msg of the translated result, don't reply anything else other then the JSON



    """
PROMPT = PromptTemplate(
        input_variables=["input_query"], template=prompt_template
)

chain = PROMPT | llm

response_msg = chain.invoke({"input_query": input_query})

print(response_msg.trimmed_output())