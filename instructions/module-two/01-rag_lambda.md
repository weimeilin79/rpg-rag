### CLoud 9 


### Update LangChain app with RAG by loading documents

### Update the bedrock one 

To create a knowledge base
Sign in to the AWS Management Console, and open the Amazon Bedrock console at https://console.aws.amazon.com/bedrock/.

From the left navigation pane, select Knowledge base.

In the Knowledge bases section, select Create knowledge base.

On the Provide knowledge base details page, set up the following configurations:

(Optional) In the Knowledge base details section, change the default name and provide a description for your knowledge base.

In the IAM permissions section, choose an AWS Identity and Access Management (IAM) role that provides Amazon Bedrock permission to access other AWS services. You can let Amazon Bedrock create the service role or choose a custom role that you have created.

(Optional) Add tags to your knowledge base. For more information, see Tag resources.

Select Next.

On the Set up data source page, provide the information for the data source to use for the knowledge base:

(Optional) Change the default Data source name.

Select Current account or Other account for Data source location

Provide the S3 URI of the object containing the files for the data source that you prepared. If you selection Other account you may need to update the other account's Amazon S3 bucket policy, AWS KMS key policy, and the current account's Knowledge Base role.

Note
Choose an Amazon S3 bucket in the same region as the knowledge base that you're creating. Otherwise, your data source will fail to sync.

If you encrypted your Amazon S3 data with a customer managed key, select Add customer-managed AWS KMS key for Amazon S3 data and choose a KMS key to allow Amazon Bedrock to decrypt it. For more information, see Encryption of information passed to Amazon OpenSearch Service.

(Optional) To configure the following advanced settings, expand the Advanced settings - optional section.

While converting your data into embeddings, Amazon Bedrock encrypts your data with a key that AWS owns and manages, by default. To use your own KMS key, expand Advanced settings, select Customize encryption settings (advanced), and choose a key. For more information, see Encryption of transient data storage during data ingestion.

Choose from the following options for the Chunking strategy for your data source:

Default chunking – By default, Amazon Bedrock automatically splits your source data into chunks, such that each chunk contains, at most, 300 tokens. If a document contains less than 300 tokens, then it is not split any further.

Fixed size chunking – Amazon Bedrock splits your source data into chunks of the approximate size that you set. Configure the following options.

Max tokens – Amazon Bedrock creates chunks that don't exceed the number of tokens that you choose.

Overlap percentage between chunks – Each chunk overlaps with consecutive chunks by the percentage that you choose.

No chunking – Amazon Bedrock treats each file as one chunk. If you choose this option, you may want to pre-process your documents by splitting them into separate files.

Note
You can't change the chunking strategy after you have created the data source.

Select Next.

In the Embeddings model section, choose a supported embeddings model to convert your data into vector embeddings for the knowledge base.

In the Vector database section, choose one of the following options to store the vector embeddings for your knowledge base:

Quick create a new vector store – Amazon Bedrock creates an Amazon OpenSearch Serverless vector search collection for you. With this option, a public vector search collection and vector index is set up for you with the required fields and necessary configurations. After the collection is created, you can manage it in the Amazon OpenSearch Serverless console or through the AWS API. For more information, see Working with vector search collections in the Amazon OpenSearch Service Developer Guide. If you select this option, you can optionally enable the following settings:

To enable redundant active replicas, such that the availability of your vector store isn't compromised in case of infrastructure failure, select Enable redundancy (active replicas).

Note
We recommend that you leave this option disabled while you test your knowledge base. When you're ready to deploy to production, we recommend that you enable redundant active replicas. For information about pricing, see Pricing for OpenSearch Serverless

To encrypt the automated vector store with a customer managed key select Add customer-managed KMS key for Amazon OpenSearch Serverless vector – optional and choose the key. For more information, see Encryption of information passed to Amazon OpenSearch Service.

Select a vector store you have created – Select the service that contains a vector database that you have already created. Fill in the fields to allow Amazon Bedrock to map information from the knowledge base to your database, so that it can store, update, and manage embeddings. For more information about how these fields map to the fields that you created, see Set up a vector index for your knowledge base in a supported vector store.

Note
If you use a database in Amazon OpenSearch Serverless, Amazon Aurora, or MongoDB Atlas, you need to have configured the fields under Field mapping beforehand. If you use a database in Pinecone or Redis Enterprise Cloud, you can provide names for these fields here and Amazon Bedrock will dynamically create them in the vector store for you.

Select Next.

On the Review and create page, check the configuration and details of your knowledge base. Choose Edit in any section that you need to modify. When you are satisfied, select Create knowledge base.

The time it takes to create the knowledge base depends on the amount of data you provided. When the knowledge base is finished being created, the Status of the knowledge base changes to Ready.



### deploy again, and run test