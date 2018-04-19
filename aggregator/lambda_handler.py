from difflib import SequenceMatcher
import serbian_stemmer as stemmer
import boto3
from boto3.dynamodb.conditions import Attr
from os import environ as env
import env_helper


def handle(event, context):
    env_helper.check_env(['FILTERED_ADVERTS_TABLE', 'SCRAPED_ADVERTS_TABLE'])
    dynamo_db = boto3.resource('dynamodb')
    scraped_adverts_table = dynamo_db.Table(env['SCRAPED_ADVERTS_TABLE'])
    filtered_adverts_table = dynamo_db.Table(env['FILTERED_ADVERTS_TABLE'])
    scraped_adverts = scraped_adverts_table.scan(FilterExpression=Attr('processed').eq(False))
    if scraped_adverts and 'Items' in scraped_adverts:
        filtered_items = get_all_filtered(filtered_adverts_table)
        for scraped_advert in scraped_adverts['Items']:
            process_scraped(scraped_advert, filtered_items)
        with filtered_adverts_table.batch_writer(overwrite_by_pkeys=['title_hash']) as batch:
            for item in filtered_items:
                batch.put_item(Item=item)
        with scraped_adverts_table.batch_writer(overwrite_by_pkeys=['title_hash']) as batch:
            for item in scraped_adverts['Items']:
                batch.put_item(Item=item)


def process_scraped(scraped_advert, filtered_adverts):
    scraped_advert['processed'] = True
    for filtered_advert in filtered_adverts:
        if similar(scraped_advert, filtered_advert):
            if scraped_advert['link'] == filtered_advert['link']:
                return
            if 'similar_adverts' not in filtered_advert:
                filtered_advert['similar_adverts'] = []
            add_to_similar = True
            for similar_advert in filtered_advert['similar_adverts']:
                if similar_advert['link'] == filtered_advert['link']:
                    add_to_similar = False
                    break
            if add_to_similar:
                filtered_advert['similar_adverts'].append({
                    'title': filtered_advert['title'],
                    'link': filtered_advert['link']})
            filtered_advert['title'] = scraped_advert['title']
            filtered_advert['link'] = scraped_advert['link']
            filtered_advert['timestamp'] = scraped_advert['timestamp']
            filtered_advert['area'] = scraped_advert['area']
            filtered_advert['price'] = scraped_advert['price']
            filtered_advert['text'] = scraped_advert['text']
            filtered_advert['advertiser'] = scraped_advert['advertiser']
            filtered_advert['metadata'] = scraped_advert['metadata']
            filtered_advert['images'] = scraped_advert['images']
            return
    filtered_adverts.append(scraped_advert)


def get_all_filtered(filtered_adverts_table):
    items = []
    res = filtered_adverts_table.scan()
    if 'Items' in res:
        items = res['Items']
        while 'LastEvaluatedKey' in res:
            res = filtered_adverts_table.scan(ExclusiveStartKey=res['LastEvaluatedKey'])
            items.extend(res['Items'])
    return items


def similar(a, b):
    if a['location'] == b['location'] and a['area'] == b['area'] and a['price'] == b['price']:
        print('{} is similar to {}, the location, area and price matches'.format(a['link'], b['link']))
        return True
    ratio = SequenceMatcher(None,
                            stemmer.stem_str(a['text'].replace('.', '').replace(',', '').replace('!', '')).strip(),
                            stemmer.stem_str(
                                b['text'].replace('.', '').replace(',', '').replace('!', '')).strip()).ratio()
    if (0 <= abs(a['area'] - b['area']) < 5) and ratio >= 0.75:
        print('{} is similar to {}, area delta {}, similarity {}'.format(a['link'], b['link'],
                                                                         (abs(a['area'] - b['area'])), ratio))
        return True
    return False
