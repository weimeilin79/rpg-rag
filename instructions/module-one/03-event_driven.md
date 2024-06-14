## Data flow in Event Driven Architecture

Event-driven architecture is a powerful approach that enables systems to respond to events and triggers in real-time. In this architecture, data flows through various components, each responsible for handling specific events and performing relevant actions. 

To ensure seamless data integration and routing, a robust data integration pipeline is essential. This pipeline acts as a central hub, receiving incoming data and intelligently rerouting it to the appropriate service based on the event type and the specific model being used. 

By leveraging this data integration pipeline, organizations can efficiently handle different models and services, ensuring that each event is processed by the right component. This approach not only enhances scalability and flexibility but also enables the system to adapt to changing requirements and handle complex event-driven scenarios effectively.


### Upload Redpanda Connect Binary to S3
**Redpanda Connect** is a powerful data integration tool that enables seamless data processing and routing in event-driven architectures. With Redpanda Connect, you can easily handle different models and services, ensuring that each event is processed by the right component.

It is a powerful data integration tool written in Golang. It is designed to handle data processing and routing in event-driven architectures with ease. One of the key advantages of Redpanda Connect is its small footprint, making it an efficient choice for resource-constrained environments.

Being a single binary, Redpanda Connect offers simplicity and ease of deployment. You can quickly set up and configure Redpanda Connect without the need for complex installations or dependencies. This makes it a convenient choice for integrating different components in your event-driven architecture.And you can easily define data processing pipelines using a simple and intuitive configuration file in YAML. It supports various processors and output options, allowing you to customize your data flow according to your specific requirements.

Whether you need to transform, filter, or route data, Benthos provides a flexible and scalable solution. It seamlessly integrates with other components in your architecture, enabling smooth data flow and efficient handling of events.You can enhance the performance and reliability of your event-driven system. Its lightweight nature and efficient design make it an ideal choice for building robust and scalable data integration pipelines.

First, you'll upload the Redpanda binary file to S3
- Download the **Redpanda Connect** single binary from [here](tbd)
- In the AWS Management Console, select Services and then choose S3 under the "Storage" category.
- Click the Create bucket button, with Bucket type: General Purpose
- Enter a name `redpanda-connect` for your bucket,  go ahead with default values and create.
  
![Create Bucket](images/s3-bucket-create.png)

- Now, upload the binary, click the Upload button.
- Click Add files and select the `redpanda-connect-lambda-al2_4.27.0_linux_arm64.zip`.
- Click Upload to upload the file to S3.
- Copy the URL for this file in S3.
![Upload Binary](images/s3-upload.png)


### Use the ZIP File to Add a Layer to a Lambda Function

- In the Lambda dashboard, click on Layers in the left-hand navigation pane.
  ![Findlayer](images/lambda-find-layer.png)
- Click the Create layer button.
**Name**: `redpanda-connect-binary`.
**Upload**: Under the Code entry type section, select Upload a file from S3.
**S3 Link**: Choose Amazon S3 location and provide the link to the ZIP file you uploaded (The URL that was copied in previous step).
**Runtime**: Select the runtime `Amazon Linux 2` for the layer (e.g., Go 1.x).
- Click the Create button to create the layer.
![Create new layer](images/lambda-create-layer.png)

### Create a New Lambda Function:

- Click the Create function button.
- Select Author from scratch.
- Function name: Enter name `rerouteNPC` for the Lambda function.
- Runtime: Choose Amazon Linux 2. as we need Go runtime.
- Architecture: arm64
- Click Create function to create the function.

![Create new function](images/lambda-create-reroute.png)


### Redpanda Connect in Lambda
- In the Lambda function editor, create a file `benthos.yaml` and enter the following code,
  Make sure to replace your the <REDPANDA_BROKER_URL> and <REDPANDA_USER_PWD> with your Redpanda Broker URL and pwd to `1234qwer` :
```
pipeline:
  processors:
    - mapping: |
         root = this.records.values().index(0).index(0).value.decode("base64")
output:
  switch:
    cases:
      - check: this.who == "npc1"
        output:
          kafka_franz:
            seed_brokers:
              - <REDPANDA_BROKER_URL>
            topic: npc1-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: workshop
                password: <REDPANDA_USER_PWD>
          processors:
            - type: bloblang
              bloblang: |
                root = this.msg
      - check: this.who == "npc2"
        output:
          kafka_franz:
            seed_brokers:
              - <REDPANDA_BROKER_URL>
            topic: npc2-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: workshop
                password: <REDPANDA_USER_PWD>
          processors:
            - type: bloblang
              bloblang: |
                root = this.msg
      - check: this.who == "npc3"
        output:
          kafka_franz:
            seed_brokers:
              - <REDPANDA_BROKER_URL>
            topic: npc3-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: workshop
                password: <REDPANDA_USER_PWD>
          processors:
            - type: bloblang
              bloblang: |
                root = this.msg
  logger:
    level: DEBUG
    format: logfmt
    add_timestamp: false
    level_name: level
    timestamp_name: time
    message_name: msg
    static_fields:
      '@service': benthos

```
![Redpanda Connect Config](images/lambda-config-code.png)


### Add the Layer to Your Go Lambda Function

- In the Code tab, scroll down.
- Click the Add a layer button.
- 
![Layer Button](images/lambda-layer-button.png)

- Choose **Custom layers** and select the layer you created .

![Add Layer](images/lambda-add-layer.png)

- In the Code Source tab, if you see the __Changes not deployed__, click **Deploy** to update your function
![Deploy Reroute function](images/llambda-deploy-reroute.png)


### Configure the Trigger for the Lambda Function
To configure the trigger for the Lambda function and connect to the topic in Redpanda Serverless using Kafka endpoint, follow these steps:

- In the function's configuration, go to the "Triggers" tab.
- Click on the "Add trigger" button.
- For the trigger configuration, choose "Kafka".
- Enter the required details:
    - **Bootstrap Server**: Provide the Kafka endpoint of your Redpanda Serverless cluster.
    - **Kafka topic**: Specify the name of the topic you want the Lambda function to subscribe to `npc-request`.
    - **Batch size**: Set the batch size to 1 to retrieve one record at a time.
    - **Starting position**: Choose where to start reading messages, LATEST to start from the latest message.
    - **Authentication**: Select `SASL_SCRAM_256_AUTH` as the authentication mechanism.
    - **Secrets Manager key**: Enter the key **workshop/redpanda/lambda** for the Secrets Manager secret.

![Add Trigger](images/lambda-trigger-reroute.png)


### Test the result
Use the Redpanda Serverless console to post a text message in the "npc-request" topic. Enter the value below as the message content.

```
{
    "who": "npc1",
    "msg": "Where were you yesterday?"
}
```

![Redpanda question](images/rp-reroute-produce.pngrp-reroute-produce.png)
![Redpanda question create](images/rp-reroute-test.png)

After the Lambda function is triggered, check the "npc1-request" topic to see the result.
![Redpanda response](images/rp-topic-response-reroute.png)

### Clone the GitHub Repository and Start the Node.js App


Open a terminal or command prompt.
```
git clone https://github.com/weimeilin79/rpg-rag.git
```
Navigate to the frontend directory:
```
cd rpg-rag/frontend
```
Run the following command to install the necessary dependencies:
```
npm install
```
Start the Node.js application:
```
node index.js
```




## Challenge add another NPC 
Can you add another serverless function for a new NPC? 


{ "who": "npc1", "msg": "Where were you yesterday?" }