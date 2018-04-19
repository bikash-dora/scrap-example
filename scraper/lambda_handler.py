from multiprocessing.dummy import Pool
from nekretnine_rs_scraper import NekretnineRsScraper
from oglasi_rs_scraper import OglasiRsScraper
from nadjidom_rs_scraper import NadjiDomRsScraper
import time
import boto3
from os import environ as env
import sys
import env_helper

sys.setrecursionlimit(10000)


def handle(event, context):
    env_helper.check_env(['SCRAPED_ADVERTS_TABLE'])
    table = boto3.resource('dynamodb').Table(env['SCRAPED_ADVERTS_TABLE'])
    start = time.time()
    print('Scraping started')
    pool = Pool(10)
    res = [pool.apply_async(NekretnineRsScraper().process, [1]),
           pool.apply_async(NekretnineRsScraper().process, [2]),
           pool.apply_async(OglasiRsScraper().process, [1]),
           pool.apply_async(OglasiRsScraper().process, [2]),
           pool.apply_async(NadjiDomRsScraper().process, [1]),
           pool.apply_async(NadjiDomRsScraper().process, [2]),
           pool.apply_async(NadjiDomRsScraper().process, [3]),
           pool.apply_async(NadjiDomRsScraper().process, [4]),
           pool.apply_async(NadjiDomRsScraper().process, [5]),
           pool.apply_async(NadjiDomRsScraper().process, [6])]
    pool.close()
    pool.join()
    end = time.time()
    print('Scraping took {} seconds'.format((end - start)))
    start = time.time()
    print('Started to write scraped data to database')
    for async_res in res:
        write_to_db(table, async_res.get())
    print('Finished writing data to database, operation took {} seconds'.format((time.time() - start)))


def write_to_db(table, items):
    with table.batch_writer(overwrite_by_pkeys=['title_hash']) as batch:
        for item in items:
            batch.put_item(Item=item)
