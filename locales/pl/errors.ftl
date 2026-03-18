# General API errors
error-no-token =
    Klucz API { $name } nie jest skonfigurowany.
    Skonfiguruj go: /setup
error-invalid-token =
    Klucz API { $name } jest nieprawidłowy lub wygasł.
    Skonfiguruj inny: /setup

    Możesz go uzyskać tutaj: { $token_url }
error-forbidden-chars =
    Klucz API { $name } zawiera niedozwolone znaki.
    Skonfiguruj inny: /setup

    Możesz go uzyskać tutaj: { $token_url }
error-limit-exhausted =
    Wyczerpałeś limit klucza API { $name }.
    Spróbuj ponownie później lub skonfiguruj inny: /setup

    Możesz go uzyskać tutaj: { $token_url }
error-access-denied =
    Dostęp dla klucza API { $name } został odrzucony.
    Skonfiguruj inny: /setup

    Możesz go uzyskać tutaj: { $token_url }
error-token-format =
    Nieprawidłowy format klucza API dla { $name }.
    Skonfiguruj inny: /setup

    Możesz go uzyskać tutaj: { $token_url }

    { $error }
error-model-overloaded =
    Serwery { $name } są obecnie przeciążone z powodu dużego natężenia ruchu.
    Spróbuj ponownie za kilka minut.
# Unexpected errors
error-unexpected =
    Nieoczekiwany błąd podczas dostępu do { $name }:

    { $error }
error-client-api = Błąd klienta { $name } (API)
