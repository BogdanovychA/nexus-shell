# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the bot:**
```bash
uv run python src/main.py
```

**Run all tests:**
```bash
uv run pytest tests/
```

**Run a single test file:**
```bash
uv run pytest tests/test_ai_api_by_pytest.py
```

**Run a specific test:**
```bash
uv run pytest tests/test_ai_api_by_pytest.py::test_ai_queries
```

**Run tests via unittest:**
```bash
uv run python -m unittest tests/test_ai_api_by_unittest.py
```

**Lint / format:**
```bash
uv run black src/
uv run isort src/
```

**Initialize PostgreSQL schema (run once):**
```bash
uv run python src/storage/sql_alchemy/models.py
```

**Generate a Fernet encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Docker — full stack:**
```bash
docker compose up -d
docker compose logs -f bot
```

## Project structure

```
src/
├── main.py               # Entry point — wires bot, dispatcher, middleware
├── models.py             # Pydantic models: User, AISettings, FSM state groups
├── resolvers.py          # All Telegram handlers (single aiogram Router)
├── ai/
│   ├── abstract.py       # AIModel ABC — query(i18n, token, global_prompt, local_prompt) -> str
│   ├── claude.py         # Anthropic Claude implementation
│   ├── chat_gpt.py       # OpenAI ChatGPT implementation
│   └── gemini.py         # Google Gemini implementation
├── config/
│   ├── bot.py            # Main bot config (base_dir, default_locale, MAIN__GLOBAL_STORAGE)
│   ├── encryption.py     # CRYPTOGRAPHY__SECRET_KEY
│   ├── firebase.py       # Firebase SDK path + collection settings (no env vars, BaseModel)
│   ├── mongo.py          # MONGO_INITDB_ROOT_* settings
│   ├── postgres.py       # POSTGRES_* settings
│   ├── redis.py          # REDIS__* + KEY_BUILDER__* settings
│   └── telegram.py       # TELEGRAM__TOKEN, TELEGRAM__ADMIN_ID
├── storage/
│   ├── abstract.py       # StorageManager ABC + PostgresStorage / FirebaseStorage / MongoStorage
│   ├── firebase.py       # FirebaseManager (sync, firebase-admin SDK)
│   ├── mongo.py          # MongoManager (sync, pymongo)
│   └── sql_alchemy/
│       ├── models.py     # ORM: users + ai_settings tables; run directly to init schema
│       └── postgresql.py # PostgresManager (async, SQLAlchemy + asyncpg)
├── utils/
│   ├── constants.py      # Provider URL constants (CLAUDE_URL, CHATGPT_URL, GEMINI_URL)
│   ├── encryption.py     # Fernet encrypt/decrypt helpers
│   ├── locale_manager.py # LocaleManager — aiogram-i18n integration, LANGUAGES list
│   └── utils.py          # flatten_dict(), create_user_instance() and other shared helpers
└── secret/               # Excluded from git and Docker image (see .gitignore / .dockerignore)
    └── firebase-admin_sdk.json  # Firebase credentials (local runs only)
```

## Architecture

The bot entry point is `src/main.py`. It wires together three independent subsystems — storage, i18n, and AI clients — and passes them to the aiogram `Dispatcher` as named dependencies available to all handlers.

### Storage subsystem (`src/storage/`)

`storage/abstract.py` defines the `StorageManager` ABC with methods: `save_user`, `load_user`, `load_user_data`, `update_user_data`, `update_ai_settings`, `load_ai_settings`, `close`. Three concrete implementations:

- **`PostgresStorage`** — fully async via SQLAlchemy + asyncpg. ORM models in `sql_alchemy/models.py` define two tables: `users` and `ai_settings`.
- **`FirebaseStorage`** — synchronous `FirebaseManager` wrapped with `asyncio.to_thread()`. Uses `merge=True` on all writes (upsert semantics). Firebase Admin SDK is initialized once via `firebase_admin.get_app()` guard.
- **`MongoStorage`** — synchronous `MongoManager` (pymongo `MongoClient`) wrapped with `asyncio.to_thread()`. Uses `_id = user_id` as document key, `update_one(..., upsert=True)`. Nested dicts are flattened with `utils.flatten_dict()` before writes.

