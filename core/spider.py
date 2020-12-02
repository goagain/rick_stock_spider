import lxml.html
import urllib3
import re

class Spider:
    def __init__(self):
        self.url = 'https://www.prnewswire.com/news-releases/news-releases-list/'
        self.pool = urllib3.PoolManager()
    
    def get_news_urls(self):
        html_page = self.http_request(self.url)

        html = lxml.etree.HTML(html_page.decode('utf-8'))
        hrefs = html.xpath("//a[@class='news-release']")
        return [href.get('href') for href in hrefs]

    def http_request(self, url):
        req = self.pool.request(url = url, method = 'get')
        return req.data
    
    def get_model(self):
        ret = []
        urls = self.get_news_urls()

        for sub_url in urls:
            url = f"https://www.prnewswire.com/{sub_url}"
            item = {}
            article = ArticleReader(url, self)

            item['title'] = article.title
            item['symbols'] = article.symbols
            item['time'] = article.time
            item['body'] = article.body
            item['url'] = url
            ret.append(item)
        return ret

class ArticleReader:
    '''Read and Parse Article'''

    def __init__(self, url, parent):
        self.parent = parent
        self.url = url
        xml = self.parent.http_request(url)
        self._xml = xml
        self._element_tree = lxml.etree.HTML(xml)

    @property
    def time(self):
        '''Return the time of the Article'''
        element = self._element_tree.xpath("//p[@class='mb-no']")
        return element[0].text if element else ''

    @property
    def title(self):
        '''Return the title of the Article'''
        element = self._element_tree.xpath("//h1")
        return element[0].text if element else ''

    @property
    def body(self):
        '''Return the body of the Article'''
        elements = self._element_tree.xpath(
            "//section[@class='release-body container ']")
        text = ''
        if len(elements) > 0:
            text = ''.join(elements[0].itertext()).strip()

        elements = self._element_tree.xpath(
            "//section[@class='release-body container']")
        if len(elements) > 0:
            text = ''.join(elements[0].itertext()).strip()

        return text

    @property
    def symbols(self):
        '''Return stock symbols in the Article'''
        result = []
        elements = self._element_tree.xpath("//a[@class='ticket-symbol']")
        for element in elements:
            if element.text not in result:
                result.append(element.text)
        # matches = re.findall(r"\(([A-Z]{2,7})\)", self.body)
        # for match in matches:
        #     if match not in result:
        #         result.append(match)
        return result

