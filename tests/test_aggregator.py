
import aggregator.lambda_handler as lambda_handler
import pytest
import moto
import boto3
import os
import simplejson as json


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
    os.environ['SCRAPED_ADVERTS_TABLE'] = 'scraped'
    os.environ['FILTERED_ADVERTS_TABLE'] = 'filtered'


def test_no_env():
    setup_env()
    del os.environ['SCRAPED_ADVERTS_TABLE']
    del os.environ['FILTERED_ADVERTS_TABLE']
    with pytest.raises(KeyError):
        lambda_handler.handle(None, None)


@moto.mock_dynamodb2
def test_db_not_empty():
    setup_env()
    db = boto3.resource('dynamodb')
    scraped_table = create_table(db, 'scraped', 'title_hash', 'S')
    filterted_table = create_table(db, 'filtered', 'title_hash', 'S')
    test_items = json.load(open('data_files/test_items.json', 'r'))
    for item in test_items['items']:
        item['processed'] = False
        scraped_table.put_item(Item=item)
    lambda_handler.handle(None, None)
    filtered_res = filterted_table.scan()
    assert len(filtered_res['Items']) > 0
    

@moto.mock_dynamodb2
def test_db_empty():
    setup_env()
    db = boto3.resource('dynamodb')
    create_table(db, 'scraped', 'title_hash', 'S')
    filterted_table = create_table(db, 'filtered', 'title_hash', 'S')
    lambda_handler.handle(None, None)
    filtered_res = filterted_table.scan()
    assert len(filtered_res['Items']) == 0
