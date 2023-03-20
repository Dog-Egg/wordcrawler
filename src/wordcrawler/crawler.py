import cgi
import fnmatch
import re
from collections import Counter

import pydash
import scrapy
from scrapy.http.response import Response
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess

# 至少包含2个字母
ENGLISH_WORD_PATTERN = re.compile(r"^[a-zA-Z]{2,}$")


def extract_words(text):
    for w in pydash.words(text):
        if ENGLISH_WORD_PATTERN.match(w):
            yield w


class WordSpider(scrapy.Spider):
    name = 'word-spider'

    def __init__(self, start_url: str, urlpattern: str, callback):
        super().__init__()

        self.start_url = start_url
        self.urlpattern = re.compile(fnmatch.translate(urlpattern))
        self.callback = callback

        self.link_extractor = LxmlLinkExtractor()
        self.word_counter = Counter()

    def start_requests(self):
        yield scrapy.Request(self.start_url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        mimetype, options = cgi.parse_header(response.headers['Content-Type'].decode())
        # 只处理 HTML 的内容，排除 js、压缩文件类型等
        if mimetype == 'text/html':
            for text in response.xpath('//body//text()').getall():
                for word in extract_words(text):
                    self.callback(word)

            for link in self.link_extractor.extract_links(response):
                if self.urlpattern.search(link.url):
                    yield response.follow(link.url, callback=self.parse)
                else:
                    self.logger.info('忽略 %s (不匹配)', link.url)


def run_spider(**kwargs):
    process = CrawlerProcess(settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(WordSpider, **kwargs)
    process.start()
