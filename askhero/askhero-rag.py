import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from langchain.text_splitter import CharacterTextSplitter

from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_community.llms import Ollama

host = 'xiegh39p77tea8gi3uo5.us-east-1.aoss.amazonaws.com' # NB without HTTPS prefix, without a port - be sure to substitute your region again
region = 'us-east-1' # substitute your region here
service = 'aoss'


# LangChain setup
session = boto3.Session(region_name = 'us-east-1', 
							)
session_creds = session.get_credentials()
auth = AWSV4SignerAuth(session_creds, region, service)

client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")



#Loading the story

loader = DirectoryLoader('./story', glob="./corin.md", show_progress=True)

documents = loader.load()

print("--->" + str(len(documents)))

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

docsearch = OpenSearchVectorSearch.from_documents(
    docs,
    embeddings,
    opensearch_url=f'https://{host}:443',
    engine="faiss",
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    index_name='hero_index'
)



llm = Ollama(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)


# RAG Prompt
retriever = docsearch.as_retriever()
prompt_template = """You must provide an answer."
                
                "context": "You are a hero who lives in the fantasy world, you just defeated a monster, has been asked a question. 
                sound more upbeat tone ."

    user: {input_query}
    """
prompt = PromptTemplate(
        input_variables=["input_query"], template=prompt_template
)

chain = (
    prompt
    | llm
    | StrOutputParser()
)
# The result here should be a well-formatted answer to our question
print(chain.invoke("Tell me about you?"))
