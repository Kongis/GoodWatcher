import scrapy
from urllib.parse import urlencode
from scrapy.http import Response
import requests
import time

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

class cyklobazar(scrapy.Spider):
    name = "cyklobazar"
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "USER_AGENT": "",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_impersonate.ImpersonateDownloadHandler",
            "https": "scrapy_impersonate.ImpersonateDownloadHandler",
        },
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_impersonate.RandomBrowserMiddleware": 1000,
        },
    }
    def __init__(self, guard=None, notify=True, start_url=None, **kwargs):
        super().__init__(**kwargs)
        self.guard = guard 
        self.start_urls = [start_url]
        self.notify = notify

        

    async def start(self):
        
        #res = requests.get(self.start_urls[0], headers=headers, timeout=10)

        #self.parse(res)
        
        
        yield scrapy.Request(
            url= self.start_urls[0],
            dont_filter=True,
            callback=self.parse,
        )
        

    def parse(self, response: Response):
        #print(response.text)


        for item in response.xpath('//li[@class="cb-offer-list__item"]'):
            #item = item.xpath('.//div[contains(@class, "@container group/card")]/a')
            
            title = item.xpath('./a//div[@class="cb-offer__header"]/h4/text()').get()  #('./div/*[1]/div[contains(@class, "@cardLg:pr-2")]//text()').get()
            url = item.xpath('./a/@href').get()
            price = item.xpath('./a//strong[@class="cb-offer__price"]').get()      #('.//div[contains(@class, "@cardLg:pr-2")]/*[2]/b//text()').get() or ""
            
            if price is None or title is None:
                continue
            
            price = "".join(ch for ch in price if ch.isdigit())
            price = "0" if price == "" else price
            price = int(price)
       
            yield {
                "guard": self.guard,
                "url": response.urljoin(url),
                "title": title,
                "price": price,
                "notify": self.notify
            }
        
        
        next_page = response.xpath('//li[@class="paginator__item paginator__item--next"]/a/@href').get()

        time.sleep(2)
        if next_page is not None:
            print('FOLLOW NEXT PAGE')
            print(next_page)
            yield response.follow(next_page, callback=self.parse)
        