import requests
import os
from dotenv import load_dotenv
from itemadapter import ItemAdapter
from good_watcher.db import connection, Goods
import time
from datetime import datetime, timezone
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

load_dotenv()
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
#https://discord.com/api/webhooks/1558149883649728635/Z4AMF_IpLvZgstm4sZNsZRIZ3VTsfgXWuNNyjLAoIZI8dLenb0EDQ3cp16gZLvhiKJPg

COLOR_NEW = 0x2ECC71        # zelená
COLOR_DROP = 0x2ECC71       # zelená: cena klesla
COLOR_RISE = 0xE74C3C       # červená: cena stoupla

def fmt_price(value: float) -> str:
    return f"{value:,.0f}".replace(",", "\u00a0") + "\u00a0Kč"

def notify(type, item, old_price=0):
    match type:
        case 0: #New product

            embed = {
                "title": f"🆕 {item['title']}"[:256],
                "url": item["url"],
                "description": f"Nové zboží za **{fmt_price(item['price'])}**",
                "color": COLOR_NEW,
                "fields": [
                    {"name": "Cena", "value": fmt_price(item["price"]), "inline": True},
                    {"name": "Watcher", "value": item['guard'], "inline": True},
                ],
                "footer": {"text": "GoodWatcher"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        case 1: #Price change
            new_price: float = item["price"]
            diff = new_price - old_price
            percent = diff / old_price * 100 if old_price else 0
            dropped = diff < 0

            arrow = "📉" if dropped else "📈"
            sign = "" if dropped else "+"

            embed = {
                "title": f"{arrow} {item['title']}"[:256],
                "url": item["url"],
                "description": f"~~{fmt_price(old_price)}~~ → **{fmt_price(new_price)}**",
                "color": COLOR_DROP if dropped else COLOR_RISE,
                "fields": [
                    {"name": "Původní cena", "value": fmt_price(old_price), "inline": True},
                    {"name": "Nová cena", "value": fmt_price(new_price), "inline": True},
                    {
                        "name": "Změna",
                        "value": f"{sign}{fmt_price(diff)} ({sign}{percent:.1f} %)",
                        "inline": True,
                    },
                    {"name": "Watcher", "value": item['guard'], "inline": False},
                ],
                "footer": {"text": "GoodWatcher"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    payload = {"embeds": [embed]}
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    if not resp.ok:
        print("DISCORD ODPOVĚĎ:", resp.status_code, resp.text)
        print("ODESLANÝ PAYLOAD:", embed)
    time.sleep(5)

class GoodWatcherPipeline:
    def open_spider(self, spider):
        self.conn = connection("data/app.db")
        self.products = Goods(self.conn)

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        result = self.products.upsert(item)
        if result is None:
            return
        
        if result == -1:
            spider.logger.info(f"Nové zboží: {item['title']}")
            if item['notify']:
                notify(0, item)
        else:
            spider.logger.info(f"Změna ceny: {item['title']} -> {item['price']}")
            if item['notify']:
                notify(1, item, result)

