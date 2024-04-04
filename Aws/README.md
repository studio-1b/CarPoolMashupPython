# Instructions for running Carpool container in AWS

Login to AWS

## Manually configuring AWS, ECS-Fargate to run image from existing image

### 3 Options to deploy to Amazon AWS ECS (bolded)
1. **Ok Practices method:** Pull Image from AWS ECR-private, run in AWS ECS, manually adding the KEYS as environment variables
    - A private repo in AWS ECR, only users with access to your AWS account, can pull this image, so it can have secrets inside, but better not to
    - When you create AWS ECS Fargate container/service/cluster, you specify environment variables.  Carpool (as well as many containerized applications) can read secrets from environment variables.  Secrets meaning username/passwords/keys.  The person creating the ECS container/service/cluster knows has to know the secrets, to enter it as hardcoded environment variables.
        * Needed: Google API KEY
        * Know how to check AWS Account Credentials for Roles, 
        * Be able to create AWS ECS container/service/cluster 
2. **Better Practices method:** Pull cleaned (and no proprietary information inside) image from AWS ECR-public, run in AWS ECS, and specify Environment Variables to pull from AWS Parameter Store
    - A public repo in AWS ECR, all users on internet can pull this image, so it CANNOT have proprietary information, nor passwords stored inside the repo image, b/c it will be available for anyone to examine using the right tools available on the internet.
    - When you create AWS ECS Fargate container/service/cluster, and specify environment variables, there is a dropdown option for "ValueFrom".  The default is "Value".  Changing it to "ValueFrom" allows you to paste a AWS Parameter Store URL.  A AWS Parameter Store URL, is a unique identifier for a variable created in your AWS Account.  You put secrets such as username/passwords/keys/connectionsstring/privateurl in AWS Parameter Store.  The ECS will read from this parameter store and put it in the container environment variable on startup.  A good feature is that you can secure the Parameter Store value from other eyes who create the ECS container/service/cluster, and they only see the URL (starts with ARN).  Using AWS Parameter store also has the advantage that you only have to change these keys/passwords in one place.  The bad thing is that bc they are environment variables, injected on startup, the containers need to be restarted to reflect any changes.
        * Needed: Google API Key
        * Know how to check AWS Account Credentials for Roles
        * (new) Know how to change AWS Role permission, to read Parameter below
        * (new) Know how to create AWS Parameter Store to store above Parameter key
        * Be able to create AWS ECS container/service/cluster 
        * (new) While doing above, know how to change environment variable setting to read from parameter store
3. **Best Practice method:** Use a AWS CloudFormation JSON template.  It should have the configurations you redo in the above steps, but all stored in a file.  
    - And whenever you want to create a new ECS container/service/cluster, you just paste the JSON(or YAML) into AWS CloudFormation
        * Needed: Google API Key
        * Know how to check AWS Account Credentials for Roles
        * Know how to change AWS Role permission, to read Parameter below
        * Know how to create AWS Parameter Store to store above Parameter key
        * ~~(deleted) Be able to create AWS ECS container/service/cluster~~ 
        * ~~(deleted) how to change environment variable to read from parameter store~~
        * (new) Know how to change a json file, for same data, entered in other steps
        * (new) Use AWS Cloudformation upload the json(or YAML) file to create the ECS container/service/cluster

### Detailed steps

(Options 2 & 3) Create "Parameter Store (Systems Manager feature)" in AWS.  You can search for it.
- You need to store the Google API KEY as value, and give it a unique name, ie. like mine: GOOGLE_JAVASCIPT_MAP_KEY
- Reference: https://aws.plainenglish.io/managing-ecs-application-secrets-with-aws-parameter-store-a1f37db10575
- The user who will be creating the ECS container, has to have this permission assigned to read the the value (which is the API KEY).
4. Preformatted text in a list item:
        {   "Version": "2012-10-17",
            "Statement": [
                {   "Effect": "Allow",
                    "Action": "ssm:GetParameters",
                    "Resource": [ "arn:aws:ssm:us-east-1:1XXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY" ]
                } ] }
To Add this permission, goto Users (or Role, depending on who is missing this)

