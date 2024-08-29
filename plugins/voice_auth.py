#TODO: Update code to even have voice profile for different users

import os
import numpy as np
from scipy.spatial.distance import euclidean
from plugins.utils import record_voice, extract_features
from config.config import VoiceAuthConfig, logger

class VoiceAuthenticator:
    def __init__(self):
        self.initial_voice_path = VoiceAuthConfig.INITIAL_VOICE_PATH
        self.new_voice_path = VoiceAuthConfig.NEW_VOICE_PATH
        self.threshold = VoiceAuthConfig.THRESHOLD

    def enroll_user(self):
        if not os.path.exists(self.initial_voice_path):
            logger.info("Enrolling user voice.")
            print("Recording initial voice. Please say 'Canopus, how are you?'.")
            record_voice(self.initial_voice_path)
            logger.info(f"User voice enrolled and saved to {self.initial_voice_path}.")
            print("Recorded voice saved to:", self.initial_voice_path)
        else:
            logger.info(f"User voice already exists at {self.initial_voice_path}.")

    def authenticate_user(self):
        logger.info("Starting authentication process...")
        print("Starting authentication process.")
        logger.info("Authenticating user voice.")
        print("Recording new voice.")
        record_voice(self.new_voice_path)
        print("Recorded voice saved to:", self.new_voice_path)
        initial_features = extract_features(self.initial_voice_path)
        new_features = extract_features(self.new_voice_path)
        distance = euclidean(initial_features, new_features)
        print("Computed distance:", distance)
        logger.debug(f"Computed distance: {distance}")
        if distance <= self.threshold:
            logger.info("Voice authentication successful.")
            print("Voice authentication successful.")
            return True  # Allow user
        else:
            logger.info("Voice authentication failed.")
            print("Voice authentication failed.")
            return False  # Deny user