from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from kafka import KafkaConsumer,KafkaProducer
import json
REDPANDA_SERVER = "localhost:19092"


# Create a Kafka consumer
consumer = KafkaConsumer(
    'npc3-request',  # Kafka topic to consume from
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
    group_id='llm-bedrock-bot',
    value_deserializer=lambda x: x.decode('utf-8')  # decode messages from bytes to string
)

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
     value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializer to convert to JSON
)



llm = Ollama(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)


def query_data(query):
    messages = chat_template.format_messages(text=query)
    response_msg =  llm.invoke(messages)
    # Define the message to be sent
    message_data = {
        "who": "npc3",
        "msg": response_msg  # Assume this is your dynamic response message
    }
    producer.send('rpg-response', message_data)


chat_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                "You are a goddess of wisdom and knowledge in a fantasy world, You are asked a question and you provide an answer. "
                "Your personality is a lay back, calm, with a hint of sexiness in your voice."
            )
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)



try:
    for message in consumer:
        # Extract the question from the message value
        question = message.value
        print(f"Received question: {question}")
        # Query the data with the question
        llmResult = query_data(question)
        

except KeyboardInterrupt:
    pass

finally:
    # Close the consumer
    consumer.close()