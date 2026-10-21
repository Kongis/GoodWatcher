from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from good_watcher.db import connection, Guards, Guard

try:

    conn = connection("data/app.db")
    guards = Guards(conn)
    process = CrawlerProcess(get_project_settings())

    for g in guards.active():
        process.crawl(g.spider, guard=g.name, notify=not g.first, start_url=g.url)

    process.start()
    guards.firstRun()
    print("firstRun called")
    exit(0)

except Exception as e:
    print(e)
    exit(404)

