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
    SENDER_EMAIL = "#Replace with your email"
    SENDER_PASSWORD = "#Replace with password"
    RECIPIENT_EMAIL = "#Replace with Email"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

class CodeGenerationConfig:
    GENERATE_API_URL = "Get A API URL"

class InformationRetrievalConfig:
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    GEMINI_API_KEY = "Get Token"

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
