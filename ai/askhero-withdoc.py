from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from kafka import KafkaConsumer,KafkaProducer
import json

from langchain_community.document_loaders import DirectoryLoader
from langchain_core.prompts import ChatPromptTemplate

REDPANDA_SERVER = "localhost:19092"


# Create a Kafka consumer
consumer = KafkaConsumer(
    'npc1-request',  # Kafka topic to consume from
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address    group_id='llm-bedrock-bot',
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

loader = DirectoryLoader('./story', glob="./Corin.md", show_progress=True)

docs = loader.load()


chat_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("You are a hero Corin in the following pieces of context, has been asked a question. You must provide an answer."
                "sound more upbeat tone. Don't answer if the question is not in the context."

                "{context}"           
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)


def query_data(question):
    messages = chat_template.format_messages(context=docs[0].page_content, text=question)
    response_msg =  llm.invoke(messages)
    # Define the message to be sent
    message_data = {
        "who": "npc1",
        "msg": response_msg  # Assume this is your dynamic response message
    }
    producer.send('rpg-response', message_data)



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