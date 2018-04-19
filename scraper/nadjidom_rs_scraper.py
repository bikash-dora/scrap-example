from decimal import Decimal
from abstract_scraper import AbstractScraper
import time
import datetime
import requests
from bs4 import BeautifulSoup


class NadjiDomRsScraper(AbstractScraper):

    url = 'http://www.nadjidom.com/sr/search?mode=detail&validate=Pretraga&ad_type=1&description=&id_city=2&id_type=&min_price=40000&max_price=70000&street=&min_surface=49&max_surface=100&min_nb_rooms=&max_nb_rooms=&id_ad=&id_hood=118,119,120,121&&date_range=0&offset={PAGE_OFFSET}'

    def get_name(self):
        return 'NadjiDom.rs'

    def fetch_links(self, page_number):
        # self.browser().open(self.url.replace('{PAGE_OFFSET}', str((page_number - 1) * 10)))
        # return [x.find('a')['href'] for x in self.browser().get_current_page().find('div', id='centerContainer-middle').find_all('p', class_='listTitle wordBreak')]
        soup = BeautifulSoup(requests.get(self.url.replace('{PAGE_OFFSET}', str((page_number - 1) * 10))).text, 'lxml')
        return [x.find('a')['href'] for x in soup.find('div', id='centerContainer-middle').find_all('p', class_='listTitle wordBreak')]
        

    def process_link(self, link):
        # self.browser().open(link)
        # page = self.browser().get_current_page()
        page = BeautifulSoup(requests.get(link).text, 'lxml')
        content = page.find('div', id='details')
        images = []
        for x in content.find('div', class_='items').find_all('div', class_='item'):
            images.append(x.find('a')['href'])
        title = ' '.join(content.find('h1', class_='wordBreak').get_text().split())
        location = [' '.join(content.find('div', class_='cityName').get_text().split()),
                    ' '.join(content.find('div', class_='hoodName').get_text().split())]
        price = Decimal(' '.join(content.find('div', id='priceDetails').get_text().split(' ')).replace('.', '')[:-2])
        area = int(' '.join(content.find('div', class_='listSurface').get_text().split()).split(' ')[0].replace('.', '').replace(',', ''))
        text = ''
        for p in content.find('div', class_='inner').find_all('p'):
            text = text + p.get_text() + ' '
        text = ' '.join(text.split())
        if not text:
            text = ' '.join(content.find('h1', class_='wordBreak').get_text().split())
        metadata = []
        property_details = content.find('div', class_='detailsProperties')
        for detail in property_details.find_all('div', class_='parameters three-columns'):
            for m in [x.get_text().split(': ') for x in detail.find_all('div')]:
                value = ' '.join(m[1].split())
                if value:
                    metadata.append('{}={}'.format(m[0], value))
        additional_metadata = ', '.join([x.get_text() for x in property_details.find('div', class_='parameters three-columns ui-widget-content').find_all('label')])
        if additional_metadata:
            metadata.append({'Dodatne informacije={}'.format(' '.join(additional_metadata.split()))})
        contact_details = content.find('div', class_='detailsContact')
        adv_name = ' '.join(contact_details.find('div', class_='contact-name').find('span').get_text().split())
        phones = []
        for x in contact_details.find_all('span', class_='hidden-phone'):
            phone = x['data-original'].replace('/', '').replace('-', '').strip()
            if phone:
                phones.append(phone)
        date_str = content.find('div', class_='date_update').find('span').get_text()
        timestamp = int(time.mktime(datetime.datetime.strptime(' '.join(date_str.split()), '%d/%m/%y').timetuple()))
        if not phones:
            phones = ['nema']
        if not adv_name:
            adv_name = 'nema'

        data = {
            'link': link,
            'title': title,
            'area': area,
            'price': price,
            'text': text,
            'advertiser': {
                'name': adv_name,
                'phones': phones
            },
            'timestamp': timestamp
        }
        if location:
            data['location'] = location
        if metadata:
            data['metadata'] = metadata
        if images:
            data['images'] = images
        return data


