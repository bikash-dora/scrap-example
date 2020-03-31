# Serverless app for scraping real estate adverts
#Testing

This application demonstrates the usage of Serverless framework to build a simple application. More detailed info about the application can found [here](https://gitlab.codecentric.de/jozef.jung/sls-basics/blob/master/blogpost.md).

## Prerequisites

Before you can try the application, you need the following installed:

- Python 3.6
- [Node and npm](https://nodejs.org/en/)
- [Docker](https://www.docker.com/community-edition)
- [Serverless framework](https://serverless.com/framework/)
- [AWS account](https://aws.amazon.com/free/)

## Configuration

Follow the serverless setup guide [here](https://serverless.com/framework/docs/providers/aws/guide/quick-start#pre-requisites).

Install the following plugins:

- `sls plugin install -n serverless-python-requirements`
- `sls plugin install -n serverless-finch`

## Running the tests

Tests are using [pytest](https://docs.pytest.org/en/latest/) framework.

In order to execute the tests, do the following steps:

- create a virtual in the root of the project: `virtualenv venv`
- activate it: `source venv/bin/activate`
- go to `tests` directory
- run the tests by executing `python setup.py test`. This should download and install the dependencies which are required for testing and should run the tests.

## Building, running and deploying

- `sls package` will create the packages but won't deploy them
- `sls deploy` will deploy the application to AWS (will create the stack, will configure the API gateway, will deploy the lambda functions)
- `sls client deploy` will deploy the frontend to a bucket in S3

## `serverless.yml`

The `serverless.yml` is the central part of the application.

The `provider` part configures the cloud provider, which is AWS in our case. It defines the runtime, region and other common values which are applied to every function. These values are `memorySize`, `timeout` and `iamRoleStatements`. IAM role statements are used to grant or deny actions for certain resources. In this case every resource is allowed to execute any operation on DynamoDB (this approach is the fastest way to set up and test the project, but it allows everything - to overcome this, by default everything should be forbidden IAM role statements should be defined for every resource separately).

 ```yaml
service: sls-basics

provider:
  name: aws
  runtime: python3.6
  stage: ${opt:stage, 'dev'}
  region: eu-central-1
  memorySize: 128
  timeout: 300
  iamRoleStatements:
    - Effect: "Allow"
      Action:
        - "dynamoDB:*"
      Resource: "*"
 ```

The `package` part defines how the function should be packed. `individually` means that every function is packed separately. The default value is `false`. With `exclude` you can specify what should be excluded from the package.

```yaml
package:
  individually: true
  exclude:
    - "**/.eggs/**"
    - "**/.pytest_cache/**"
    - "**/*.egg-info/**"
    - "**/tests/**"
    - "**/__pycache__/**"
    - "**/*.iml"
    - "**/setup.py"
    - "**/test_*.py"
    - "**/*_test.py"
```

The `functions` part defines the lambda functions. The functions are defined by the names you give them (e.g.: `scraper`).

Under every function is the configuration for the given function. `handler` specifies the method which is called when the function is invoked. The global configuration values can be overridden in the functions, like the `memorySize`. The first function needs more memory since scraping is more memory intensive task. The environment variables which are going to be available for the function are defined in `environment`.

The `event` defines what invokes the function. In this case there are several cron events and one http event. The same function can be invoked by several different events.

```yaml
functions:
  scraper:
    handler: lambda_handler.handle
    module: scraper
    memorySize: 512
    environment:
      SCRAPED_ADVERTS_TABLE: ScrapedAdverts-${opt:stage, self:provider.stage}
    events:
      - schedule: cron(0 6,12,18 * * ? *)
    vendor: ./utils # workaround for including common libs, since package.include has a bug and not working when package.individually is set to true
  adverts_controller:
    handler: lambda_handler.handle
    module: adverts_controller
    environment:
      FILTERED_ADVERTS_TABLE: FilteredAdverts-${opt:stage, self:provider.stage}
    events:
      - http:
          path: adverts/get
          method: get
    vendor: ./utils
  db_cleaner:
    handler: lambda_handler.handle
    module: db_cleaner
    environment:
      SCRAPED_ADVERTS_TABLE: ScrapedAdverts-${opt:stage, self:provider.stage}
    events:
      - schedule: cron(0 3 * * ? *)
    vendor: ./utils
  aggregator:
    handler: lambda_handler.handle
    module: aggregator
    environment:
      SCRAPED_ADVERTS_TABLE: ScrapedAdverts-${opt:stage, self:provider.stage}
      FILTERED_ADVERTS_TABLE: FilteredAdverts-${opt:stage, self:provider.stage}
    events:
      - schedule: cron(0/30 6-8,12-14,18-20 * * ? *)
    vendor: ./utils
```

The `custom` part contains the configuration for the plugins.

```yaml
custom:
  pythonRequirements:
    dockerizePip: true
  client:
    bucketName: adverts-website-bucket
    distributionFolder: client/dist
    indexDocument: index.html
    errorDocument: error.html
```

The `resources` part defines the resources which should be created when the application is deployed. The resources part must use [CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html) syntax. The snippet below creates two tables in DynamoDB.

```yaml
resources:
  Resources:
    advertisementsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ScrapedAdverts-${opt:stage, self:provider.stage}
        AttributeDefinitions:
          - AttributeName: title_hash
            AttributeType: S
        KeySchema:
          - AttributeName: title_hash
            KeyType: HASH
        ProvisionedThroughput:
          ReadCapacityUnits: 5
          WriteCapacityUnits: 5
    filteredAdvertisementsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: FilteredAdverts-${opt:stage, self:provider.stage}
        AttributeDefinitions:
          - AttributeName: title_hash
            AttributeType: S
        KeySchema:
          - AttributeName: title_hash
            KeyType: HASH
        ProvisionedThroughput:
          ReadCapacityUnits: 5
          WriteCapacityUnits: 5
```

The plugin section defines the used plugins by the serverless framework. `serverless-python-requirements` plugin downloads the dependencies for every function based on `requirements.txt` and bundles them with the function. `serverless-finch` is used to deploy the frontend.

```yaml
plugins:
  - serverless-python-requirements
  - serverless-finch
```
