import adverts_controller.lambda_handler as lambda_handler
import moto
import boto3
import simplejson as json
import os
import helper


@moto.mock_dynamodb2
def test_adverts_controller_get_valid_pages():
    helper.set_env({'FILTERED_ADVERTS_TABLE': 'filtered'})
    populate_table(helper.create_table(boto3.resource('dynamodb'), 'filtered', 'title_hash', 'S'))

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
    helper.set_env({'FILTERED_ADVERTS_TABLE': 'filtered'})
    populate_table(helper.create_table(boto3.resource('dynamodb'), 'filtered', 'title_hash', 'S'))
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
