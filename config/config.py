import os
import logging

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

class VoiceConfig:
    SAMPLE_RATE = 16000
    CHANNELS = 1
    DURATION = 5

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
