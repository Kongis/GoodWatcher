import scrapy
from urllib.parse import urlencode
from scrapy.http import Response
import requests
import time

class sbazar(scrapy.Spider):
    name = "sbazar"

    def __init__(self, guard=None, notify=True, start_url=None, **kwargs):
        super().__init__(**kwargs)
        self.guard = guard 
        self.start_urls = [start_url]
        self.notify = notify

    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            cookies=
                {'euconsent-v2': 'CQr-V4AQr-V4AD3ACQCSCzF8AP_gAEPgAATILdwPAAFAAQAAqABkAEAAKAAWgAyABoAEUAJIATAAnABbgC8AL8AYQBiAEBAIIAhABFACOAE4AKEAcQA7gCEAEaAJEAUgAswBpwDtgHvAQ4AjoBKwCbQFSAKyAWSAtwBeYDCAGMgMbAZYAy4BoYDUQGygP8AgOBCsCMwEbwJNAStAp6BYECwoFuwW7gQgAVABAADIAGgARQAmABiAD8AIQARwAnAB3AEIAIsARoAkQB2wErAJtAVIArIBbgC8wGWAMuAbKBCsCMwEbwJVgStAsKBbsAAA.ILdwQgAFAAQAAqABkAEAAKAAWgAyABoAEUAJIATAAnABbgC8AL8AYQBiAD8AICAQQBCACKAEcAJwAUIAzQBxADuAIQARYAjQBIgCkAFmANOAdsA94CHAEdAJWATaAqQBWQCyQFuALzAYQAxkBjYDLAGXANDAaiA2UB_gEBwIVgRmAjeBJoCVYErQKegVgAr4BYECwoFuwAAA.YAAAAAAAAWAA',
                 'szncmpone': '1'}
            ,
            dont_filter=True,
            callback=self.parse,
        )

    def parse(self, response: Response):
        for item in response.xpath('//div[contains(@class, "w-screen-offer-card-list")]/*[2]//ul[@data-test="offer-list"]/*'):
            item = item.xpath('.//div[contains(@class, "relative")]/a')
            
            title = item.xpath('.//div[contains(@class, "group-hover/card:text-red-hover")]//text()').get()
            url = item.xpath('./@href').get()
            price = item.xpath('.//div[contains(@class, "line-clamp-1 text-ellipsis text-dark-blue-60")]/b/text()').get()

            if price is None or title is None:
                print("Invalid offer")
                continue
            
            price = "".join(ch for ch in price if ch.isdigit())
            price = 0 if price == "" else price
            price = int(price)

            yield {
                "guard": self.guard,
                "url": response.urljoin(url),
                "title": title,
                "price": price,
                "notify": self.notify
            }

        next_page = response.xpath('//astro-island[@data-preact-island-id="31"]/div/a/@href').get()

        time.sleep(2)
        if next_page is not None:
            print('FOLLOW NEXT PAGE')
            print(next_page)
            yield response.follow(next_page, callback=self.parse)