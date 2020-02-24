# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    page_url = scrapy.Field()
    page_section = scrapy.Field()
    page_type = scrapy.Field()
    page_publication_date = scrapy.Field()
    page_modification_date = scrapy.Field()
    page_wordcount = scrapy.Field()
    page_ext_links = scrapy.Field()

    site_url = scrapy.Field()
    site_id = scrapy.Field()





