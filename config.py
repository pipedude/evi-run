# =============================================================================
# MAIN CONFIGURATION SETTINGS for the bot behavior and features
# =============================================================================

# REQUIRED! Enter your Telegram ID (get from @userinfobot)
ADMIN_ID = XXX

# Bot usage mode: 'private' (owner only), 'free' (public with limits), 'pay' (monetized)
TYPE_USAGE = 'private'

# Daily credit allocation for pay and free mode users
CREDITS_USER_DAILY = 500
CREDITS_ADMIN_DAILY = 5000

# Credit costs for text processing (per 1000 tokens, pay mode only)
CREDITS_INPUT_TEXT = 2
CREDITS_OUTPUT_TEXT = 8

# Credit costs for image processing (per 1000 tokens, pay mode only)
CREDITS_INPUT_IMAGE = 10
CREDITS_OUTPUT_IMAGE = 40

# Token usage warning threshold - user gets notified when exceeded
TOKENS_LIMIT_FOR_WARNING_MESSAGE = 15000

# Supported languages configuration
AVAILABLE_LANGUAGES = ['en', 'ru']
AVAILABLE_LANGUAGES_WORDS = ['English', 'Русский']
DEFAULT_LANGUAGE = 'en'
LANGUAGE_FALLBACKS = {
    'ru': ['ru', 'en'],
    'en': ['en']
}

# Application host address (do not modify)
HOST_ADDRESS = 'https://evi.run'
