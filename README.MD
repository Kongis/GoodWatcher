# 🛒 GoodWatcher

> Watches Czech marketplaces for new listings and sends them straight to Discord, so you never miss a good deal. 🎯

GoodWatcher periodically scrapes your saved searches on several marketplaces,
stores the results in a local SQLite database and notifies you about new items.

## ✨ Features

- 🏪 Watch multiple marketplaces: **OdKarla.cz, Sbazar.cz, Bazos.cz, Cyklobazar.cz, Aukro.cz**
- 📝 Watchers defined in a single `watchers.toml` file
- 🔎 Optional keyword filter per watcher
- 🤫 Silent first run: existing listings are saved without triggering notifications
- ⏰ Automatic crawling every hour
- 🔔 **Discord notifications** about new listings via webhook
- 🐳 Runs locally or in **Docker**
- 🛡️ Removed watchers are only deactivated, never deleted, so no data is lost by accident
- 💾 Persistent database in Docker via volume

## ⚙️ How it works

```
run.py
 ├── loads watchers.toml at startup and syncs it into the database
 └── every hour launches crawler.py as a subprocess
        └── Scrapy spiders → SQLite
```

Each crawl runs in a separate process, so the Scrapy reactor starts fresh every
time and a crashing spider cannot take down the scheduler.

> 🔄 `watchers.toml` is read **only at startup**. After editing it, restart the app
> (`docker compose restart` in Docker).

## 📋 Requirements

- 🐍 Python 3.11+ (uses `tomllib`; developed on 3.14) for local runs
- 🐳 Docker and Docker Compose for the container setup

## 🔧 Configuration

### 1. Discord webhook 🔔

Create a webhook: *Server Settings → Integrations → Webhooks → New Webhook*,
choose the target channel and copy the URL.

```bash
cp .env.example .env
```

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 2. Watchers 👀

Edit `watchers.toml`:

```toml
[[watcher]]
name = "garmin-bazos"        # unique name
site = "bazos"              # odkarla | sbazar | bazos | cyklobazar | aukro
search = "garmin hodinky"
keywords = "GPS Fenix"             # optional
```

Each `[[watcher]]` block defines one search on one marketplace.

🛡️ **Removing a watcher is safe.** If you delete a block from the file, the watcher
is only **deactivated** in the database, so an accidental edit never destroys its
data. Add it back later and it becomes active again instead of being created anew
(its stored listings are kept, so there is no flood of "new" notifications).

### 3. Optional settings 🎛️

| Variable | Default | Purpose |
|----------|---------|---------|
| `WAIT_TIME` | `3600` | ⏰ Pause between crawls, in **seconds**. |
| `DB_PATH` | see `.env.example` | 💾 Database location for **local runs only**. Ignored in Docker, where the path is fixed by the container setup. |

## 🚀 Usage

### 💻 Local

```bash
git clone git@github.com:YOUR_NAME/GoodWatcher.git
cd GoodWatcher

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run.py
```

### 🐳 Docker

```bash
git clone git@github.com:YOUR_NAME/GoodWatcher.git
cd GoodWatcher

cp .env.example .env             # fill in DISCORD_WEBHOOK_URL
# edit watchers.toml

docker compose up -d --build
docker compose logs -f           # follow the output
docker compose down              # stop
```

💾 The database is stored in a Docker volume, so your data **survives**
`docker compose down` and restarts.

## 🩺 Troubleshooting

- 🔑 **`DISCORD_WEBHOOK_URL` missing**: copy `.env.example` to `.env` and fill it in.
- 📄 **Invalid `watchers.toml`**: the app reports which entry is wrong at startup.
- 🔒 **`database is locked`**: two crawls wrote to SQLite at once. Wait and retry.
- 🕳️ **No items found**: the marketplace may have changed its layout. Check `crawler.log`.