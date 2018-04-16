from multiprocessing.dummy import Pool
from nekretnine_rs_scraper import NekretnineRsScraper
from oglasi_rs_scraper import OglasiRsScraper
import time
import boto3
from os import environ as env
import sys

db = boto3.resource('dynamodb')
table = db.Table('ScrapedAdverts-{}'.format(env['STAGE']))
sys.setrecursionlimit(10000)


def handle(event, context):
    start = time.time()
    print('Scraping started')
    pool = Pool(6)
    res = [pool.apply_async(NekretnineRsScraper().process, [1]), pool.apply_async(OglasiRsScraper().process, [1]),
           pool.apply_async(NekretnineRsScraper().process, [2]), pool.apply_async(OglasiRsScraper().process, [2])]
    pool.close()
    pool.join()
    end = time.time()
    print('Scraping took {} seconds'.format((end - start)))
    start = time.time()
    print('Started to write scraped data to database')
    for async_res in res:
        write_to_db(async_res.get())
    print('Finished writing data to database, operation took {} seconds'.format((time.time() - start)))


def write_to_db(items):
    with table.batch_writer(overwrite_by_pkeys=['title_hash']) as batch:
        for item in items:
            batch.put_item(Item=item)


if __name__ == '__main__':
    handle(None, None)

