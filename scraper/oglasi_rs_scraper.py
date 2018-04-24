from abstract_scraper import AbstractScraper
from decimal import Decimal
import time
import datetime
import requests
from bs4 import BeautifulSoup

class OglasiRsScraper(AbstractScraper):

    url = 'https://www.oglasi.rs/oglasi/nekretnine/prodaja/stanova/grad/novi-sad/deo/liman+liman-1+liman-2+liman-3+liman-4?p={PAGE_NUMBER}&i=48&s=d&pr%5Bs%5D=40000&pr%5Be%5D=70000&pr%5Bc%5D=EUR&d%5BKvadratura%5D%5B0%5D=50&d%5BKvadratura%5D%5B1%5D=60&d%5BKvadratura%5D%5B2%5D=70'

    def get_name(self):
        return 'Oglasi.rs'

    def fetch_links(self, page_number):
        soup = BeautifulSoup(requests.get(self.url.replace('{PAGE_NUMBER}', str(page_number))).text, 'lxml')
        return ['https://www.oglasi.rs{}'.format(a['href']) for a in soup.find_all('a', class_='fpogl-list-title')]


    def process_link(self, link):
        page = BeautifulSoup(requests.get(link).text, 'lxml')
        content = page.find('div', id='content')
        timestamp = int(time.mktime(datetime.datetime.strptime(' '.join(content.find('time').get_text().split()), '%d.%m.%Y. %H:%M:%S').timetuple()))

        title = content.find('h1').string
        price = Decimal(content.find('span', {'itemprop': 'price'})['content'])
        location = []
        # get the location and area, metadata
        area = 0
        metadata = []
        table = content.find('table')
        for row in table.find_all('tr'):
            row_contents = row.get_text().split(':')
            row_contents[0] = ' '.join(row_contents[0].split())
            row_contents[1] = ' '.join(row_contents[1].split())
            if row_contents[0] == 'Lokacija' or row_contents[0] == 'Ulica i broj':
                loc = row_contents[1].replace(' (Srbija, Novi Sad, Novi Sad)', '').strip()
                if loc:
                    location.append(loc)
                continue
            if row_contents[0] == 'Kvadratura':
                area = int(row_contents[1][:2])
                continue
            if row_contents[1]:
                metadata.append('{}={}'.format(' '.join(row_contents[0].split()), ' '.join(row_contents[1].split())))

        additional_info = ' '.join(content.find('p').get_text().split())
        if additional_info:
            metadata.append('Dodatne informacije={}'.format(additional_info))
        # extract the advertiser
        adv_info = []
        for div in page.find('aside', {'id': 'right-bar'}).find('div', class_='panel-body').find_all('div'):
            if div.string:
                adv_info.append(div.string.strip())
        adv_name = adv_info[0]
        phones = adv_info[1:]
        # extract text
        text = ' '.join(content.find('div', {'itemprop': 'description'}).get_text().split()).strip()

        # extract images
        try:
            images = ['https://www.oglasi.rs{}'.format(img['src']) for img in content.find('figure', {'data-advert-image-gallery': ''}).find_all('img')]
        except Exception as e:
            images = []
            print('No image found for {}'.format(link))
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
