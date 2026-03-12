# Загальні помилки API
error-no-token =
    API-ключ { $name } відсутній у налаштуваннях.
    Налаштуй: /setup
error-invalid-token =
    API-ключ { $name } недійсний або термін його дії закінчився.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-forbidden-chars =
    API-ключ { $name } містить заборонені символи.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-limit-exhausted =
    Ти вичерпав ліміт за API-ключем для { $name }.
    Спробуй пізніше або налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-access-denied =
    Доступ за API-ключем для { $name } заборонений.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }
error-token-format =
    Некоректний формат API-ключа для { $name }.
    Налаштуй інший: /setup

    Отримати можна тут: { $token_url }

    { $error }

# Непередбачувані помилки
error-unexpected =
    Неочікувана помилка при зверненні до { $name }:

    { $error }
error-client-api = Помилка клієнта { $name } (API)