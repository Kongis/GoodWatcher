# GoodWatcher

> A terminal tool that watches Czech marketplaces for new listings, so you never miss a good deal.

GoodWatcher periodically scrapes your saved searches on several marketplaces,
stores the results in a local database and detects new items.

## Features

- Watch multiple marketplaces: **OdKarla.cz, Sbazar.cz, Bazos.cz, Cyklobazar.cz, Aukro.cz**
- Interactive terminal menu for adding new watchers
- Optional keyword filter per watcher
- Silent first run: existing listings are saved without triggering notifications
- Automatic crawling every hour in the background
- **Discord notifications** about new listings via webhook
- Graceful shutdown: a running crawl is finished before the app exits


## How it works

```
run.py (asyncio)
 ├── menu()     – reads commands from the terminal
 └── crawler()  – every hour launches crawler.py as a subprocess
                    └── Scrapy spiders → SQLite (data/app.db)
```

Each crawl runs in a separate process, so the Scrapy reactor starts fresh every
time and a crashing spider cannot take down the menu.

## Requirements

- Python 3.10+ (developed on 3.14)

## Installation

```bash
git clone git@github.com:YOUR_NAME/GoodWatcher.git
cd GoodWatcher

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

1. Create a Discord webhook: *Server Settings → Integrations → Webhooks → New Webhook*,
   choose the target channel and copy the webhook URL.
2. Copy the example environment file and fill in your webhook:

```bash
   cp .env.example .env
```

```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

3. The `data/` folder and the SQLite database (`data/app.db`) are created automatically on first run.
4. The crawl interval is set by `WAIT_TIME` in `run.py` (seconds, default 3600).

## Usage

```bash
python run.py
```

On start, the app performs a silent run and then shows a menu:

```
Choose:
1. Add new shop to watch
2. Terminate
```

Adding a watcher asks for: the marketplace, a watcher name, a search word and
an optional keyword filter. The first crawl of a new watcher is silent.
Choosing **Terminate** waits for a running crawl to finish, then exits.

Crawler output goes to `crawler.log`.

## Project structure

```
GoodWatcher/
├── run.py              # menu + scheduler
├── crawler.py          # entry point for a single crawl
├── good_watcher/
│   ├── db.py           # SQLite layer (Guard, Guards)
│   └── spiders/        # one Scrapy spider per marketplace
├── data/               # database (not tracked by Git)
└── requirements.txt
```

## Troubleshooting

- **`database is locked`**: two crawls wrote to SQLite at once. Wait and retry.
- **No items found**: the marketplace may have changed its layout. Check `crawler.log`.
