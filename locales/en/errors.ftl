# General API errors
error-no-token =
    The { $name } API key is missing from settings.
    Configure it: /setup
error-invalid-token =
    The { $name } API key is invalid or has expired.
    Configure another one: /setup

    You can get one here: { $token_url }
error-forbidden-chars =
    The { $name } API key contains forbidden characters.
    Configure another one: /setup

    You can get one here: { $token_url }
error-limit-exhausted =
    You have exhausted the limit for the { $name } API key.
    Try again later or configure another one: /setup

    You can get one here: { $token_url }
error-access-denied =
    Access for the { $name } API key is denied.
    Configure another one: /setup

    You can get one here: { $token_url }
error-token-format =
    Invalid API key format for { $name }.
    Configure another one: /setup

    You can get one here: { $token_url }

    { $error }
error-model-overloaded =
    The { $name } servers are currently overloaded due to high demand.
    Please try again in a few minutes.
# Unexpected errors
error-unexpected =
    Unexpected error when accessing { $name }:

    { $error }
error-client-api = { $name } client error (API)
