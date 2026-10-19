import asyncio
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from good_watcher.db import connection, Guards, Guard

conn = connection("data/app.db")
guards = Guards(conn)

ODKARLA_URL = "https://live.luigisbox.tech/search?tracker_id=224905-260203&f[]=type:item&f[]=availability:1&q={key}&sort=price_amount:desc&size=48"
SBAZAR_URL = "https://www.sbazar.cz/hledej/{key}"
BAZOS_URL = "https://www.bazos.cz/search.php?hledat={key}"
CYKLOBAZAR_URL = 'https://www.cyklobazar.cz/vsechny-kategorie?q={key}'
AUKRO_URL = 'https://aukro.cz/lp/nejlepsi-{key}'
WAIT_TIME = 3600

async def crawler(flag_stop: asyncio.Event):
    print('\n Silent run start')
    
    with open("crawler.log", "a") as log:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "crawler.py", "--first",
            stdout=log, stderr=log,
        )
    await proc.wait()
    print("\n Silent run was successful")

    while flag_stop.is_set():

        try:
            await asyncio.wait_for(flag_stop.wait(), timeout=WAIT_TIME)
            break
        
        except asyncio.TimeoutError:
            print('\n Normal run start')

            with open("crawler.log", "w") as log:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, "crawler.py",
                    stdout=log, stderr=log,
                )
            await proc.wait()
            print("\n Normal run was successful")

async def first_crawl(name: str):

    record = guards.get(name)

    with open("silent_crawler.log", "a") as log:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "crawler.py", "--first", record.name,
            stdout=log, stderr=log,
        )
    await proc.wait()

async def newShop():

    while True:

        print("Web to watch:")
        print("1.) OdKarla.cz")
        print("2.) Sbazar.cz")
        print("3.) Bazos.cz")
        print("4.) Cyklobazar")
        print("5.) Aukro.cz")
        print("6.) Exit")

        try:
                answer = int(await asyncio.to_thread(input, "Zvol 1-5: "))
                name = str(await asyncio.to_thread(input, "Name Watcher: "))
                search = str(await asyncio.to_thread(input, "Search word: "))
                keywords = str(await asyncio.to_thread(input, "Keyword (Optional): "))

        except Exception as e:
            print(e)
            continue

        try:
            match answer:
                
                    case 1:
                        guards.add_shop(Guard(name, 
                            ODKARLA_URL.format(key=search), 
                            "odkarla", keywords))
                        await first_crawl(name)

                    case 2:
                        guards.add_shop(Guard(name, 
                            SBAZAR_URL.format(key=search), 
                            "sbazar", keywords))
                        await first_crawl(name)

                    case 3:
                        guards.add_shop(Guard(name, 
                            BAZOS_URL.format(key=search), 
                            "bazos", keywords))
                        await first_crawl(name)
                        
                    case 4:
                        guards.add_shop(Guard(name, 
                            CYKLOBAZAR_URL.format(key=search), 
                            "cyklobazar", keywords))
                        await first_crawl(name)
                        
                    case 5:
                        guards.add_shop(Guard(name, 
                            AUKRO_URL.format(key=search), 
                            "aukro", keywords))
                        await first_crawl(name)

                    case 6:
                        return
                    case _:
                        print("Unsupported input")
                        continue

        except Exception as error:
            print(error)

async def menu(flag_stop: asyncio.Event):
    while True:
        print("1. Add new shop to watch")
        print("2. Terminate")
        try:
            answer = int(await asyncio.to_thread(input, "Choose:"))
        except Exception as e:
            print(e)
            continue

        match answer:
            case 1:
                await newShop()

            case 2:
                flag_stop.set()
                return
            
            case _:
                print("Unsupported input")

async def main():
    stop = asyncio.Event()

    await asyncio.gather(
        crawler(stop),
        menu(stop),
    )


if __name__ == "__main__":
    asyncio.run(main())
    
    #ONLY FOR DEBUG
    #process = CrawlerProcess(get_project_settings())
    #guard = guards.get("bazos-garmin")
    #process.crawl(guard.spider, guard=guard.name, notify=False, start_url=guard.url)
    #process.start()
    #subprocess.run([sys.executable, "crawler.py", "--first"], check=True)
    #exit(0)