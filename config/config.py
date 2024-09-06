import logging

class VoiceAuthConfig:
    INITIAL_VOICE_PATH = "models/initial_voice.wav"
    NEW_VOICE_PATH = "models/new_voice.wav"
    THRESHOLD = 39

class ObjectDetectionConfig:
    DETECT_API_URL = "Get A API URL Or See AI API Folder"


class SOSConfig:
    SENDER_EMAIL = "#Replace with your email"
    SENDER_PASSWORD = "#Replace with password"
    RECIPIENT_EMAIL = "#Replace with Email"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

class CodeGenerationConfig:
    GENERATE_API_URL = "Get A API URL Or See AI API Folder"

class InformationGeneratorConfig:
    INFO_API_URL = "Get A UPI URL Or See AI API Folder"

class SpotifyConfig:
    CLIENT_ID = "your_spotify_client_id"
    CLIENT_SECRET = "your_spotify_client_secret"
    REDIRECT_URI = "http://localhost:8888/callback"  # or your chosen redirect URI

class ChatGenerationConfig:
    CHAT_API_URL = "Get A API URL Or See AI API Folder"

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
