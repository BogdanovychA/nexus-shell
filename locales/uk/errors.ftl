# Загальні помилки API
error-no-token =
    API-ключ (токен) { $name } відсутній у налаштуваннях.
    Налаштуй: /setup
error-invalid-token =
    API-ключ (токен) { $name } недійсний або термін його дії закінчився.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-forbidden-chars =
    API-ключ (токен) { $name } містить заборонені символи.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-limit-exhausted =
    Ти вичерпав ліміт за цим API-ключем (токеном).
    Спробуй пізніше або налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-access-denied =
    Доступ за цим API-ключем (токеном) заборонений.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-token-format =
    Некоректний формат токена.

    { $error }

# Непередбачувані помилки
error-unexpected =
    { $info-forward-text }
    Неочікувана помилка при зверненні до { $name }:

    { $error }
error-telegram-too-long = Відповідь занадто довга. Надсилаю файлом.
error-client-api =
    { $info-forward-text }
    Помилка клієнта { $name } (API)