(Options 1 & 2)
Find ECS.  Create a service, task defintion, and cluster.
- Reference:[https://aws.plainenglish.io/deploying-a-docker-container-in-aws-using-fargate-5a19a140b018](https://aws.plainenglish.io/deploying-a-docker-container-in-aws-using-fargate-5a19a140b018)

Task Defintion:
- Task definition family: <anything you want, ie.carpool-family>
- Container Name:         <anything you want, ie.carpool-container>
- Image URI:              public.ecr.aws/y8w3p2i4/carpoolmashup-with-testdata:latest
- Execution Role:         <This also has to have permission above>
- expose port             80
- (Option 2) you need 2 add environment variables (the values must exist in)
   * You must select       ValueType="ValueFrom"
   * GOOGLE_GEOCODE_API_KEY="arn:aws:ssm:XX-XXXX-X:1XXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY"
   * GOOGLE_MAP_JS_API_KEY="arn:aws:ssm:XX-XXXX-X:1XXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY"
   * the "arn:" URL directs ECS to search the parameter store, for the value.
   * (Option 1) In a pinch, you can directly, paste the API KEY in the value field for the environment variable.  But you will be sacrificing security of the key, and you might have to change it in several places, if you need to invalidate it and change them
   * In this case, you need to select Value type="Value"
      - GOOGLE_GEOCODE_API_KEY="KEYXXX"
      - GOOGLE_MAP_JS_API_KEY="KEYXXX"
- After Task is created, Click Deploy > Create Service
Create a Service
- You don't have cluster yet (or if you skipped ahead, pick the one you created)
  * Click "Create a new cluster"
    - This should have popped up a new window or tab
    - Create a Cluster
      - Cluster name: <anything you want, ie.carpool-cluster>
      - AWS Fargate: checked
    - Close this new window/tab
  * click "refresh" for cluster
  * Service name: <anything you want, ie.carpool-service>
  * VPC: Any
  * Subnet: Any
  * Security Group: Any that allows port 80
  * public IP: checked

> [!WARNING]
> This is the message you get, when starting service, when the container's execution role doesn't have the correct permissions
> Task stopped at: 2024-03-31T02:56:45.407Z
> ResourceInitializationError: unable to pull secrets or registry auth: execution resource retrieval failed: unable to retrieve secrets from ssm: service call has been retried 1 time(s): AccessDeniedException: User: arn:aws:sts::XXXXXXXXX:assumed-role/ecsTaskExecutionRole/7cb7b3bcc4b642298dc313b41fdc8d9d is not authorized to perform: ssm:GetParameters on resource: arn:aws:ssm:us-east-1:XXXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY because no identity-based policy allows the ssm:GetParameters action status code: 400, request id: abf11493-709e-4424-af02-ceede85c64f7

> [!WARNING]
> Having a Security Group assignment wrong, will not fail the container startup, but the Security Group is essentially a simple firewall configuration.  And misconfigured, it might block port 80, which is what the carpool container is programmed to start on

After "the service" (which is last step) has started, you can find the public IP address at:
  - (In created cluster) > Tasks > click task > Network Bindings > external IPv4 link

Copy and paste (the IP address above) into your browser to trial the Carpool application
  - Test on your browser, at your liesure

To stop carpool (b/c AWS ECS Fargate includes a daily cost, which adds up to about USD$24/mo), 
  - Remove/delete the task and service.  You can un-register the task definition.  There is no free tier for running a ECS service.  It is about $24/mo.



## To skip steps above, and just cut and paste one file into AWS CloudFormation

(Option 3)

Find CloudFormation in AWS.  Create a Stack, using existing template.

Read the file:

```bash
cat carpool_ECS_cloudformation_template.json 
```

edit the file for these items

    "SecurityGroupIDs".Default
    "SubnetIDs".Default
    "VpcID".Default

which is surrounded with "**" and "**" below:
```
     "SecurityGroupIDs": {
        "Type": "CommaDelimitedList",
        "Default": "**sg-XXXXXXXXXXXXX**"
      },
      "SubnetIDs": {
        "Type": "CommaDelimitedList",
        "Default": "**subnet-XXXXXXXXXXXX,subnet-XXXXXXXXXX**"
      },
      "VpcID": {
        "Type": "String",
        "Default": "**vpc-XXXXXXXXXXX**"
      },
      "LoadBalancerName": {
        "Type": "String",
        "Default": ""
      }
```
and this item, for 2 environment variables

     Container.Definition.Secrets

which is surrounded with "**" and "**" below
```
"Secrets": [
	{ "name": "GOOGLE_GEOCODE_API_KEY", "valueFrom": "**arn:aws:ssm:us-XXXX-X:XXXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY**"},
	{ "name": "GOOGLE_MAP_JS_API_KEY", "valueFrom": "**arn:aws:ssm:us-XXXX-X:XXXXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY**"}
]
```
and this item might already exist in your AWS, but you need to change the URL for the role in your account. the role needs to have permission to read the secret specified in the URL

    Resource.ECSTask.Properties.ExecutionRoleArn

which is surrounded with "**" and "**" below
```
   "Resources": {
        "ECSTask": {
            "Type": "AWS::ECS::TaskDefinition",
            "Properties": {
                "RequiresCompatibilities": [
                    "FARGATE"
                ],
                "ExecutionRoleArn": "<b>arn:aws:iam::XXXXXX:role/ecsTaskExecutionRole</b>",
```

My Role (url: arn:aws:iam::XXXXX:role/ecsTaskExecutionRole), under Security Credentials > Roles (on left side), has URL under ARN.  This is what you paste above in ExecutionRoleArn.
It has this as Inline Permission added below, to read the Parameter Store Value "GOOGLE_JAVASCRIPT_MAP_KEY".  You may need to add permission, for the key you created
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "StatementCarpoolParameter",
            "Effect": "Allow",
            "Action": "ssm:GetParameters",
            "Resource": [
                "arn:aws:ssm:us-XXXX-X:XXXXXXXXX:parameter/GOOGLE_JAVASCIPT_MAP_KEY"
            ]
        }
    ]
