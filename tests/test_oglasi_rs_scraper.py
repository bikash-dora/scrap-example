import requests_mock
from scraper.oglasi_rs_scraper import OglasiRsScraper
from decimal import Decimal


def test_oglasi_fetch_links():
    scraper = OglasiRsScraper()
    with requests_mock.mock() as mock:
        mock.get(scraper.url.replace('{PAGE_NUMBER}', '1'), text=open('data_files/oglasi_rs_adverts.html', 'r').read())
        links = scraper.fetch_links(1)
        assert len(links) == 24


def test_oglasi_process_link():
    scraper = OglasiRsScraper()
    with requests_mock.mock() as mock:
        mock.get('https://www.oglasi.rs/stan/1', text=open('data_files/oglasi_rs_advert.html').read())
        data = scraper.process_link('https://www.oglasi.rs/stan/1')
        assert data == {'link': 'https://www.oglasi.rs/stan/1', 'title': 'Renoviran ,dvosoban stan', 'location': ['Liman 3'], 'area': 49, 'price': Decimal('49900.00'), 'text': 'Potpuno renoviran stan pre nepune tri godine .Urađena pvc stolarija (prozori ),sigurnosna vrata sa tri brave ,renovirana terasa,kuhinja ( urađena keramika ,vodovod kao i celo kupatilo ).Hoblovan parket,izgletovani zidovi.U dečijoj sobi postavljen kvalitetan ,vrhunski laminat.Sastoji se iz kuhinje ,kupatila,dnevne sobe i vece spavaće sobe .Zbog prostranog hodnika lako može da se prepravi u dvoiposoban stan. Dvosoban ,komforan stan na odličnoj lokaciji ,idealan za porodične ljude i svu decu.Ogroman ,prostran parking .Neposredna blizina vrtića ,na minut hoda,škole ,igrališta za decu ,limanskog parka ,keja,gradske plaže Štrand,domova Zdravlja,apoteka,velikih marketa,pošte ,pijace. .Autobuska stanica na minut hoda i odlična povezanost sa većim delovima grada. Sve na jednom mestu.', 'metadata': ['Sobnost=Dvosoban', 'Stanje objekta=Starija gradnja', 'Grejanje=Gradsko', 'Nivo u zgradi=3. sprat', 'Dodatne informacije=Terasa, Parking, garaža'], 'advertiser': {'name': 'pr.natasha', 'phones': ['0607189739']}, 'timestamp': 1524130619, 'images': ['https://www.oglasi.rs/serve/2874e053-5238-499b-852c-a055a24e71fd/original-20170513_190240.jpg', 'https://www.oglasi.rs/serve/2874e053-5238-499b-852c-a055a24e71fd/original-20170513_185759.jpg', 'https://www.oglasi.rs/serve/2874e053-5238-499b-852c-a055a24e71fd/original-20170513_185705.jpg']}
