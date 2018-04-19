from scraper.nadjidom_rs_scraper import NadjiDomRsScraper
import requests_mock
from decimal import Decimal


def test_nadjidom_scraper_fetch_links():
    scraper = NadjiDomRsScraper()
    with requests_mock.mock() as mock:
        mock.get(scraper.url.replace('{PAGE_OFFSET}', '0'), text=open('data_files/nadjidom_rs_adverts.html', 'r').read())
        links = scraper.fetch_links(1)
        assert len(links) == 10

def test_nadjidom_scraper_process_link():
    scraper = NadjiDomRsScraper()
    with requests_mock.mock() as mock:
        mock.get('http://nadjidom.rs/stan/1', text=open('data_files/nadjidom_rs_advert.html').read())
        data = scraper.process_link('http://nadjidom.rs/stan/1')
        assert data == {
            'link': 'http://nadjidom.rs/stan/1',
            'title': 'Odlican trosoban stan, u blizini Somborskog Bulevara 0612446466',
            'area': 63860,
            'price': Decimal('63680'),
            'text': 'Kontakt: 0612446466 Dalibor',
            'advertiser': {
                'name':'ĐORĐEVIĆ Nekretnine',
                'phones': ['0216611000', '021426010', '021426800', '0658118018', '064 649 88 66']
            },
            'timestamp': 1524088800,
            'location': ['Novi Sad', 'Telep'],
            'metadata': ['Šifra oglasa=473195', 'Tip=Stan', 'Grejanje=Gas', 'Broj soba=3', {'Dodatne informacije=Terasa, Internet, Kablovska, Uknjiženo, Telefon, Interfon'}],
            'images': ['http://www.nadjidom.com/images/photos/large/2018/04/19/ag5m7gk3cc-1523709843.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/iyu8jskrgt-1523709847.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/yria2ur5re-1523709959.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/82h9ejz6ni-1523709966.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/6zch47ee4t-1523709972.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/8wj82igjbc-1523710015.jpg', 'http://www.nadjidom.com/images/photos/large/2018/04/19/9dernc6e7d-1523710025.jpg']
        }
