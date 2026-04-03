# 🤖 Nexus Shell AI Agent

> 🌐 **Translations:** [🇺🇦 Українська](README.uk.md)

A Telegram bot for interacting with leading language models — Gemini, ChatGPT, and Claude — through a single unified interface. Each user configures their own API key and system prompt.

---

## ✨ Features

- Support for three AI providers: **Google Gemini**, **OpenAI ChatGPT**, **Anthropic Claude**
- Per-user personalized settings (API key + system prompt)
- Settings stored in **Firebase Firestore**, **PostgreSQL**, or **MongoDB** (configurable)
- State caching in **Redis**
- API keys stored **encrypted** (AES-128 via Fernet)
- Automatic sending of long responses as a file (bypasses Telegram message limits)
- FSM-based step-by-step bot configuration flow
- **Multi-language** interface support (🇺🇦 Ukrainian, 🇬🇧 English, 🇵🇱 Polish)
- **Docker-ready** — run the entire stack with a single `docker compose up -d`

---

## 🔒 Security

User API keys are encrypted before being saved to the database (AES-128 via Fernet).
The plaintext key exists only in memory during requests to the AI provider.

---

## 🛠 Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/setup` | Step-by-step setup of model, key, and prompt |
| `/model` | Change the language model |
| `/locale` | Change the interface language |
| `/status` | Check current settings |
| `/help` | Help with obtaining API keys |

---

## 🏗 Stack

