# Hello ~~world~~ **real estate advertisements**

A simple application written in Python using the [*serverless*](https://serverless.com/) framework to implement a real world scenario.

## Background story

I am looking for flat to buy. Since there are lots of recurring adverts on different ad websites, and the same flats are advertised multiple times to be always on the first page of results, I thought it would be an interesting idea to write an application which scrapes the advertisements from different sites and compares them. The main goal is to make a unique list of advertisements which is browseable.

In the past couple of months I am working with serverless technologies and I came up with the idea to implement this application as a serverless application, document it and share it.

The application is simple enough to understand, yet not a typical hello word application.

## Concept of serverless

In a nutshell, serverless means that you do not have to think about the servers. Just write the code which executes the business logic. The provider takes care of the rest (spinning up a container, initialization of the execution environment, code execution, scaling, etc.)

This enables fast project setup and efficient development.

## Application architecture

The architecture of the application is on the picture below.
![architecture](https://www.lucidchart.com/publicSegments/view/502202a0-b654-4728-a58d-47bfd646982b/image.png)

The architecture consists of the following functions:

- `scraper` - scrapes the advertisements from three different sites for advertising. It extracts the data from the ads, formats the data and puts the data into `ScrapedAdverts` DynamoDB table. This is a scheduled lambda which is executed 3 time per day.
- `aggregator` - reads the data from `ScrapedAdverts` table and processes them. Checks if the given advertisement exists in `FilteredAdverts` table by performing a similarity check. If the advertisement exists, it is going to be updated. If it does not exists, the data is going to be inserted. This lambda is also scheduled and runs several times per day. It processes only a chunk of data from `ScrapedAdverts` (the amount of data which is returned in one scan by DynamoDB)
- `adverts_controller` - acts as request handler for the API Gateway. It is mapped to `GET adverts/get?page=` call.
- `db_cleaner` - is executed once per day and cleans the `ScrapedAdverts` table. It deletes the entires which are older than 15 days.

The frontend is hosted in a public S3 bucket and can be reached [here](http://adverts-website-bucket.s3-website.eu-central-1.amazonaws.com/). It fetches the advertisements through API Gateway from `adverts_controller`.

## Project structure

Every function is in its own directory, and every function has its own requirements (`requirements.txt`).

The exceptions are the following directories:

- `tests` - contains the unit tests.
- `utils` - contains common helper functions. The content of this directory in included in every packed function.
- `client/dist` - contains the frontend code (HTML and JS).

### serverless.yml

The main entry point of the project is the `serverless.yml` file. This file tells to serverless framework what do deploy and how. Let's go through this file.

The `provider` part configures the cloud provider, which is AWS in our case. It defines the runtime, region and other common values which are applied to every function. These values are `memorySize`, `timeout` and `iamRoleStatements`. IAM role statements are used to grand or deny actions for certain resources. In this case every resource is allowed to execute any operation on DynamoDB (this approach is the fastest way to set up and test the project, but it allows everything - to overcome this, by default everything should be forbidden IAM role statements should be defined for every resource separately).

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

### The code

On AWS lambda, when using Python, the function which are used for handling the invocation should have the following signature:

```python
def handler(event, context):
    pass
```

- `event` holds the data which is passed to function, e.g.: if the handler handles http events, the the request body, the query parameters, path parameters, etc. are passed in the event object.
- `context` is injected by the AWS lambda runtime, and it can be used to gather information and interact with the runtime. More info on this can be found [here](https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html).

[Boto3](http://boto3.readthedocs.io/en/latest/) library is the de-facto standard in Python to interact with the AWS services. It is available in the AWS Python runtime.

### The unit tests

So far, so good, it's simple and easy to write functions. But what about the testing? Testing a lambda function by deploying it and invoking, and then watching the logs is a bad idea.

Writing unit tests is a crucial step in writing better code. Fortunately the lambda functions are easily testable. [Moto](http://docs.getmoto.org/en/latest/) is a powerful library for testing lambda function. It mocks AWS services like DynamoDB and the mocked service behaves like the real service.

Tests are using [pytest](https://docs.pytest.org/en/latest/) framework.

In order to execute the tests, you have to set up a python virtualenv, then go to the `tests` directory and invoke `python setup.py test`. This should download and install the dependencies which are required for testing and should run the tests.

## Notes

Please check out the project's [readme file](https://gitlab.codecentric.de/jozef.jung/sls-basics/blob/master/README.md). It contains the steps how to set up the application, how to run the tests anf how to deploy it.

## Conclusion

We've seen that implementing a simple application is easy with the help of serverless framework and AWS stack.

There are several things which can be added/improved:

- security: deny all permissions and allow some on function level
- ability to manage ads: add an authenticated user which can manage the scraped adverts
- make the scraper configurable