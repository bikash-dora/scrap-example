import os

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


def set_env(kvpairs: dict):
    for k, v in kvpairs.items():
        os.environ[k]=v


def unset_env(keys: list):
    for k in keys:
        if k in os.environ:
            del os.environ[k]