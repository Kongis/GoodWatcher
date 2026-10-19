import asyncio
import sys

async def crawler():
    while True:
        proc = await asyncio.create_subprocess_exec(sys.executable, "crawler.py")
        await proc.wait()
        await asyncio.sleep(3600)

async def menu():
    while True:
        print("Choose:")
        print("1. Add new shop to watch")
        try:
            answer = int(await asyncio.to_thread(input))
        except Exception as e:
            print(e)
            continue
        match answer:
            case 1:
                #newShop() -> v realnem kodu
                pass
            case _:
                print("Unsupported input")

async def main():
    await asyncio.gather(
        crawler(),
        menu(),
    )

asyncio.run(main())