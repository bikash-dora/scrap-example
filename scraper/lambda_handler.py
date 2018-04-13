from multiprocessing.dummy import Pool
from nekretnine_rs_scraper import NekretnineRsScraper
from oglasi_rs_scraper import OglasiRsScraper
import time
import boto3
from os import environ as env
from difflib import SequenceMatcher
import serbian_stemmer as stemmer
import logging
import sys
import simplejson as json

db = boto3.resource('dynamodb')
table = db.Table('adverts-{}'.format(env['STAGE']))
sys.setrecursionlimit(10000)
log = logging.getLogger('lambda_handler')


def handle(event, context):
    start = time.time()
    pool = Pool(6)
    res = [pool.apply_async(NekretnineRsScraper().process, [1]), pool.apply_async(OglasiRsScraper().process, [1]),
           pool.apply_async(NekretnineRsScraper().process, [2]), pool.apply_async(OglasiRsScraper().process, [2])]
    pool.close()
    pool.join()
    end = time.time()
    print('Processing took {} seconds'.format((end - start)))
    print('Combining results started')
    start = time.time()
    unique_results = []
    for async_res in res:
        for data in async_res.get():
            if not has_similar(data, unique_results):
                unique_results.append(data)
    end = time.time()
    print('Combining results finished - combination took {} seconds'.format((end - start)))
    print('Number of unique results {}'.format(len(unique_results)))
    # print(json.dumps(unique_results, indent=2, use_decimal=True))
    write_to_db(unique_results)


def write_to_db(items):
    with table.batch_writer(overwrite_by_pkeys=['title_hash']) as batch:
        for item in items:
            batch.put_item(Item=item)


def has_similar(data, entries):
    for entry in entries:
        if similar(data, entry):
            return True
    return False


def similar(a, b):
    is_similar = False
    if a['location'] == b['location'] and a['area'] == b['area'] and a['price'] == b['price']:
        is_similar = True
    ratio = SequenceMatcher(None, stemmer.stem_str(a['text'].replace('.', '').replace(',', '').replace('!', '')).strip(),
                            stemmer.stem_str(b['text'].replace('.', '').replace(',', '').replace('!', '')).strip()).ratio()
    if (0 <= abs(a['area'] - b['area']) < 5) and ratio >= 0.75:
        log.info('{} is similar to {}, area delta {}, similarity {}'.format(a['link'], b['link'], (abs(a['area'] - b['area'])), ratio))
        is_similar = True
    if is_similar:
        if not b.get('similar_adverts'):
            b['similar_adverts'] = []
        b['similar_adverts'].append({'title': a['title'], 'link': a['link']})
        log.info('{} is similar to {}'.format(a['link'], b['link']))
    return is_similar


if __name__ == '__main__':
    handle(None, None)

