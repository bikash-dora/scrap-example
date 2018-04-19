
import aggregator.lambda_handler as lambda_handler
import pytest
import moto
import boto3
import os
import simplejson as json
import helper


def test_no_env():
    helper.unset_env(['SCRAPED_ADVERTS_TABLE','FILTERED_ADVERTS_TABLE'])
    with pytest.raises(KeyError):
        lambda_handler.handle(None, None)


@moto.mock_dynamodb2
def test_db_not_empty():
    helper.set_env({
        'SCRAPED_ADVERTS_TABLE': 'scraped',
        'FILTERED_ADVERTS_TABLE': 'filtered'
    })
    db = boto3.resource('dynamodb')
    scraped_table = helper.create_table(db, 'scraped', 'title_hash', 'S')
    filterted_table = helper.create_table(db, 'filtered', 'title_hash', 'S')
    test_items = json.load(open('data_files/test_items.json', 'r'))
    for item in test_items['items']:
        item['processed'] = False
        scraped_table.put_item(Item=item)
    lambda_handler.handle(None, None)
    filtered_res = filterted_table.scan()
    assert len(filtered_res['Items']) > 0
    

@moto.mock_dynamodb2
def test_db_empty():
    helper.set_env({
        'SCRAPED_ADVERTS_TABLE': 'scraped',
        'FILTERED_ADVERTS_TABLE': 'filtered'
    })
    db = boto3.resource('dynamodb')
    helper.create_table(db, 'scraped', 'title_hash', 'S')
    filterted_table = helper.create_table(db, 'filtered', 'title_hash', 'S')
    lambda_handler.handle(None, None)
    filtered_res = filterted_table.scan()
    assert len(filtered_res['Items']) == 0
