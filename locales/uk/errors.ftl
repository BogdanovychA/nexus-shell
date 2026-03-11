# Загальні помилки API
error-no-token = API-ключ (токен) { $name } відсутній у налаштуваннях.{"\n"}Налаштуй: /setup
error-invalid-token = API-ключ (токен) { $name } недійсний або термін його дії закінчився.{"\n"}Налаштуй інший: /setup{"\n\n"}Отримати можна тут: { $token_url }
error-forbidden-chars = API-ключ (токен) { $name } містить заборонені символи.{"\n"}Налаштуй інший: /setup{"\n\n"}Отримати можна тут: { $token_url }
error-limit-exhausted = Ти вичерпав ліміт за цим API-ключем (токеном).{"\n"}Спробуй пізніше або налаштуй інший: /setup{"\n\n"}Отримати можна тут: { $token_url }
error-access-denied = Доступ за цим API-ключем (токеном) заборонений.{"\n"}Налаштуй інший: /setup{"\n\n"}Отримати можна тут: { $token_url }
error-token-format = Некоректний формат токена.{"\n\n"}{ $error }

# Непередбачувані помилки
error-unexpected = { $forward_text }{"\n"}Неочікувана помилка при зверненні до { $name }:{"\n\n"}{ $error }
error-telegram-too-long = Відповідь занадто довга. Надсилаю файлом.
error-client-api = { $forward_text }{"\n"}Помилка клієнта { $name } (API)