import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.document_loaders import TextLoader
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain import LangChain

host = 'xiegh39p77tea8gi3uo5.us-east-1.aoss.amazonaws.com' # NB without HTTPS prefix, without a port - be sure to substitute your region again
region = 'us-east-1' # substitute your region here
service = 'aoss'
credentials = boto3.Session().get_credentials()

auth = AWSV4SignerAuth(credentials, region, service)

client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Embeddings
# create HuggingFaceEmbeddings with BGE embeddings
model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
mbeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
dimensions = 1024

# Index Creation
index_name = "charcter-hero"
indexBody = {
    "settings": {
        "index.knn": True
    },
    "mappings": {
        "properties": {
            "vector_field": {
                "type": "knn_vector",
                "dimension": dimensions,
                "method": {
                    "engine": "faiss",
                    "name": "hnsw"
                }
            }
        }
    }
}

try:
    create_response = client.indices.create(index_name, body=indexBody)
    print('\nCreating index:')
    print(create_response)
except Exception as e:
    print(e)
    print("(Index likely already exists?)")


loader = TextLoader("./stateoftheunion.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

docsearch = OpenSearchVectorSearch.from_documents(
    docs,
    embeddings,
    opensearch_url=f'https://{host}:443',
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    index_name=index_name
)



# Document Search
query = "What is happening with Justice Breyer"
docs = docsearch.similarity_search(query, k=200)

print('Total results:', len(docs))
# The result here should be the document which closest resembles our question - the RAG phase actually formats an answer. 
print('Best result:', docs[0].page_content)


# RAG Prompt
retriever = docsearch.as_retriever()
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI()
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
# The result here should be a well-formatted answer to our question
print(chain.invoke(query))