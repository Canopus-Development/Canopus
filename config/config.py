import os
import logging
from typing import Dict, List

class Paths:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk-model-small-en-us")

class AIConfig:
    ENDPOINT = "https://models.inference.ai.azure.com"
    API_KEY = os.getenv("GITHUB_TOKEN")
    
    MODELS = {
        "gpt4": "gpt-4o",
        "o1-mini": "o1-mini",
        "llama": "Llama-3.2-90B-Vision-Instruct"
    }
    
    DEFAULT_MODEL = MODELS["gpt4"]
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    TOP_P = 1.0

class AssistantConfig:
    WAKE_WORD = "assistant"
    COMMAND_TIMEOUT = 100
    BLOCK_SIZE = 8000

class EmailConfig:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("EMAIL_SENDER")
    SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("EMAIL_RECIPIENT")

class SecurityConfig:
    SENSITIVE_COMMANDS = ["sos", "email", "settings"]
    MAX_COMMANDS_PER_MINUTE = 10
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key")
    AUTH_REQUIRED = True
    SANDBOX_ENABLED = True

class LanguageConfig:
    DEFAULT_LANGUAGE = "en-US"
    SUPPORTED_LANGUAGES = {
        "en-US": "English (US)",
        "es-ES": "Spanish",
        "fr-FR": "French",
        "de-DE": "German"
    }
    TTS_VOICES = {
        "en-US": "en-US-Standard-A",
        "es-ES": "es-ES-Standard-A",
        "fr-FR": "fr-FR-Standard-A",
        "de-DE": "de-DE-Standard-A"
    }

class CustomizationConfig:
    WAKE_WORDS = {
        "default": "Canopus",
        "custom": []  # User can add custom wake words
    }
    COMMAND_ALIASES: Dict[str, str] = {}
    PLUGIN_STATUS: Dict[str, bool] = {}  # Enabled/disabled status

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(Paths.LOGS_DIR, 'Canopus.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Create necessary directories
os.makedirs(Paths.LOGS_DIR, exist_ok=True)
os.makedirs(Paths.MODELS_DIR, exist_ok=True)

# Initialize logger
logger = logging.getLogger("Canopus")
