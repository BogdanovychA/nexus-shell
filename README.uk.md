# 🤖 Nexus Shell AI Agent

> 🌐 **Переклади:** [🇬🇧 English](README.md)

Telegram-бот для взаємодії з провідними мовними моделями — Gemini, ChatGPT та Claude — через єдиний інтерфейс. Кожен користувач налаштовує власний API-ключ і системний промпт.

---

## ✨ Можливості

- Підтримка трьох AI-провайдерів: **Google Gemini**, **OpenAI ChatGPT**, **Anthropic Claude**
- Персональні налаштування для кожного користувача (API-ключ + системний промпт)
- Збереження налаштувань у **Firebase Firestore**, **PostgreSQL** або **MongoDB** (на вибір)
- Кешування стану у **Redis**
- API-ключі зберігаються у **зашифрованому вигляді** (AES-128, Fernet)
- Автоматична відправка довгих відповідей як файл (обхід обмежень Telegram)
- FSM-логіка для покрокового налаштування бота
- Підтримка **кількох мов** інтерфейсу (🇺🇦 Українська, 🇬🇧 English, 🇵🇱 Polski)
- **Docker-ready** — весь стек піднімається однією командою `docker compose up -d`

---

## 🔒 Безпека

API-ключі користувачів шифруються перед збереженням у базі даних (AES-128 через Fernet).
У відкритому вигляді ключ існує лише в пам'яті під час запиту до AI-провайдера.

---

## 🛠 Команди

| Команда | Опис |
|---|---|
| `/start` | Запустити бота |
| `/setup` | Покрокове налаштування моделі, ключа та промпту |
| `/model` | Змінити мовну модель |
| `/locale` | Змінити мову інтерфейсу |
| `/status` | Перевірити поточні налаштування |
| `/help` | Допомога з отриманням API-ключів |

---

## 🏗 Стек

