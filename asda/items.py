# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    url = scrapy.Field()
    RPC = scrapy.Field()
    brand = scrapy.Field()
    reviews_data = scrapy.Field()
