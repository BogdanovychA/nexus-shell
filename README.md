# 🤖 Nexus Shell AI Agent

Telegram-бот для взаємодії з провідними мовними моделями — Gemini, ChatGPT та Claude — через єдиний інтерфейс. Кожен користувач налаштовує власний API-ключ і системний промпт.

---

## ✨ Можливості

- Підтримка трьох AI-провайдерів: **Google Gemini**, **OpenAI ChatGPT**, **Anthropic Claude**
- Персональні налаштування для кожного користувача (API-ключ + системний промпт)
- Збереження налаштувань у **Firebase Firestore**
- Кешування стану у **Redis**
- API-ключі зберігаються у **зашифрованому вигляді** (AES-128, Fernet)
- Автоматична відправка довгих відповідей як файл (обхід обмежень Telegram)
- FSM-логіка для покрокового налаштування бота

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
| `/status` | Перевірити поточні налаштування |
| `/help` | Допомога з отриманням API-ключів |

---

## 🏗 Стек

- **Python 3.14+**
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) — збереження користувачів
- [Redis](https://redis.io/) — FSM-стан
- [anthropic](https://docs.anthropic.com/) / [openai](https://platform.openai.com/docs) / [google-genai](https://ai.google.dev/) — AI-клієнти
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — конфігурація через `.env`
- [uv](https://github.com/astral-sh/uv) — менеджер залежностей

---

## ⚙️ Налаштування

### 1. Клонувати репозиторій

```bash
git clone https://github.com/your-username/nexus-shell.git
cd nexus-shell
```

### 2. Створити `.env` файл

```bash
mv .env.example .env
nano .env
```

### 3. Додати Firebase credentials

Розмісти файл `firebase-admin_sdk.json` у директорії:
```
src/secret/firebase-admin_sdk.json
```

### 4. Встановити залежності та запустити

```bash
uv run python src/main.py
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
