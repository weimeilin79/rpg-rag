## Setup Bedrock KnowledgebKnowledgeBasease

To set up the knowledge base in Amazon Bedrock, follow these steps:

- Navigate to the Amazon Bedrock service, Click on "Create Knowledge Base" to start the setup process.
![Bedrock KnowledgeBase 01](../images/nb-step-01.png)
- Provide a name for your knowledge base or use the default generated name, select the **create and use a new service role** and click *Next*
![Bedrock KnowledgeBase 02](../images/nb-step-02.png)
- In the Configure data source page, under Amazon S3 URI section, click on the **Browse S3** button, add the `redpanda-workshop` bucket  
![Bedrock KnowledgeBase 03](../images/nb-step-03.png)
- Select **Titan Embedding G1** as the embedding model and check the **Quick Create a new vector store**, it will create a new collection in the OpenSearch Serverless 
![Bedrock KnowledgeBase 04](../images/nb-step-04.png)
- Check the configuration again and click **Create knowledge base** to start creating.
![Bedrock KnowledgeBase 05](../images/nb-step-05.png)
- It'll take a few minutes to setup, once done, let's go ahead to sync the documents in the S3 bucket to the vector store by going to the Data source section, select the knowledge base you just created and click on the **sync** button.
![Bedrock KnowledgeBase 06](../images/nb-step-06.png)
- On the right-hand panel, you'll see a section to test knowledge base select **Claude Instant
v1.2** as the model
![Bedrock KnowledgeBase 07](../images/nb-step-07.png)
- Put in your question specific about the character, and click **Run**
![Bedrock KnowledgeBase 08](../images/nb-step-08.png)
- Also see the newly created collection in the OpenSearch Serverless Service
![Bedrock KnowledgeBase 09](../images/nb-step-09.png)



## Update the sorcerer function to use the
