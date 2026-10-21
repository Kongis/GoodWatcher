import sys
import subprocess
import os
import time
import tomllib
from good_watcher.db import connection, Guards, Guard
from dotenv import load_dotenv

load_dotenv()

conn = connection(os.environ["DB_PATH"]) #connection("data/app.db")
guards = Guards(conn)

ODKARLA_URL = "https://live.luigisbox.tech/search?tracker_id=224905-260203&f[]=type:item&f[]=availability:1&q={key}&sort=price_amount:desc&size=48"
SBAZAR_URL = "https://www.sbazar.cz/hledej/{key}"
BAZOS_URL = "https://www.bazos.cz/search.php?hledat={key}"
CYKLOBAZAR_URL = 'https://www.cyklobazar.cz/vsechny-kategorie?q={key}'
AUKRO_URL = 'https://aukro.cz/lp/nejlepsi-{key}'
WAIT_TIME = 3600

def crawler():
    
    while True:
        print('Crawler start')
        
        with open("crawler.log", "w") as log:
            subprocess.run(
                [sys.executable, "crawler.py"],
                stdout=log, stderr=log,
            )

        print("Crawler was successful")
        time.sleep(WAIT_TIME)


                
def loadGuard():
    guards.deactivateAll()
    with open("watchers.toml", "rb") as f:
        watchers = tomllib.load(f)

    for w in watchers["watcher"]:

        match w['site']:
            
            case 'odkarla':
                url = ODKARLA_URL.format(key=w['search'])
            case 'bazos':
                url = BAZOS_URL.format(key=w['search'])
            case 'aukro':
                url = AUKRO_URL.format(key=w['search'])
            case 'cyklobazar':
                url = CYKLOBAZAR_URL.format(key=w['search'])
            case 'sbazar':
                url = SBAZAR_URL.format(key=w['search'])

            case _:
                print("Invalid site")

        newGuard = Guard(w['name'], url, w['site'],w.get('keywords', ""), True)
        guards.add_shop(newGuard)

if __name__ == "__main__":
    loadGuard()
    crawler()
    
    #ONLY FOR DEBUG
    #process = CrawlerProcess(get_project_settings())
    #guard = guards.get("bazos-garmin")
    #process.crawl(guard.spider, guard=guard.name, notify=False, start_url=guard.url)
    #process.start()
    #subprocess.run([sys.executable, "crawler.py", "--first"], check=True)
    #exit(0)