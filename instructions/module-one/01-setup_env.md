# Enhancing NPCs in Online RPG Games with AI and Serverless Architecture 

## Overview
Traditional RPG games are renowned for their rich and immersive worlds, populated by numerous NPCs (Non-Player Characters) that provide crucial information, hints, and contribute significantly to world-building. However, many current online games fall short in this aspect, with NPCs often reduced to repetitive, robotic dialogues, which can be quite monotonous. To address this, we are going to leverage AI to enhance NPC interactions in our next game, making them more dynamic and engaging.

To prototype this game, we have set the following requirements: the solution needs to be scalable to handle fluctuating traffic typical of online games. It must also scale down resources when they are not needed to optimize cost and efficiency. Therefore, we have decided to adopt a serverless architecture, utilizing streaming for data flow and an Event-Driven Architecture (EDA) as the backbone.

Benefits of Using AI with Serverless Architecture for NPCs:

Scalability and Cost Efficiency:
  - Dynamic Scaling
  - Pay-as-You-Go
Enhanced Player Experience:
  - Intelligent NPCs
  - Continuous Improvement
Efficient Data Handling with Streaming and EDA:
  - Real-time Data Processing
  - Event-Driven Flexibility
  - Modular Design
Seamless Integration and Maintenance:
  - Reliability and Resilience

By leveraging AI and serverless architecture, we can revolutionize NPC interactions in online RPG games, providing a more immersive, responsive, and engaging player experience while maintaining cost efficiency and scalability.

## Technology Stack 
In this workshop, we will leverage a variety of AWS and Redpanda technologies to build and deploy scalable, efficient, and intelligent systems.

- **AWS Lambda**: Serverless computing service to run code in response to events without provisioning or managing servers.
- **AWS Bedrock**: Powerful models for natural language processing and chat functionalities.
- **LangChain**: Framework for developing applications powered by language models, streamlining AI integration.
- **Redpanda Serverless**: Scalable and high-throughput data streaming.
- **Redpanda Connect**: Facilitates seamless data flow integration with various endpoints.



## Sign up for Bedrock
- Amazon Bedrock is a fully managed service that provides access to foundation models available via an API. With Bedrock, you can choose from a variety of models to find the one that’s best suited for your use case.
- In US-EAST-1, go to https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess and enable the following model.



## Sign up for Redpanda Serverless Cluster

### Sign up and Create a Cluster
Redpanda supports Dedicated Cloud, with clusters operating within the Redpanda Cloud environment, as well as Bring Your Own Cloud (BYOC), which allows clusters to run in your private cloud. Redpanda offers developers a third option known as "serverless," providing seamless and immediate access to streaming capabilities.

- For our workshop, we will be using the serverless platform. To start using Redpanda Serverless, [sign up](https://cloud.redpanda.com/sign-up/) for a free trial. Each trial supports five Serverless clusters. 

- Click on the default namespace and enter the welcome cluster
![Serverless Overview](../images/rp-overview.png)

Note: You have the ability to create multiple clusters under the namespace. It's great for projects that don’t need a dedicated cluster all the time, have spiky workloads, or need separate virtual clusters for topic management.

### Get Redpanda bootstrap URL
- In Overview, under How to connect, click on the `Kafka API`, you'll find the **Bootstrap server URL**, make sure you save it somewhere for later.
![Redpanda Bootstrap URL](../images/rp-bootstrap.png)

### Securing Redpanda
- Configure authentication by going to security and create a new user. 
- Set the username to `workshop`, password to `1234qwer`
![Serverless Create new user](../images/rp-create-user.png)


Access-control lists (ACLs) are the primary mechanism used by Redpanda to manage user permissions. 

- On the top tab, click **ACL** and click on the `workshop` principle that you have just created
![Serverless Create ACL](../images/rp-create-acl.png)

- Grant permissions to the newly created credentials. In the configuration page, chose to grant all permission and click OK to save. 
![Serverless Config ACL](../images/rp-acl-config.png)


## Setup Secret Manager

Securely managing sensitive information like the credentials, and encryption keys is crucial. AWS Secret Manager provides a secure and scalable solution for storing and managing secrets. With Secret Manager, you can easily store, retrieve, and rotate secrets, ensuring that your applications have access to the necessary credentials without compromising security.

In this section, we will walk you through the process of setting up Secret Manager and demonstrate how to create and manage secrets. By the end of this tutorial, you will have a solid understanding of how to leverage Secret Manager to enhance the security of your applications.

Let's get started!

### Open the Secrets Manager Console
- Open the Secrets Manager console at https://console.aws.amazon.com/secretsmanager/.

### Create a New Secret
- Choose Store a new secret.
- On the Choose secret type page, do the following:
- For Secret type, choose **Other type of secret**.
- In Key/value pairs,  enter your secret in JSON Key/value pairs and configure the following key/value. And click Next.
    - REDPANDA_SERVER :  **Your Redpanda Bootstrap server URL**
    - REDPANDA_USER : `workshop`
    - REDPANDA_PWD : `1234qwer`
![Secrets manager configurations](../images/secretsmanager-config.png)  

- Name the Secret name : `workshop/redpanda/npc` and go through the steps with default value until you reach step Review, click **store** button to finish setting up the secret.
![Secrets manager name](../images/secretsmanager-name.png)  

- You'll see the secret created.
![Secrets manager list](../images/secretsmanager-list.png)  

Create another new secret called `workshop/redpanda/lambda` for the lambda trigger, repeat above steps with following configuration:
    - username : `workshop`
    - password : `1234qwer`

## Set Up AWS Cloud9 Workspace
Next, create a workspace for the Redpanda workshop, follow these steps:

- navigate to the AWS Cloud9 service.
- Click on the "Create environment" button.
  - Enter a name for your workspace,`redpanda-workshop`.
  - Choose "Create a new EC2 instance for environment (direct access)" as the environment type.
  - Select "t3.small" as the instance type.
  - Set the timeout value to 4 hours.
-  Review the configuration and click on the "Create environment" button.
![Cloud9 Setup](../images/cloud9-setup.png)

-  Wait for the workspace to be created. Once it's ready, you can access it by clicking on the "Open IDE" button.
![Cloud9 Setup](../images/ccloud9-list.png)

Now you have a Cloud9 workspace set up for the Redpanda workshop. You can use this workspace to follow along with the instructions and complete the workshop tasks.

This concludes the setup instructions. By following these steps, you will be prepared to leverage AI and serverless architecture to enhance NPC interactions in your online RPG game, ensuring scalability, efficiency, and an improved player experience.


