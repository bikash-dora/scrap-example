from scraper.nekretnine_rs_scraper import NekretnineRsScraper
import requests_mock
from decimal import Decimal


def test_nekretnine_scraper_fetch_links():
    scraper = NekretnineRsScraper()
    with requests_mock.mock() as mock:
        mock.get(scraper.url.replace('{PAGE_NUMBER}', '1'), text=open('data_files/nekretnine_rs_adverts.html', 'r').read())
        links = scraper.fetch_links(1)
        assert len(links) == 50


def test_nekretnine_scraper_process_link():
    scraper = NekretnineRsScraper()
    with requests_mock.mock() as mock:
        mock.get('https://nekretnire.rs/stan/1', text=open('data_files/nekretnine_rs_advert.html', 'r').read())
        data = scraper.process_link('https://nekretnire.rs/stan/1')
        assert data == {
            'link': 'https://nekretnire.rs/stan/1', 
            'title': 'DVOSOBAN STAN NA LIMANU 1!!!',
            'location': ['Liman 1'],
            'area': 50,
            'price': Decimal('50470.00'),
            'text': 'DVOSOBAN STAN NA LIMANU 1,UKNJIŽEN,VREDI POGLEDATI.(Kodeks i Dunav Nekretnine-Đorđević Nekretnine DOO Novi Sad upisan u Reg. Pos. Broj 183) ŠIFRA:1036848',
            'metadata': ['ID=1596605', 'Objavljen=13.03.2018.', 'Oglas od=Zastupnik', 'Uknjiženo=Da', 'Sobe=2', 'Kupatila=1', 'Na spratu=7', 'Ukupno Spratova=8'],
            'advertiser': {'name': ' Nikolina Popović 21000 Novi Sad', 'phones': ['0658118033', '0645983023']},
            'timestamp': 1520895600,
            'images': [
                'https://www.nekretnine.rs/data/images/2018/03/13/1036848T1520931634_540c.jpg',
                'https://www.nekretnine.rs/data/images/2018/03/13/1490174216T1520931634_540c.jpg',
                'https://www.nekretnine.rs/data/images/2018/03/13/1490174265T1520931635_540c.jpg',
                'https://www.nekretnine.rs/data/images/2018/03/13/1490174280T1520931636_540c.jpg',
                'https://www.nekretnine.rs/data/images/2018/03/13/1490174291T1520931636_540c.jpg',
                'https://www.nekretnine.rs/data/images/2018/03/13/1490176137T1520931637_540c.jpg'
                ]
            }
