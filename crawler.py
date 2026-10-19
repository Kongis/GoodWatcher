import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from good_watcher.db import connection, Guards, Guard

try:

    conn = connection("data/app.db")
    guards = Guards(conn)

    parser = argparse.ArgumentParser()
    parser.add_argument("--first", action="store_true", default=False)
    parser.add_argument("--name", type=str, default="", help="Name watcher for silent first run")
    args = parser.parse_args()

    if args.name:

        process = CrawlerProcess(get_project_settings())
        guard = guards.get(args.name)
        process.crawl(guard.spider, guard=guard.name, notify=False, start_url=guard.url)
        process.start()
        exit(0)

    process = CrawlerProcess(get_project_settings())

    for g in guards.active():
        process.crawl(g.spider, guard=g.name, notify=not args.first, start_url=g.url)

    process.start()
    exit(0)

except Exception as e:
    print(e)
    exit(404)

