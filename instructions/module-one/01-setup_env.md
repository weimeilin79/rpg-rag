# Sign up Bedrock

Amazon Bedrock is a fully managed service that provides access to FMs from third-party providers and Amazon; available via an API. With Bedrock, you can choose from a variety of models to find the one that’s best suited for your use case.

In US-EAST-1 go to 
https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

And enable

### Enable AWS IAM permissions for Bedrock

We'll first setup AWS identity by creating an IAM User with sufficient [AWS IAM permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) to call the Amazon Bedrock service.

To create an user in IAM


To grant Bedrock access to your identity, you can:

- Open the [AWS IAM Console](https://us-east-1.console.aws.amazon.com/iam/home?#)
- Find your [User](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users)
- Select *Add Permissions > Create Inline Policy* to attach new inline permissions, open the *JSON* editor and paste in the below example policy:

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

# Setup container registry

### Create an image repository
A repository is where you store your Docker or Open Container Initiative (OCI) images in Amazon ECR. Each time you push or pull an image from Amazon ECR, you specify the repository and the registry location which informs where to push the image to or where to pull it from.

Open the Amazon ECR console at https://console.aws.amazon.com/ecr/.

Choose Get Started.

For Visibility settings, choose `Private`.

For Repository name, type in `redpanda-workshop`

For Tag immutability, choose the tag mutability setting for the repository. Repositories configured with immutable tags will prevent image tags from being overwritten. For more information, see Image tag mutability.

For Scan on push, choose the image scanning setting for the repository. Repositories configured to scan on push will start an image scan whenever an image is pushed, otherwise image scans need to be started manually.

Important
Configuring image scanning at the repository level has been deprecated in favor of configuring it at the registry level. For more information, see Image scanning.

For KMS encryption, choose whether to enable server-side encryption using AWS KMS keys stored in the AWS Key Management Service service. For more information about this feature, see Encryption at rest.

Choose Create repository.

Build, tag, and push a Docker image
In this section of the wizard, you use the Docker CLI to tag an existing local image (that you have built from a Dockerfile or pulled from another registry, such as Docker Hub) and then push the tagged image to your Amazon ECR registry. For more detailed steps on using the Docker CLI, see Using Amazon ECR with the AWS CLI.

Select the repository you created and choose View push commands to view the steps to push an image to your new repository.

Run the login command that authenticates your Docker client to your registry by using the command from the console in a terminal window. This command provides an authorization token that is valid for 12 hours.

(Optional) If you have a Dockerfile for the image to push, build the image and tag it for your new repository. Using the docker build command from the console in a terminal window. Make sure that you are in the same directory as your Dockerfile.

Tag the image with your Amazon ECR registry URI and your new repository by pasting the docker tag command from the console into a terminal window. The console command assumes that your image was built from a Dockerfile in the previous step. If you did not build your image from a Dockerfile, replace the first instance of repository:latest with the image ID or image name of your local image to push.

Push the newly tagged image to your repository by using the docker push command in a terminal window.

Choose Close.
### Setup secret manager
To create a secret (console)
Open the Secrets Manager console at https://console.aws.amazon.com/secretsmanager/.

Choose Store a new secret.
Choose Next.
On the Choose secret type page, do the following:

For Secret type, choose Other type of secret.

In Key/value pairs, either enter your secret in JSON Key/value pairs, or choose the Plaintext tab and enter the secret in any format. You can store up to 65536 bytes in the secret. Some examples:


secret_name = "demo/redpanda/rpg"
Choose Next.

### Sign up for Redpanda Serverless cluster
Redpanda supports **Dedicated Cloud**, with clusters operating within the Redpanda Cloud environment, as well as **Bring Your Own Cloud (BYOC)**, which allows clusters to run in your private cloud. Redpanda offers developers a third option known as "serverless," providing seamless and immediate access to streaming capabilities.

We will be utilizing a serverless platform.

Sign up by setting up your credentials.
![Sign up](../assets/step-2-signup.png)

Click on the `default` namespace .
![New name space](../assets/step-2-namespace.png)

Click to enter the welcome cluster
![Create cluster](../assets/step-2-create-cluster.png)
> You have the ability to create multiple clusters under the namespace, it's great for projects that don’t need a dedicated cluster all the time, spiky workloads and needed separate virtual cluster for topic management.

In your working lab environment, login to the cloud.
```bash,run
rpk cloud login --no-browser
```

Click on the authentication link in the terminal, you will be prompted that you have signed in successfully. If not, please login with the email you used to registered for the masterclass.

> This command checks for an existing Redpanda Cloud API token and, if present, ensures it is still valid.

Once login, choose the `welcome` cluster. You will be prompted with your broker address, make a note of it, we will be using it later.

Next you'll defined a set of user credential that will be authenticated by the Redpanda cluster.

Go to __Security__ on the left menu, click on the **Create User** button,
and enter `myuser` as the username and set password to `1234qwer`, select `SCRAM-SHA-256` and hit **create** button.
![Create ACL User](../assets/step-2-acl-user.png)

You'll need to set up the new user authorizations, grant user permission to perform operations on topics, groups and etc. Click on the newly created `myuser` to set the ACL, we'll grant access to **Allow all operations**, and click **OK**.

![Create ACL User](../assets/step-2-grant-all-acl.png)

You are all set to start streaming with Redpanda Serverless.