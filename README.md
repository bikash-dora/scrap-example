# Serverless app for scraping real estate adverts

This application demonstrates the usage of Serverless framework to build a simple application.

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

- create a virtual in the root of the project: `virtualenv venv`
- activate it: `source venv/bin/activate`
- go to `tests` directory
- run the tests by executing `python setup.py test`

## Building, running and deploying

- `sls package` will create the packages but won't deploy them
- `sls deploy` will deploy the application to AWS (will create the stack, will configure the API gateway, will deploy the lambda functions)
- `sls client deploy` will deploy the frontend to a bucket in S3

 