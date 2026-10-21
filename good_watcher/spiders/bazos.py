import scrapy
from urllib.parse import urlencode
from scrapy.http import Response
import time

class bazos(scrapy.Spider):
    name = "bazos"

    def __init__(self, guard=None, notify=True, start_url=None, **kwargs):
        super().__init__(**kwargs)
        self.guard = guard 
        self.start_urls = [start_url]
        self.notify = notify

        

    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            dont_filter=True,
            callback=self.parse,
        )

    def parse(self, response: Response):
        for item in response.xpath('//div[@class="inzeraty inzeratyflex"]'):
            
            title = item.xpath('.//h2[@class="nadpis"]//text()').get()
            url = item.xpath('.//h2[@class="nadpis"]/a/@href').get()
            price = item.xpath('./div[@class="inzeratycena"]//text()').get()
            
            if price is None or title is None:
                continue
            
            price = "".join(ch for ch in price if ch.isdigit())
            price = "0" if price == "" else price
            price = int(price)

            yield {
                "guard": self.guard,
                "url": url,
                "title": title,
                "price": price,
                "notify": self.notify
            }

        next_page = response.xpath('//div[@class="strankovani"]/*')[-1]
        next_page = next_page.xpath('./@href').get()

        time.sleep(2)        
        if next_page is not None:
            print('FOLLOW NEXT PAGE')
            print(next_page)
            yield response.follow(next_page, callback=self.parse)

        