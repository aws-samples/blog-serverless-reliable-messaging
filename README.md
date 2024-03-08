<!--
MIT No Attribution

Copyright 2023 Amazon.com, Inc. or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.-->

# Building a Serverless Pipeline to Deliver Reliable Messaging

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
- [Requirements](#requirements)
- [Organization](#organization)
- [Configuration](#configuration)
- [Message Formats](#message-formats)
- [Building and Publishing](#building-and-publishing)
- [License](#license)

</details>

## About

Please see the blog post [here](https://aws.amazon.com/blogs/compute/building-a-serverless-streaming-pipeline-to-deliver-reliable-messaging/) for more information.

The architecture is designed for maximizing audit record ingestion performance.  This system operates between the limit of most messaging systems (256Kb to 1Mb) and the limit for Lambda functions (6Mb). The primary source of latency is the time it takes for an audit record to be transmitted across the network. An AWS Lambda function to receive the message and an Amazon ElastiCache for Redis cluster provides initial blocking persistence layer write that provides better performance than S3. Once the data is persisted in ElastiCache, the AWS Step Functions workflow then manages the orchestration of the communication and persistence functions. The architecture diagram below models the flow of the audit record through the system.

![Architecture diagram](./media/architecture.png)

---

## Requirements

* **AWS Command Line Interface:** ([link](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html))
* **AWS Serverless Application Model:** ([link](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html))The deployment scripts have been created with AWS Cloud Development Kit (AWS CDK) v2 [Link](https://docs.aws.amazon.com/cdk/v2/guide/home.html).  The python version of the CDK has been used
* **Python:** Python 3.10 was used during the development and deployment of the solution

_Note: This solution has been developed and tested on Windows and Amazon Linux 2_

---

## Organization

**Folder structure:**
``` bash
├── infra
├── internal-json
├── media
├── src
|   ├── commonLayer 
|   ├── finalStateAggregate 
|   ├── ingestFailure
|   ├── ingestMessage
|   ├── messageArchive
│   └── messageMetaData
├── statemachine
├── test_client
├── template.yaml
└── test_message.json
```

* ```infra``` SAM templates for VPC and Redis stack creation
* ```internal-json``` Examples of internal message payloads
* ```media``` Architecture diagram
* ```src``` Code to support Lambda functions
    * ```commonLayer``` Universal constants, exception handler, and JSON template loader code with necessary universal Python libraries
    * ```finalStateAggregate``` Builds final message to be sent to subscribers
    * ```ingestFailure``` If the initial ingestion Lambda fails, this Lambda salvages the raw message and writes it to a S3 bucket
    * ```ingestMessage``` Main lambda process that receives the message from the client (via the API gateway), writes the payload to Redis, and initiates the Step Function
    * ```messageArchive``` Stores the message payload in S3 from Redis
    * ```messageMetaData``` Stores the meta data about the message in DynamoDB
* ```statemachine``` Contains the JSON definition of the State Machine
* ```test_client``` Code and sample payload to exercise the API gateway and test the stack
* ```template.yaml``` Primary SAM definition that will create the stack

---

## Message Formats

### Incoming message format:
The incoming message requires three types of data:
* Message payload: treated as a block of data that does not require parsing, usually represented as Base64 data, but may be any JSON compatible format.
* Message metadata: Defined by the use case. A minimally suggested metadata contains source system identification, message type, and time/date stamps. In the walkthrough below, the original timestamp from the message producer is used as the timestamp for internal messages.
*	Security Context: When the message producer authenticates and posts to the API Gateway endpoint, you can query the security context to get metadata about the source of the payload. This context includes security principles, receipt information, timestamp, environmental information (source IP and headers) and a message payload checksum.  This context is stored in the DynamoDB metadata record and is queried from there by downstream systems.

### Internal message format:
The internal message contains data about the storage context and data for the Step Functions workflow to route the message.
* Message ID: generated by the ingest Lambda function.
* Message Metadata: contains system information plus metadata copied from the incoming message.
* Security Context: security context copied from the incoming message.
* Storage Context.
    * ElastiCache for Redis reference information, e.g., cluster address and key.
    * Amazon S3 reference information, e.g., bucket and key.
    * Persistence flags, true or false that shows if the data has or has not been persisted.
    * DynamoDB Metadata persistence reference information, e.g. table and key.

### Notification message format:
Information sent to downstream subscribers about messages received by the system.
* Message ID: generated by the ingest Lambda function.
* Message Metadata: repeated from incoming message.
* State information:
    * Message Persisted in Amazon S3: True/False.
    * Metadata Persisted in DynamoDB: True/False.
* Data storage information:
    * ElastiCache for Redis reference, e.g., cluster address and key.
    * Amazon S3 reference information, e.g., bucket and key.
    * DynamoDB Metadata persistence reference information, e.g. table and key.


---

## Building and Publishing

__Prerequisites__

* An Amazon account to deploy the stack into
* Credentials with AWS Region configured with permissions necessary to run SAM script (see [AWS CLI documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html))

__The following commands will build and deploy the stack__

``` bash
cd <project directory>

sam build
sam deploy --guided
```

These are the parameters that are required:

1.	Stack Name: Name given to this deployment (example: serverless-messaging)
1.	AWS Region: Where to deploy (example: us-east-1)
1.	ElasticacheInstanceClass: EC2 cache instance type to use with (example: cache.t3.small)
1.	ElasticReplicaCount: How many replicas should be used with ElastiCache (recommended minimum: 2)
1.	ProjectName: Used for naming resources in account (example: serverless-messaging)
1.	MultiAZ: True/False if multiple Availability Zones will be used (recommend: True)
1.	The default parameters can be selected for the remainder of questions

---

## Configuration

The SAM script will ask for the following configuration items:

* __ElasticacheInstanceClass__ What EC2 instance type to use with AWS ElastiCache Redis cluster.  Recommend ```cache.t3.small``` for low volume testing
* __ElasticReplicaCount__ How many instances/replicas of the ElastiCache to create.  Recommend ```2```
* __ProjectName__ Name to use with VPC naming. _No recommendation_
* __MultiAZ__ Configure Redis to use MultiAZ deployment configuration.  Recommend ```true```

---

## License

MIT No Attribution

Copyright 2023 Amazon.com, Inc. or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.