```
I can't remember if the role existed already as part of AWS, but the ecsTaskExecutionRole Role has this policy assigned to it (in addition to the inline permission, that gives it permission to read GOOGLE_JAVASCIPT_MAP_KEY)
```
    AmazonECSTaskExecutionRolePolicy
```

The Service, Task, and Cluster names can remain the same.  But if you update the default values in the file, CloudFormation will fill the form fields for you, and it will always be the same, unless you choose to change them.  But the values for these items, depend on your VPC and your Security groups.
You can go find VPC, and find the VPC id.  Each VPC should have at least 1 subnet.  copy the subnet id's.  SecurityGroups can be found in EC2, under Security Groups.  Find a Security Group that allows port 80 access, and if it doesn't exist, then create one.  Copy it's id.

after changing the defaults, paste the edited contents of the file into cloudformation.

and it will ask if you want to change the defaults.  You probably don't if you just updateed them, but if you are reusing an existing one, you may have updated values.

After you finish the steps, it will show the stack specified in the configuration is being created, and The container service should be created after a few minutes.

You can find the public IP address by going to ECS > finding the cluster, then service, then task and look in networking bindings tab.

Copy and paste into your browser to trial

to undo (b/c cloudformation created the ECS service, which has daily cost), just remove the Cloudformation stack.  That's it.  It will remove all the components it installed.


## If you want to run carpool in a Free Tier, you can create a free tier VM in EC2.

Free tier is t2.micro or t3.micro.  Run Amazon Linux.

You can run it anyway you want, in the VM.  You just need to follow the instructions for logging into the VM (ssh as ec2-user using a certificate)
  Run it as python, by installing python, then following the instructions for running python source code
  Run it as docker container, by 
    1. running the Docker instructions, to build image, and run that image.  Cut and paste the testdata in console to build some test data to play with application
    2. Pull the already built AWS ECR image, that has testdata already loaded (but the Google API KEY has to be yours, to try this application on your own metal).
```
docker run -it --rm -e GOOGLE_GEOCODE_API_KEY=<google_api> -e GOOGLE_MAP_JS_API_KEY=<google api>  public.ecr.aws/y8w3p2i4/carpoolmashup-with-testdata:latest
```

You also find the public IP address in EC2 instance > Networking tab > public IPv4 address

> [!WARNING]
> EC2 public IP addresses are also temporary.  They likely will change if you stop and start the EC2 instance.  You have to create a Elastic IP, which locks a public IP address for you.  Then assign that IP to your EC2 isntance.


All 3 options I've tested on AWS.