- **Python 3.14+**
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- [aiogram-i18n](https://github.com/aiogram/i18n) — багатомовність (Fluent)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) — збереження користувачів *(за замовчуванням)*
- [SQLAlchemy](https://docs.sqlalchemy.org/) + [asyncpg](https://magicstack.github.io/asyncpg/) — підтримка PostgreSQL *(альтернатива)*
- [PyMongo](https://pymongo.readthedocs.io/) — підтримка MongoDB *(альтернатива)*
- [Redis](https://redis.io/) — FSM-стан
- [anthropic](https://docs.anthropic.com/) / [openai](https://platform.openai.com/docs) / [google-genai](https://ai.google.dev/) — AI-клієнти
- [cryptography](https://cryptography.io/) — шифрування API-ключів
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — конфігурація через `.env`
- [uv](https://github.com/astral-sh/uv) — менеджер залежностей

---

## ⚙️ Налаштування

### 1. Клонувати репозиторій

```bash
git clone https://github.com/BogdanovychA/nexus-shell
cd nexus-shell
```

### 2. Створити `.env` файл

```bash
mv .env.example .env
nano .env
```

### 3. Згенерувати ключ шифрування (один раз)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Додати результат у `.env`:

```env
CRYPTOGRAPHY__SECRET_KEY=your_generated_key
```

### 4. Додати Firebase credentials

Розмісти файл `firebase-admin_sdk.json` у директорії:
```
src/secret/firebase-admin_sdk.json
```

### 5. Встановити залежності та запустити

```bash
uv run python src/main.py
```

---

## 🗄 Сховище даних

За замовчуванням бот використовує **Firebase Firestore**. Як альтернативу можна підключити **PostgreSQL** або **MongoDB**.

### Перемикання на PostgreSQL

У файлі `.env` змінити налаштування сховища:

```env
# За замовчуванням — Firebase
MAIN__GLOBAL_STORAGE=Firebase

# Альтернатива — PostgreSQL
MAIN__GLOBAL_STORAGE=PostgreSQL
```

Заповнити облікові дані PostgreSQL у тому ж `.env`:

```env
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

Ініціалізувати схему бази даних (створює всі таблиці):

```bash
uv run python src/storage/sql_alchemy/models.py
```

### Запуск через Docker Compose (PostgreSQL)

Для зручності в репозиторії є `docker-compose.yml`, який одною командою піднімає PostgreSQL, pgAdmin, Redis та RedisInsight:

```bash
docker compose up -d
```

| Сервіс | URL | Опис |
|---|---|---|
| PostgreSQL | `localhost:${POSTGRES_PORT}` | Основна база даних |
| pgAdmin | `http://localhost:8033` | Веб-інтерфейс PostgreSQL |
| Redis | `localhost:${REDIS__PORT}` | Збереження FSM-стану |
| RedisInsight | `http://localhost:5541` | Веб-інтерфейс Redis |

> **Примітка:** Firebase credentials потрібні лише при `MAIN__GLOBAL_STORAGE=Firebase` (за замовчуванням). При переході на PostgreSQL файл `firebase-admin_sdk.json` та Firebase Admin SDK не потрібні.

---

### Перемикання на MongoDB

У файлі `.env` змінити налаштування сховища:

```env
MAIN__GLOBAL_STORAGE=MongoDB
```

MongoDB підтримує два режими підключення залежно від того, де розгорнута база даних.

#### Варіант 1 — Docker-контейнер (локально)

Заповнити окремі поля підключення:

```env
MONGO_INITDB_ROOT_SERVER=localhost
MONGO_INITDB_ROOT_PORT=27017
MONGO_INITDB_ROOT_USERNAME=your_username
MONGO_INITDB_ROOT_PASSWORD=your_password
```

`MONGO_INITDB_ROOT_URI` залишати закоментованим — якщо він заданий, він має пріоритет над окремими полями.

#### Варіант 2 — Хмарна БД (наприклад, MongoDB Atlas)

Передати готовий рядок підключення через `MONGO_INITDB_ROOT_URI`:

```env
MONGO_INITDB_ROOT_URI="mongodb+srv://your_username:your_password@your_cluster.your_server/?appName=your_app_name"
```

Окремі поля (`SERVER`, `PORT`, `USERNAME`, `PASSWORD`) при цьому ігноруються.

### Запуск через Docker Compose (MongoDB)

```bash
docker compose up -d
```

| Сервіс | URL | Опис |
|---|---|---|
| MongoDB | `localhost:${MONGO_INITDB_ROOT_PORT}` | Основна база даних |
| Mongo Express | `http://localhost:8082` | Веб-інтерфейс MongoDB |
| Redis | `localhost:${REDIS__PORT}` | Збереження FSM-стану |
| RedisInsight | `http://localhost:5541` | Веб-інтерфейс Redis |

Для входу в Mongo Express використовувати значення `ME_CONFIG_BASICAUTH_USERNAME` / `ME_CONFIG_BASICAUTH_PASSWORD` з файлу `.env`.

> **Примітка:** При використанні хмарної БД піднімати MongoDB-контейнер не потрібно — достатньо запустити лише Redis: `docker compose up db-redis redisinsight -d`.

---

## 🐳 Деплой через Docker

`docker-compose.yml` містить сервіс `bot`, який збирає і запускає бота разом з усією інфраструктурою (Redis, PostgreSQL / MongoDB).

### 1. Підготувати `.env` файл

```bash
mv .env.example .env
nano .env
```

### 2. Firebase credentials (якщо використовується Firebase)

Розмісти файл `firebase-admin_sdk.json` у директорії:
```
docker_data/secret/firebase-admin_sdk.json
```

Він буде автоматично змонтований у контейнер за шляхом `src/secret/firebase-admin_sdk.json`.

> Якщо як сховище використовується PostgreSQL або MongoDB — цей файл не потрібен.

### 3. Зібрати та запустити всі сервіси

```bash
docker compose up -d --build
```

| Сервіс | URL | Опис |
|---|---|---|
| Bot | — | Telegram-бот |
| PostgreSQL | `localhost:${POSTGRES_PORT}` | Основна БД (PostgreSQL) |
| pgAdmin | `http://localhost:8033` | Веб-інтерфейс PostgreSQL |
| MongoDB | `localhost:${MONGO_INITDB_ROOT_PORT}` | Основна БД (MongoDB) |
| Mongo Express | `http://localhost:8082` | Веб-інтерфейс MongoDB |
| Redis | `localhost:${REDIS__PORT}` | Збереження FSM-стану |
| RedisInsight | `http://localhost:5541` | Веб-інтерфейс Redis |

> Піднімати всі сервіси одночасно не обов'язково. Наприклад, якщо використовується PostgreSQL, MongoDB-контейнер просто не буде задіяний — на роботу бота це не впливає.

### 4. Переглянути логи

```bash
docker compose logs -f bot
```

---

## 🚀 Деплой як systemd-сервіс

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

## 🔑 Отримання API-ключів

- **Gemini** — [Google AI Studio](https://aistudio.google.com/app/api-keys)
- **ChatGPT** — [OpenAI Platform](https://platform.openai.com/account/api-keys)
- **Claude** — [Anthropic Console](https://platform.claude.com/settings/keys)

---

## Лінки

* [Бот в Telegram](https://t.me/NexusShellBot)
* [Підтримати проєкт](https://send.monobank.ua/jar/8Qn1woNnC7)