The active backend is chosen at startup via `MAIN__GLOBAL_STORAGE` env var (`Firebase` / `PostgreSQL` / `MongoDB`).

### AI subsystem (`src/ai/`)

`ai/abstract.py` defines the `AIModel` ABC with a single `async query(i18n, token, global_prompt, local_prompt) -> str` method and a `clean_token()` static helper. Each provider implements it and returns either the AI response text or an i18n error key string.

Active models (hardcoded per provider — do not change without testing):
- **Claude** — `claude-haiku-4-5-20251001` (alternatives commented in source: `claude-sonnet-4-5-20250929`, `claude-opus-4-20250812`, `claude-sonnet-4-20250514`)
- **ChatGPT** — `gpt-4o` (alternatives commented: `gpt-4-turbo`, `gpt-3.5-turbo`)
- **Gemini** — `gemini-2.5-flash` (alternative commented: `gemini-2.5-pro`)

Error handling per provider maps provider-specific exceptions to i18n keys: `error-no-token`, `error-invalid-token`, `error-forbidden-chars`, `error-balance-is-low`, `error-limit-exhausted`, `error-model-overloaded`, `error-client-api`, `error-unexpected`.

### FSM flow

User state is managed by aiogram's FSM backed by Redis. Two state groups are defined in `src/models.py`:
- `AISetup` — sequential setup wizard: `waiting_for_model` → `waiting_for_token` → `waiting_for_prompt`
- `Work` — operational states: `ready` / `not_ready`

All Telegram command and message handlers live in `src/resolvers.py` (single router, registered in `main.py`).

### Config (`src/config/`)

Each subsystem has its own pydantic-settings module. All settings load from `.env` using double-underscore namespace separators. Key env var prefixes:

| Module | Prefix | Notes |
|---|---|---|
| `bot.py` | `MAIN__` | `GLOBAL_STORAGE`, `DEFAULT_LOCALE` |
| `redis.py` | `REDIS__`, `KEY_BUILDER__` | Nested via `env_nested_delimiter="__"` |
| `telegram.py` | `TELEGRAM__` | `TOKEN`, `ADMIN_ID` |
| `encryption.py` | `CRYPTOGRAPHY__` | `SECRET_KEY` |
| `postgres.py` | `POSTGRES_` | Single underscore prefix |
| `mongo.py` | `MONGO_INITDB_ROOT_` | `SERVER`, `PORT`, `USERNAME`, `PASSWORD`, `URI` |
| `firebase.py` | — | `BaseModel`, no env vars — path hardcoded relative to `base_dir` |

See `.env.example` for all required variables.

### i18n

Translations use Fluent format (`.ftl` files) located in `locales/{locale}/`. Supported locales: `en`, `uk`, `pl`. The `LocaleManager` in `src/utils/locale_manager.py` integrates with `aiogram-i18n` middleware. The default locale is set in `src/config/bot.py`. `raise_key_error=False` — missing keys silently fall back to the key name itself.

### Security

User API keys are encrypted with Fernet (AES-128) before being written to the database. Encryption/decryption utilities are in `src/utils/encryption.py`. The secret key comes from `CRYPTOGRAPHY__SECRET_KEY` in `.env`.

**Firebase credentials placement:**
- Local run (without Docker): `src/secret/firebase-admin_sdk.json`
- Docker run: `docker_data/secret/firebase-admin_sdk.json` — mounted into the container at `src/secret/`

Both paths are excluded from git (`.gitignore`) and from the Docker image (`.dockerignore`).

### Tests (`tests/`)

Two parallel test suites cover AI provider error handling — same cases, different frameworks:
- `test_ai_api_by_pytest.py` — pytest + `pytest-asyncio`, parametrized
- `test_ai_api_by_unittest.py` — `unittest.IsolatedAsyncioTestCase`

Both mock `I18nContext` and assert that invalid/empty tokens return the correct i18n error keys without making real API calls.
