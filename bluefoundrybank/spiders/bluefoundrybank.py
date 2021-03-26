import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bluefoundrybank.items import Article


class BluefoundrybankSpider(scrapy.Spider):
    name = 'bluefoundrybank'
    start_urls = ['https://bluefoundrybank.com/news/fetch?skip=0&limit=1000']

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="col-xs-12 col-md-6 details"]/span/text()').get()
        if date:
            date = " ".join(date.split()[1:4])

        content = response.xpath('//div[@class="col-xs-12 col-md-offset-1 col-md-10 col-lg-offset-2 col-lg-8 content"]'
                                 '//*[not(div[@class="col-xs-12 col-md-6 share-icons"])]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