- **Python 3.14+**
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- [aiogram-i18n](https://github.com/aiogram/i18n) — i18n support (Fluent)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) — user data storage *(default)*
- [SQLAlchemy](https://docs.sqlalchemy.org/) + [asyncpg](https://magicstack.github.io/asyncpg/) — PostgreSQL support *(alternative)*
- [PyMongo](https://pymongo.readthedocs.io/) — MongoDB support *(alternative)*
- [Redis](https://redis.io/) — FSM state storage
- [anthropic](https://docs.anthropic.com/) / [openai](https://platform.openai.com/docs) / [google-genai](https://ai.google.dev/) — AI clients
- [cryptography](https://cryptography.io/) — API key encryption
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — configuration via `.env`
- [uv](https://github.com/astral-sh/uv) — dependency manager

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/BogdanovychA/nexus-shell
cd nexus-shell
```

### 2. Create the `.env` file

```bash
mv .env.example .env
nano .env
```

### 3. Generate an encryption key (once)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the result to `.env`:

```env
CRYPTOGRAPHY__SECRET_KEY=your_generated_key
```

### 4. Add Firebase credentials

Place the `firebase-admin_sdk.json` file in the following directory:
```
src/secret/firebase-admin_sdk.json
```

### 5. Install dependencies and run

```bash
uv run python src/main.py
```

---

## 🗄 Storage Backend

By default the bot uses **Firebase Firestore**. As an alternative, you can switch to **PostgreSQL** or **MongoDB**.

### Switching to PostgreSQL

In your `.env` file, change the storage setting:

```env
# Default — Firebase
MAIN__GLOBAL_STORAGE=Firebase

# Alternative — PostgreSQL
MAIN__GLOBAL_STORAGE=PostgreSQL
```

Then fill in the PostgreSQL credentials in the same `.env` file:

```env
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

Initialize the database schema (creates all tables):

```bash
uv run python src/storage/sql_alchemy/models.py
```

### Running with Docker Compose (PostgreSQL)

For convenience, a `docker-compose.yml` is included that starts PostgreSQL, pgAdmin, Redis, and RedisInsight with a single command:

```bash
docker compose up -d
```

| Service | URL | Description |
|---|---|---|
| PostgreSQL | `localhost:${POSTGRES_PORT}` | Main database |
| pgAdmin | `http://localhost:8033` | PostgreSQL web UI |
| Redis | `localhost:${REDIS__PORT}` | FSM state storage |
| RedisInsight | `http://localhost:5541` | Redis web UI |

> **Note:** Firebase credentials are still required when `MAIN__GLOBAL_STORAGE=Firebase` (the default). If you switch to PostgreSQL, the `firebase-admin_sdk.json` file and Firebase Admin SDK are not needed.

---

### Switching to MongoDB

In your `.env` file, change the storage setting:

```env
MAIN__GLOBAL_STORAGE=MongoDB
```

MongoDB supports two connection modes depending on where your database is hosted.

#### Option 1 — Docker container (local)

Fill in the individual connection fields:

```env
MONGO_INITDB_ROOT_SERVER=localhost
MONGO_INITDB_ROOT_PORT=27017
MONGO_INITDB_ROOT_USERNAME=your_username
MONGO_INITDB_ROOT_PASSWORD=your_password
```

Leave `MONGO_INITDB_ROOT_URI` commented out — if it is set, it takes priority over the individual fields.

#### Option 2 — Cloud database (e.g. MongoDB Atlas)

Set the connection string directly via `MONGO_INITDB_ROOT_URI`:

```env
MONGO_INITDB_ROOT_URI="mongodb+srv://your_username:your_password@your_cluster.your_server/?appName=your_app_name"
```

The individual fields (`SERVER`, `PORT`, `USERNAME`, `PASSWORD`) are ignored when `URI` is provided.

### Running with Docker Compose (MongoDB)

```bash
docker compose up -d
```

| Service | URL | Description |
|---|---|---|
| MongoDB | `localhost:${MONGO_INITDB_ROOT_PORT}` | Main database |
| Mongo Express | `http://localhost:8082` | MongoDB web UI |
| Redis | `localhost:${REDIS__PORT}` | FSM state storage |
| RedisInsight | `http://localhost:5541` | Redis web UI |

To log in to Mongo Express, use the `ME_CONFIG_BASICAUTH_USERNAME` / `ME_CONFIG_BASICAUTH_PASSWORD` values from your `.env` file.

> **Note:** When using a cloud database, there is no need to start the MongoDB container. You can bring up only the Redis services: `docker compose up db-redis redisinsight -d`.

---

## 🐳 Deploy with Docker

The `docker-compose.yml` includes a `bot` service that builds and runs the bot alongside all infrastructure (Redis, PostgreSQL / MongoDB).

### 1. Prepare the `.env` file

```bash
mv .env.example .env
nano .env
```

### 2. Firebase credentials (if using Firebase)

Place the `firebase-admin_sdk.json` file in:
```
docker_data/secret/firebase-admin_sdk.json
```

It will be mounted into the container at `src/secret/firebase-admin_sdk.json` automatically.

> If you use PostgreSQL or MongoDB as storage, this file is not needed.

### 3. Build and start all services

```bash
docker compose up -d --build
```

| Service | URL | Description |
|---|---|---|
| Bot | — | Telegram bot |
| PostgreSQL | `localhost:${POSTGRES_PORT}` | Main database (PostgreSQL) |
| pgAdmin | `http://localhost:8033` | PostgreSQL web UI |
| MongoDB | `localhost:${MONGO_INITDB_ROOT_PORT}` | Main database (MongoDB) |
| Mongo Express | `http://localhost:8082` | MongoDB web UI |
| Redis | `localhost:${REDIS__PORT}` | FSM state storage |
| RedisInsight | `http://localhost:5541` | Redis web UI |

> You don't need to start all services at once. For example, if you use PostgreSQL, the MongoDB container can be left unused — it won't affect the bot.

### 4. View logs

```bash
docker compose logs -f bot
```

---

## 🚀 Deploy as a systemd service

```ini
[Unit]
Description=Telegram Bot | Nexus Shell AI Agent
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/nexus-shell
ExecStart=/home/your_user/.local/bin/uv run python src/main.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/nexus-shell.log
StandardError=append:/var/log/nexus-shell.log

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable nexus-shell
systemctl start nexus-shell
journalctl -u nexus-shell -f
```

---

## 🔑 Getting API Keys

- **Gemini** — [Google AI Studio](https://aistudio.google.com/app/api-keys)
- **ChatGPT** — [OpenAI Platform](https://platform.openai.com/account/api-keys)
- **Claude** — [Anthropic Console](https://platform.claude.com/settings/keys)

---

## Links

* [Bot on Telegram](https://t.me/NexusShellBot)
* [Support the project](https://send.monobank.ua/jar/8Qn1woNnC7)
