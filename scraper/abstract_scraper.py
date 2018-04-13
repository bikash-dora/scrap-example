import hashlib
import mechanicalsoup
import logging

log = logging.getLogger('AbstractScraper')


class AbstractScraper:

    _browser = None

    def process(self, page_number=1):
        print('Started to scrape {}'.format(self.get_name()))
        data = []
        print('{} - processing page {}'.format(self.get_name(), page_number))
        links = self.fetch_links(page_number)
        for link in links:
            try:
                processed = self.process_link(link)
                processed['title_hash'] = hashlib.sha1(processed['title'].encode('utf-8')).hexdigest()
                data.append(processed)
            except Exception as e:
                print('Failed to process {}, error: {}'.format(link, str(e)))
        return data

    def fetch_links(self, page_number):
        raise NotImplementedError('Abstract method must be implemented')

    def process_link(self, link):
        raise NotImplementedError('Abstract method must be implemented')

    def get_name(self):
        raise NotImplementedError('Abstract method must be implemented')

    def browser(self):
        if self._browser is None:
            self._browser = mechanicalsoup.StatefulBrowser()
        return self._browser

