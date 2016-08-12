# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SuperioBrandParserItem(scrapy.Item):
    products_id = scrapy.Field()
    model = scrapy.Field()
    upc = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    manufectured_by = scrapy.Field()
    category = scrapy.Field()
