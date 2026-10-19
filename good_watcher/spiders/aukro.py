import scrapy
from urllib.parse import urlencode
from scrapy.http import Response
import requests
import time
import json

class aukro(scrapy.Spider):
    name = "aukro"

    def __init__(self, guard=None, notify=True, start_url=None, **kwargs):
        super().__init__(**kwargs)
        self.guard = guard 
        self.start_urls = [start_url]
        self.notify = notify

        

    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            #cookies=
            #    {'euconsent-v2': 'CQr-V4AQr-V4AD3ACQCSCzF8AP_gAEPgAATILdwPAAFAAQAAqABkAEAAKAAWgAyABoAEUAJIATAAnABbgC8AL8AYQBiAEBAIIAhABFACOAE4AKEAcQA7gCEAEaAJEAUgAswBpwDtgHvAQ4AjoBKwCbQFSAKyAWSAtwBeYDCAGMgMbAZYAy4BoYDUQGygP8AgOBCsCMwEbwJNAStAp6BYECwoFuwW7gQgAVABAADIAGgARQAmABiAD8AIQARwAnAB3AEIAIsARoAkQB2wErAJtAVIArIBbgC8wGWAMuAbKBCsCMwEbwJVgStAsKBbsAAA.ILdwQgAFAAQAAqABkAEAAKAAWgAyABoAEUAJIATAAnABbgC8AL8AYQBiAD8AICAQQBCACKAEcAJwAUIAzQBxADuAIQARYAjQBIgCkAFmANOAdsA94CHAEdAJWATaAqQBWQCyQFuALzAYQAxkBjYDLAGXANDAaiA2UB_gEBwIVgRmAjeBJoCVYErQKegVgAr4BYECwoFuwAAA.YAAAAAAAAWAA',
            #     'szncmpone': '1'}
            #,
            dont_filter=True,
            #headers={
            #    "Referer": "https://www.odkarla.cz/",
            #    "User-Agent": "Mozilla/5.0",
            #},
            callback=self.parse,
        )

    def parse(self, response: Response):

        text = response.xpath('//script[@id="jsonld-LISTING"]/text()').get()
        data: dict = json.loads(text)

        for item in data["mainEntity"]["itemListElement"]:
            print(f"{item["name"]} - {item["offers"]["price"]} - {item["url"]}")
        
            yield {
                "guard": self.guard,
                "url": item["url"],
                "title": item["name"],
                "price": item["offers"]["price"],
                "notify": self.notify
            }

        next_page = response.xpath('//a[@class="page-number next"]/@href').get()

        time.sleep(2)
        if next_page is not None:
            print('FOLLOW NEXT PAGE')
            print(next_page)
            yield response.follow(next_page, callback=self.parse)
        