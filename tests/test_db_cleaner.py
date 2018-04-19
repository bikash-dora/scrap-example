import db_cleaner.lambda_handler as lambda_handler
import moto
import boto3
import os
import simplejson as json
import time
import helper


@moto.mock_dynamodb2
def test_db_cleaner_nothing_to_clear():
    helper.set_env({'SCRAPED_ADVERTS_TABLE': 'scraped'})
    db = boto3.resource('dynamodb')
    table = helper.create_table(db, 'scraped', 'title_hash', 'S')
    current_time = int(time.time())
    populate_table(table, current_time, current_time)
    lambda_handler.handle(None, None)
    items = table.scan()
    assert len(items['Items']) == 112


@moto.mock_dynamodb2
def test_db_cleaner_some_to_clear():
    helper.set_env({'SCRAPED_ADVERTS_TABLE': 'scraped'})
    db = boto3.resource('dynamodb')
    table = helper.create_table(db, 'scraped', 'title_hash', 'S')
    current_time = int(time.time())
    populate_table(table, current_time, current_time - (16 * 24 * 60 * 60))
    lambda_handler.handle(None, None)
    items = table.scan()
    assert len(items['Items']) == 62


@moto.mock_dynamodb2
def test_db_cleaner_all_to_clear():
    helper.set_env({'SCRAPED_ADVERTS_TABLE': 'scraped'})
    db = boto3.resource('dynamodb')
    table = helper.create_table(db, 'scraped', 'title_hash', 'S')
    current_time = int(time.time()) - (16 * 24 * 60 * 60)
    populate_table(table, current_time, current_time)
    lambda_handler.handle(None, None)
    items = table.scan()
    assert len(items['Items']) == 0


def populate_table(table, timestamp1, timestamp2):
    for i in range(0, 5):
        items = json.load(open('data_files/filtered_adverts_page_{}.json'.format(i), 'r'))
        for item in items['items']:
            item['timestamp'] = timestamp1 if i % 2 == 0 else timestamp2
            table.put_item(Item=item)
