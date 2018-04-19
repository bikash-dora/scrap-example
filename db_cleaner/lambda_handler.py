import boto3
from boto3.dynamodb.conditions import Attr
from os import environ as env
import time
from datetime import datetime, timedelta
import env_helper


def handle(event, context):
    env_helper.check_env(['SCRAPED_ADVERTS_TABLE'])
    table = boto3.resource('dynamodb').Table(env['SCRAPED_ADVERTS_TABLE'])
    print('Starting to clean the DB')
    age_threshold = int(time.mktime((datetime.today() - timedelta(days=15)).timetuple()))
    print('Fetching records where timestamp is older than {}'.format(age_threshold))
    items = get_older_than(table, age_threshold)
    print('Fetched {} items, deleting them'.format(len(items)))
    delete_items(table, items)


def get_older_than(table, age_threshold):
    items = []
    res = table.scan(Select='ALL_ATTRIBUTES',
                     FilterExpression=Attr('timestamp').lt(age_threshold))
    if 'Items' in res:
        items = res['Items']
    while 'LastEvaluatedKey' in res:
        res = table.scan(ExclusiveStartKey=res['LastEvaluatedKey'],
                         Select='ALL_ATTRIBUTES',
                         FilterExpression=Attr('timestamp').lt(age_threshold))
        items.extend(res['Items'])
    return items


def delete_items(table, items):
    if not items:
        return
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'title_hash': item['title_hash']})

