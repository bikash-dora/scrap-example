import boto3


def handle(event, context):
    if 'db_name' in event:
        table = boto3.resource('dynamodb').Table(event['db_name'])
        res = table.scan()
        items = res['Items']
        while 'LastEvaluatedKey' in res:
            res = table.scan(ExclusiveStartKey=res['LastEvaluatedKey'])
            items.extend(res['Items'])
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'title_hash': item['title_hash']})
    else:
        print('db_name not specified')
