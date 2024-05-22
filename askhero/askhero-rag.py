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
service = 'es'


# LangChain setup
session = boto3.Session(region_name = 'us-east-1', 
                        aws_access_key_id='',
                        aws_secret_access_key='',)
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



# Document Search
query = "Tell me about the hero"
docs = docsearch.similarity_search(query, k=10)

print('Total results:', len(docs))
# The result here should be the document which closest resembles our question - the RAG phase actually formats an answer. 
print('Best result:', docs[0].page_content)

llm = Ollama(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)


# RAG Prompt
retriever = docsearch.as_retriever()
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
# The result here should be a well-formatted answer to our question
print(chain.invoke(query))