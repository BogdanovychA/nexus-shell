# 🤖 Nexus Shell AI Agent

> 🌐 **Translations:** [🇺🇦 Українська](README.uk.md)

A Telegram bot for interacting with leading language models — Gemini, ChatGPT, and Claude — through a single unified interface. Each user configures their own API key and system prompt.

---

## ✨ Features

- Support for three AI providers: **Google Gemini**, **OpenAI ChatGPT**, **Anthropic Claude**
- Per-user personalized settings (API key + system prompt)
- Settings stored in **Firebase Firestore** or **PostgreSQL** (configurable)
- State caching in **Redis**
- API keys stored **encrypted** (AES-128 via Fernet)
- Automatic sending of long responses as a file (bypasses Telegram message limits)
- FSM-based step-by-step bot configuration flow
- **Multi-language** interface support (🇺🇦 Ukrainian, 🇬🇧 English, 🇵🇱 Polish)

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

By default the bot uses **Firebase Firestore**. As an alternative, you can switch to **PostgreSQL**.

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

### Running with Docker Compose

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
