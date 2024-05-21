### Open the S3 Console
- In the AWS Management Console, select Services and then choose S3 under the "Storage" category.
- Click the Create bucket button.
- Enter a name for your bucket and select the region.
- Click the Upload button.
- Click Add files and select the ZIP file you created (e.g., my_layer.zip).
- Click Upload to upload the file to S3.

### Create a New Lambda Function:

- Click the Create function button.
- Select Author from scratch.
- Function name: Enter a name for your Lambda function (e.g., MetaLlamaFunction).
- Runtime: Choose Go.
- Click Create function to create the function.

### Redpanda Connect in Lambda
- In the Lambda function editor, create a file `benthos.yaml` and enter the following code:

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
              - couk6ual9050bvlc7pm0.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
            topic: npc1-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: x
                password: x
          processors:
            - type: bloblang
              bloblang: |
                root = this.msg
      - check: this.who == "npc2"
        output:
          kafka_franz:
            seed_brokers:
              - couk6ual9050bvlc7pm0.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
            topic: npc2-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: x
                password: x
          processors:
            - type: bloblang
              bloblang: |
                root = this.msg
      - check: this.who == "npc3"
        output:
          kafka_franz:
            seed_brokers:
              - couk6ual9050bvlc7pm0.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
            topic: npc3-request
            tls:
              enabled: true
            sasl:
              - mechanism: SCRAM-SHA-256
                username: x
                password: x
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

### Use the ZIP File to Add a Layer to a Lambda Function

- In the Lambda dashboard, click on Layers in the left-hand navigation pane.
- Click the Create layer button.
**Name**: 'Redpanda Connect'.
**Description**: Optionally, enter a description for your layer.
**Upload**: Under the Code entry type section, select Upload a .zip file.
**S3 Link**: Choose Amazon S3 location and provide the link to the ZIP file you uploaded (e.g., s3://your-bucket-name/my_layer.zip).
**Runtime**: Select the runtimes compatible with your layer (e.g., Go 1.x).
= Click the Create button to create the layer.

### Add the Layer to Your Go Lambda Function

- In the Configuration tab, choose Layers from the left-hand menu.
- Click the Add a layer button.
- Choose Custom layers and select the layer you created .
- Select the version of the layer and click Add.
##  Add Redpanda as a Trigger to Lambda Functions
- In the Lambda dashboard, click on Functions in the left-hand navigation pane.
- Select the Lambda function you created 
  - askSFunction
  - LangChainFunction

### Add a Trigger
- In the Configuration tab, choose Triggers from the left-hand menu.
- Click the Add trigger button.

### Deploy the pipeline
- For Trigger configuration, choose Kafka.
- Enter the required details:
- Boostrap Server: Provide the ARN of your Kafka cluster.
- Kafka topic: Specify the topic your Lambda function should subscribe to.
- Batch size: Set the number of records to retrieve in each batch.
- Starting position: Choose where to start reading messages (e.g., TRIM_HORIZON to start from the beginning or LATEST to start from the latest message).
- Add Security Manager
- Click Add to attach the trigger to your Lambda function.

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