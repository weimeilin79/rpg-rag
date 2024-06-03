
## Create a New User in IAM

### Sign in to the AWS Management Console
Open the AWS Management Console at https://aws.amazon.com/ and sign in with your credentials.

### Navigate to the IAM Dashboard
In the AWS Management Console, select Services and then choose IAM under the "Security, Identity, & Compliance" category.

### Add a New User
In the IAM dashboard, click on Users in the left-hand navigation pane.
Click the Add user button at the top of the page.

### Set User Details
User name: Enter a unique username for the new user.
Access type: Select Programmatic access.

### Review and Create User
Review the user details and permissions. Click the Create user button.

### Download Credentials
On the final page, you will see the user’s access key ID and secret access key. Download the credentials file and store it in a secure place. You will need it later.

## Enable AWS IAM Permissions for Bedrock
### Attach Policies to the User
- After creating the user, you need to attach policies that allow access to Bedrock.
- In the IAM dashboard, click on Users and select the newly created user from the list.
- Go to the Permissions tab and click on Add permissions.

### Add Permissions
- Choose Attach policies directly.
- Search for and select the appropriate policies that grant access to Bedrock. These policies include:
    - **AmazonBedrockFullAccess**: This policy grants full access to Bedrock resources.
    - **AmazonBedrockReadOnlyAccess** : This policy grants read-only access to Bedrock resources.
- Select the policies and click on the Next: Review button.
- Review the permissions and click on the Add permissions button.

### Create Inline Policy (Optional)
- To grant Bedrock access to your identity, you can:
    - Open the AWS IAM Console.
    - Find your User.
    - Select Add Permissions > Create Inline Policy to attach new inline permissions, open the JSON editor and paste in the below example policy:
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockFullAccess",
                "Effect": "Allow",
                "Action": ["bedrock:*"],
                "Resource": "*"
            }
        ]
    }
    ```

## Sign up for Bedrock
- Amazon Bedrock is a fully managed service that provides access to foundation models available via an API. With Bedrock, you can choose from a variety of models to find the one that’s best suited for your use case.
- In US-EAST-1, go to https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess and enable the service.

## Setup a Container Registry

### Navigate to Amazon ECR
- In the AWS Management Console, select Services.
- Under the "Containers" category, choose Elastic Container Registry.

### Create a Repository
- In the Amazon ECR dashboard, click on Repositories.
- Click the Create repository button at the top of the page.

### Configure the Repository

**Cluster name**: `redpanda-workshop`.
**Visibility settings**:  `Private`, The repository is only accessible to your AWS account.

### Create the Repository

- Review your settings and click the Create repository button.
  
Copy URI `xxx.dkr.ecr.us-east-1.amazonaws.com/redpanda-workshop`

## Setup Secret Manager

### Open the Secrets Manager Console
- Open the Secrets Manager console at https://console.aws.amazon.com/secretsmanager/.

### Create a New Secret
- Choose Store a new secret.
- On the Choose secret type page, do the following:
- For Secret type, choose **Other type of secret**.
- In Key/value pairs, either enter your secret in JSON Key/value pairs, or choose the Plaintext tab and enter the secret in any format. You can store up to 65536 bytes in the secret.


### Sign up for Redpanda Serverless Cluster

## Sign up and Create a Cluster
- Redpanda supports Dedicated Cloud, with clusters operating within the Redpanda Cloud environment, as well as Bring Your Own Cloud (BYOC), which allows clusters to run in your private cloud. Redpanda offers developers a third option known as "serverless," providing seamless and immediate access to streaming capabilities.

- For our workshop, we will be using the serverless platform. Go to https://cloud.redpanda.com/  and sign up for Redpanda Serverless by setting up your credentials.

- Click on the default namespace and enter the welcome cluster

NOTE: You have the ability to create multiple clusters under the namespace, it's great for projects that don’t need a dedicated cluster all the time, spiky workloads and needed separate virtual cluster for topic management.