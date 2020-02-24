# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from sqlalchemy.orm import sessionmaker
from scrapy_spider.models import WebPages, Sites, ExternalLinks, db_connect, create_table
from datetime import datetime
from urllib.parse import urlparse


class ScrapySpiderPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.site_id = None

    def process_item(self, item, spider):
        """

        This method is called for every item pipeline component.

        """
        session = self.Session()

        webpage = WebPages()
        webpage.section = item["page_section"]
        webpage.type = item["page_type"]
        webpage.url = item["page_url"]
        webpage.publication_date = item["page_publication_date"]
        webpage.modification_date = item["page_modification_date"]
        webpage.wordcount = item["page_wordcount"]
        webpage.last_crawl_date = datetime.now()

        site = Sites()
        site.url = item["site_url"]
        site.last_crawl_date = datetime.now()
        site.crawl_status = "CRAWELING"

        if not self.site_id:
            self.site_id = session.query(Sites.id).filter(Sites.url == site.url)

        """

        try:
            if not self.site_id:

                session.add(site)
                session.commit()
                session.refresh(site)
                self.site_id = site.id

            webpage.site_id = self.site_id
            session.add(webpage)
            session.commit()
            session.refresh(webpage)

            for link in item["page_ext_links"]:
                externallink = ExternalLinks()
                externallink.page_id = webpage.id
                o = urlparse(link)
                s = str(o.netloc).split("www.")
                externallink.ext_domain = s[len(s) - 1]
                session.add(externallink)
                
            session.commit()

        except Exception as error:
            print(error)
            session.rollback()

        finally:
            session.close()
            
        """

        return item


