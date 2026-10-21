import scrapy
from urllib.parse import urlencode
from scrapy.http import Response
import requests

class odkarla(scrapy.Spider):
    name = "odkarla"

    def __init__(self, guard=None, notify=True, start_url=None, **kwargs):
        super().__init__(**kwargs)
        self.guard = guard 
        self.start_urls = [start_url]
        self.notify = notify

        

    async def start(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            headers={
                "Referer": "https://www.odkarla.cz/",
                "User-Agent": "Mozilla/5.0",
            },
            callback=self.parse,
        )

    def parse(self, response: Response):
        data = response.json()
        for item in data['results']['hits']:
        
            yield {
                "guard": self.guard,
                "url": "https://odkarla.cz" + item["url"],
                "title": item['attributes']['title'],
                "price": item['attributes']['price_amount'],
                "notify": self.notify 
            }