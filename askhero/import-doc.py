import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
#from langchain.text_splitter import CharacterTextSplitter

#from langchain.schema.runnable import RunnablePassthrough
#from langchain.schema.output_parser import StrOutputParser
#from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader
#from langchain_community.vectorstores import OpenSearchVectorSearch
#from langchain_community.llms import Ollama
from opensearchpy.helpers import bulk, BulkIndexError

host = 'x' # NB without HTTPS prefix, without a port - be sure to substitute your region again
region = 'us-east-x' # substitute your region here
service = 'aoss'


# LangChain setup
session = boto3.Session(region_name = 'us-east-x',
                        aws_access_key_id='x',
                        aws_secret_access_key='x',)

session_creds = session.get_credentials()
auth = AWSV4SignerAuth(session_creds, region, service)

client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Define the index name
index_name = 'hero_index'


#Loading the story

loader = DirectoryLoader('./story', glob="./corin.md", show_progress=True)

documents = loader.load()
print("--->" + str(len(documents)))


# Initialize the HuggingFaceEmbeddings model
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


texts = [doc.page_content for doc in documents]  
embeddings = embeddings_model.embed_documents(texts)

# Prepare documents for indexing
docs_to_index = []
for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
    doc_body = {
        'text': doc.page_content, 
        'embedding': embedding 
    }
    # Add the document to the bulk request
    docs_to_index.append({
        '_op_type': 'index',  
        '_index': index_name,
        '_source': doc_body
    })

# Bulk insert documents and handle errors
try:
    bulk(client, docs_to_index)
    print("Documents indexed successfully.")
except BulkIndexError as e:
    # Print detailed error information
    print(f"Bulk indexing error: {e}")
    for error in e.errors:
        print(error)


