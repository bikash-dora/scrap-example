from os import environ as env
import boto3
import simplejson as json
import math

table = boto3.resource('dynamodb').Table('FilteredAdverts-{}'.format(env['STAGE']))


def handle(event, context):
    query_params = event['queryStringParameters']
    res = table.scan()
    items = res['Items']
    while 'LastEvaluatedKey' in res:
        res = table.scan(ExclusiveStartKey=res['LastEvaluatedKey'])
        items.extend(res['Items'])
    items.sort(key=get_key, reverse=True)
    page = 0
    page_size = 25
    number_of_pages = len(items) / page_size
    if query_params and query_params.get('page'):
        page = int(query_params['page'])

    start = page * page_size
    end = start + page_size
    if end > len(items):
        end = len(items)
    items_slice = items[start:end]
    return create_response(200, {
        'items': items_slice,
        'page': page,
        'number_of_pages': int(math.ceil(number_of_pages)),
        'count': len(items),
        'page_count': len(items_slice)
    })


def get_key(item):
    return item['timestamp']


def create_response(status_code: int, content: dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token,Accept',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'
        },
        'body': json.dumps(content, use_decimal=True)
    }
