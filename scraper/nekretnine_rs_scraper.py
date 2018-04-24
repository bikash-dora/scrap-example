from abstract_scraper import AbstractScraper
from decimal import Decimal
import time
import datetime
from bs4 import BeautifulSoup
import requests


class NekretnineRsScraper(AbstractScraper):

    url = 'https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/zemlja/srbija/grad/novi-sad/deo-grada/liman-1_liman-2_liman-3_liman-4/kvadratura/50_0/cena/40000_70000/poredjaj-po/datumu_nanize/lista/po_stranici/50/stranica/{PAGE_NUMBER}'

    def get_name(self):
        return 'Nekretnine.rs'

    def fetch_links(self, page_number):
        soup = BeautifulSoup(requests.get(self.url.replace('{PAGE_NUMBER}', str(page_number))).text, 'lxml')
        return [entry.find('a')['href'] for entry in soup.find_all('h2', class_='marginB_5')]
        

    def process_link(self, link):
        page = BeautifulSoup(requests.get(link).text, 'lxml')
        content = page.find('div', {'id': 'singleContent'})
        # extract title, location, size and price
        title = content.find('h1', {'itemprop': 'itemreviewed'}).string
        header_data = content.find('div', {'id': 'social'})
        location = (header_data.find('h2').string.split(', ')[1:])[1:]
        area_and_price = header_data.find('h3').string.split(', ')
        area = int(area_and_price[0].split(' ')[0])
        price = Decimal(area_and_price[1].split(' ')[0].replace('.', '').replace(',', '.'))
        # extract advertisement text
        text = ' '.join(content.find('div', class_='sRightGrid fixed').find('p').get_text().split())
        # extract metadata
        metadata = []
        timestamp = 0
        for li in content.find('div', class_='sLeftGrid fixed').find('ul').find_all('li'):
            key = li.find('div', class_='singleLabel').string.strip()[:-1]
            value = li.find('div', class_='singleData').string
            if value:
                k = ' '.join(key.split())
                if 'Ažuriran' in k:
                    timestamp = int(time.mktime(datetime.datetime.strptime(' '.join(value.split()), '%d.%m.%Y.').timetuple()))
                    continue
                metadata.append('{}={}'.format(k, ' '.join(value.split())))
        # extract advertiser
        adv_name = ''
        for contact_line in content.find('div', class_='fixed sContactWrap').find_all('div', class_='sContactRow short'):
            adv_name = '{} {}'.format(adv_name, ' '.join(contact_line.get_text().replace('Srbija', '').split()))
        phones = []
        for phone in content.find_all('span', class_='phone_orig'):
            for p in phone.string.strip().split(', '):
                phones.append(p.replace('/', '').replace('-', ''))
        # extract image data
        images = []
        try:
            for img in content.find('div', {'id': 'images'}).find_all('img'):
                images.append('https://www.nekretnine.rs{}'.format(img['src']))
        except Exception as e:
            print('No image for {}'.format(link))
        if not phones:
            phones = ['nema']
        data = {
            'link': link,
            'title': title,
            'location': location,
            'area': area,
            'price': price,
            'text': text,
            'metadata': metadata,
            'advertiser': {
                'name': adv_name,
                'phones': phones
            },
            'timestamp': timestamp
        }
        if images:
            data['images'] = images
        return data
