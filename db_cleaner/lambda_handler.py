import boto3
from boto3.dynamodb.conditions import Attr
from os import environ as env
import time
from datetime import datetime, timedelta


class DynamoDBHandler:
    def __init__(self, table_name):
        self._table_name = table_name
        self._resource = None
        self._table = None

    def resource(self):
        if not self._resource:
            self._resource = boto3.resource('dynamodb')
        return self._resource

    def table(self):
        if not self._table:
            self._table = self.resource().Table(self._table_name)
        return self._table


db_handler = DynamoDBHandler('adverts-{}'.format(env['STAGE']))


def handle(event, context):
    print('Starting to clean the DB')
    age_threshold = int(time.mktime((datetime.today() - timedelta(days=15)).timetuple()))
    print('Fetching records where timestamp is older than {}'.format(age_threshold))
    items = get_older_than(age_threshold)
    print('Fetched {} items, deleting them'.format(len(items)))
    delete_items(items)


def get_older_than(age_threshold):
    items = []
    res = db_handler.table().scan(Select='ALL_ATTRIBUTES',
                                  FilterExpression=Attr('timestamp').lt(age_threshold))
    if 'Items' in res:
        items = res['Items']
    while 'LastEvaluatedKey' in res:
        res = db_handler.table().scan(ExclusiveStartKey=res['LastEvaluatedKey'],
                                      Select='ALL_ATTRIBUTES',
                                      FilterExpression=Attr('timestamp').lt(age_threshold))
        items.extend(res['Items'])
    return items


def delete_items(items):
    if not items:
        return
    with db_handler.table().batch_writer() as batch:
        for item in items:
            batch.delete_item(Item=item)

