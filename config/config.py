import logging

class VoiceAuthConfig:
    INITIAL_VOICE_PATH = "models/initial_voice.wav"
    NEW_VOICE_PATH = "models/new_voice.wav"
    THRESHOLD = 39

class ObjectDetectionConfig:
    PROTOTXT_PATH = "models/deploy.prototxt"
    MODEL_PATH = "models/mobilenet.caffemodel"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

class SOSConfig:
    SENDER_EMAIL = "Gamecooler3009@gmail.com"
    SENDER_PASSWORD = "pebq jgty qdvd ccpg"
    RECIPIENT_EMAIL = "pradyumn.tandon@hotmail.com"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

class CodeGenerationConfig:
    GENERATE_API_URL = "http://144.24.97.63:8000/generate"

class InformationRetrievalConfig:
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    GEMINI_API_KEY = "AIzaSyAIlXvxOs1mY7gUuwEgjPamLUhht9qS3Lw"

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
            'filename': 'logs/ai_assistant.log',
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

logger = logging.getLogger("ai_assistant")
