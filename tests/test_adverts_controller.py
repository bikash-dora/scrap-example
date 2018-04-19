import adverts_controller.lambda_handler as lambda_handler
import moto
import boto3
import simplejson as json
import os


@moto.mock_dynamodb2
def test_adverts_controller_get_valid_pages():
    setup_env()
    populate_table(create_table(boto3.resource('dynamodb'), 'filtered', 'title_hash', 'S'))

    for i in range(0, 5):
        response = lambda_handler.handle({
            'queryStringParameters': {
                'page': str(i)
            }
        }, None)
        assert response is not None
        response_items = json.loads(response['body'])
        test_response_items = json.load(open('data_files/filtered_adverts_page_{}.json'.format(i), 'r'))
        assert response_items == test_response_items


@moto.mock_dynamodb2
def test_adverts_get_non_existing_page():
    setup_env()
    populate_table(create_table(boto3.resource('dynamodb'), 'filtered', 'title_hash', 'S'))
    response = lambda_handler.handle({'queryStringParameters':{
        'page': '-1'
    }}, None)
    assert response is not None
    assert response['body'] == '{"items": [], "page": -1, "number_of_pages": 5, "count": 112, "page_count": 0}'
    response = lambda_handler.handle({'queryStringParameters':{
        'page': '1000'
    }}, None)
    assert response is not None
    assert response['body'] == '{"items": [], "page": 1000, "number_of_pages": 5, "count": 112, "page_count": 0}'



def populate_table(table):
    for i in range(0, 5):
        items = json.load(open('data_files/filtered_adverts_page_{}.json'.format(i), 'r'))
        for item in items['items']:
            table.put_item(Item=item)


def create_table(db, tablename, pk_name, pk_type):
    table = db.create_table(
        TableName=tablename,
        KeySchema=[
            {
                'AttributeName': pk_name,
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': pk_name,
                'AttributeType': pk_type
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    db.meta.client.get_waiter('table_exists').wait(TableName=tablename)
    return table


def setup_env():
    os.environ['FILTERED_ADVERTS_TABLE'] = 'filtered'
