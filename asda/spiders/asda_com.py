import scrapy
from scrapy import Request
import json
from .constans import *
from asda.items import Product
import re


class AsdaComSpider(scrapy.Spider):
    name = 'asda.com'
    allowed_domains = ['groceries.asda.com']
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 90,
    }

    def start_requests(self):
        start_url = [
            'https://groceries.asda.com/shelf/health-beauty/hair-care/shampoo-conditioner/shampoo/1215135760648-1215431206069-1215431208618-1215431208672']
        for url in start_url:
            yield Request(url=url, callback=self.parse_urls_lst)

    def parse_urls_lst(self, response):
        global BODY_CATEGORY
        page = 0
        x = str(response.url)
        hierarchy = x.rsplit('/')[-1]
        hierarchy_id = '"hierarchy_id"' + ":" + '"{}"'.format(str(hierarchy))   #id категории для тела запроса
        url = 'https://groceries.asda.com/api/bff/graphql'
        for i in range(10):
            page += 1
            page_number = '"page":{},'.format(page) + '"request_origin":"gi","ship_date":1634338800000,"payload":{"page_type":"aisle",' #номер страницы для тела запроса
            BODY_CATEGORY = body_ctg_pt_1 + str(page_number) + hierarchy_id + body_ctg_pt_3  # сбор тела запроса для парсинга page_id товаров со страницы категории
            yield Request(url=url, method='POST', headers=HEADERS, body=BODY_CATEGORY, callback=self.parse_category)


    def parse_category(self, response):
        dict_urls = json.loads(response.text)
        page_id_for_parse = dict_urls['data']['tempo_cms_content']['zones'][1]['configs']['skus']
        for item in page_id_for_parse:
            page_id = '"payload"' + ':' + '{' + '"page_id"' + ':' + '"{}"'.format(item)
            BODY_ITEMS = body_item_pt1 + page_id + body_item_pt3  # тело запроса для парсинга товаров
            url = 'https://groceries.asda.com/api/bff/graphql'
            yield Request(url=url, method='POST', headers=HEADERS,
                          body=BODY_ITEMS, callback=self.parse)

    def parse(self, response):
        item = Product()
        i = json.loads(response.text)
        item['RPC'] = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["item"]['sku_id']
        item['title'] = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["item"]['name']
        item['brand'] = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["item"]['brand']
        item['price'] = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["price"]["price_info"]["price"]
        reviews = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["item"]["rating_review"]["total_review_count"]
        rating = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["item"]["rating_review"]["avg_star_rating"]
        item['reviews_data'] = {"reviews_count": reviews, "avg_rating": rating}
        stock = i["data"]["tempo_cms_content"]["zones"][0]["configs"]["products"]["items"][0]["inventory"]["availability_info"]["availability"]
        if stock == 'A':
            item['stock'] = True
        else:
            item['stock'] = False
        yield item
