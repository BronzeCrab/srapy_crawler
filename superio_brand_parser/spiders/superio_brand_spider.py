from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from superio_brand_parser.items import SuperioBrandParserItem
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector

items = []
visited_next_pages = []


class SuperioBrandSpider(CrawlSpider):
    name = "superiobrand"
    allowed_domains = ["superiobrand.com"]
    start_urls = [
        "http://superiobrand.com/store/index.php?main_page=index&cPath=35",
    ]
    rules = [
        Rule(LinkExtractor(
            allow=('store/index.php\?main_page=index&cPath=35_\\d{2}$')),
            callback='parse_category',
            follow=True),
    ]

    def parse_item(self, response):
        item = response.meta['item']
        products_id = response.url[-3:]
        if products_id[0] == "=":
            products_id = products_id[1:]
        item['products_id'] = products_id
        model = response.xpath(
            '//ul[@class="additional-info list-unstyled"]/li/text()').extract_first()
        i = model.index(':')
        model = model[i+2:]
        item['model'] = model
        title = response.xpath(
            '//div[@class="product-info col-lg-5 col-md-5 col-sm-5"]/h1/text()').extract_first()
        item['title'] = title
        description = response.xpath('//div[@class="product-description"]//text()')
        for x in description:
            if 'UPC' in x.extract():
                try:
                    i = x.extract().index('#')
                    item['upc'] = x.extract()[i+1:]
                except ValueError:
                    item['upc'] = x.extract()
                if item['upc'][0] == ' ':
                    item['upc'] = item['upc'][1:]
                continue
        hxs = HtmlXPathSelector(response)
        description = hxs.select('//div[@class="product-description"]')
        item['description'] = description.extract()[0]
        manufectured_by = response.xpath('//ul[@class="additional-info list-unstyled"]/li/text()').re_first(r'Manufactured by:\s*(.*)')
        item['manufectured_by'] = manufectured_by
        additional_images = response.xpath(
            '//div[@class="jcarousel-item"]/a/@data-image').extract()
        item['additional_images'] = ''
        for i, img in enumerate(additional_images):
            if i == len(additional_images) - 1:
                item['additional_images'] += img
            else:
                item['additional_images'] += img + ','
        yield item

    def extract_anchors(self, response):
        item = response.meta['item']
        anchors = response.xpath('//div[@class="product-list row"]//a')
        for anchor in anchors:
            item = dict(item)
            url = response.urljoin(anchor.xpath('@href').extract()[0])
            try:
                item['image_path'] = anchor.xpath('./img/@data-src').extract()[0]
            except:
                continue
            yield Request(url, callback=self.parse_item, meta={'item': item})

    def parse_inner_category(self, response):
        global visited_next_pages
        item = response.meta['item']
        anchors = response.xpath('//div[@class="product-list row"]//a')

        next_pages = response.xpath('//span[@class="pages"]/a/@href')

        for next_page_link in set([x.extract() for x in next_pages]):
            if next_page_link[-1] == '1' or next_page_link in visited_next_pages:
                continue
            else:
                visited_next_pages.append(next_page_link)
                yield Request(next_page_link, callback=self.extract_anchors, meta={'item': item})

        for anchor in anchors:
            item = dict(item)
            url = response.urljoin(anchor.xpath('@href').extract()[0])
            try:
                item['image_path'] = anchor.xpath('./img/@data-src').extract()[0]
            except:
                continue
            yield Request(url, callback=self.parse_item, meta={'item': item})

    def parse_category(self, response):
        category = response.xpath('//h1[@class="page-title"]/text()')
        for sel in (response.xpath('//div[@class="pro-cat"]/a')):
            item = SuperioBrandParserItem()
            item['category'] = category.extract()[0]
            item['inner_category'] = sel.xpath('text()').extract()[0]
            href = sel.xpath('@href').extract()[0]
            url = response.urljoin(href)
            yield Request(url, callback=self.parse_inner_category,
                          meta={'item': item})
