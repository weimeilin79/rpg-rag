import boto3
from langchain_community.llms import Bedrock
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA

from langchain_aws import BedrockLLM
from langchain_core.prompts import PromptTemplate


# LangChain setup
session = boto3.Session(region_name = 'us-east-x', 
                        aws_access_key_id='x',
                        aws_secret_access_key='x',)
boto3_bedrock = session.client(service_name="bedrock-runtime")


retriever = AmazonKnowledgeBasesRetriever(
    region_name = 'us-east-1', 
    knowledge_base_id="TEPCFIZTYF",
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
)

# Langchain LLM
llm = BedrockLLM(client=boto3_bedrock, model_id="meta.llama2-13b-chat-v1", region_name='us-east-x')

# Define the user message to send.
input_query = "Tell me about you?"


# Define the prompt template with the context and user input
prompt_template = """You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question.sound more upbeat tone .
{context}
User: {question}
    """

PROMPT = PromptTemplate(
    input_variables=["context","question"], 
    template=prompt_template
)

qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": PROMPT},
    )

response = qa(input_query)

print(response)