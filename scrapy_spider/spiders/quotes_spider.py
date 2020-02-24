# -*- coding: utf-8 -*-
import scrapy
from scrapy_spider.items import CrawlerItem

from urllib.parse import urlparse
import random


class PostcadenceSpider(scrapy.Spider):

    name = 'webpages_spider'
    allowed_domains = ['selfgrowth.com']
    start_urls = ['https://www.selfgrowth.com/', 'https://selfgrowth.com/']

    requested_urls = set()
    site_urls = set()

    def parse(self, response):

        try:

            content_type = response.xpath(".//head/meta[@property='og:type'][1]/@content").get()
            section = response.xpath(".//head/meta[@property='article:section'][1]/@content").get()
            publication_date = response.xpath(".//head/meta[@property='article:published_time'][1]/@content").get()
            modification_date = response.xpath(".//head/meta[@property='article:modified_time'][1]/@content").get()

            page_text = response.xpath("//body//p").getall()
            wordcount = sum(len(s) for s in page_text)

            crawl_item = CrawlerItem()

            if not section:
                section = "Uncategorized"
            crawl_item["page_section"] = section
            crawl_item["page_type"] = content_type
            crawl_item["page_publication_date"] = publication_date
            crawl_item["page_modification_date"] = modification_date
            crawl_item["page_url"] = response.request.url
            crawl_item["page_wordcount"] = wordcount

            o = urlparse(response.request.url)
            s = str(o.netloc).split("www.")
            site_base_url = s[len(s) - 1]
            crawl_item["site_url"] = site_base_url

            ext_links_exp = "//a[starts-with(@href, '{}') and not (contains(@href, '{}'))]/@href".format("http",
                                                                                                          site_base_url)

            crawl_item["page_ext_links"] = response.xpath(ext_links_exp).getall()

            yield crawl_item

            internal_urls_exp = "//a[starts-with(@href, '{}') or starts-with(@href, '{}')]/@href".format(
                self.start_urls[0], self.start_urls[1])

            print("EXT************")
            print(internal_urls_exp)

            page_urls = response.xpath(internal_urls_exp).getall()
            random.shuffle(page_urls)
            print(page_urls)

            self.site_urls = self.site_urls.union(page_urls)

            unrequested_urls = self.site_urls.difference(self.requested_urls)

            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
                'Sec-Fetch-User': '?1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            for next_url in unrequested_urls:
                absolute_next_page_url = response.urljoin(next_url)
                self.requested_urls.add(next_url)
                yield scrapy.Request(absolute_next_page_url, headers=headers)

        except Exception as error:
            print(error)
