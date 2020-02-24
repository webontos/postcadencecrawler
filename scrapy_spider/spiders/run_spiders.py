from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_spider.spiders.quotes_spider import PostcadenceSpider


def start():

    filename = "sites.txt"

    with open(filename, "r") as f:

        for site_base_url in f:

            start_urls = ["https://" + site_base_url, "https://www." + site_base_url]

            proc = CrawlerProcess(get_project_settings())
            proc.crawl(PostcadenceSpider, start_urls=start_urls)
            proc.start()


if __name__ == "__main__":
    start()
