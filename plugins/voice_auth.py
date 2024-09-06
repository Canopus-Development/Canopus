import os
import numpy as np
from scipy.spatial.distance import euclidean
from plugins.utils import record_voice, extract_features
from config.config import VoiceAuthConfig, logger

def execute(user_command):
    logger.info("Executing voice authentication plugin.")
    authenticator = VoiceAuthenticator()

    if "enroll" in user_command:
        authenticator.enroll_user()
        return "Voice enrollment completed."
    elif "authenticate" in user_command:
        if authenticator.authenticate_user():
            return "Voice authentication successful."
        else:
            return "Voice authentication failed."
    else:
        return "Command not recognized for voice authentication."

class VoiceAuthenticator:
    def __init__(self):
        self.initial_voice_path = VoiceAuthConfig.INITIAL_VOICE_PATH
        self.new_voice_path = VoiceAuthConfig.NEW_VOICE_PATH
        self.threshold = VoiceAuthConfig.THRESHOLD

    def enroll_user(self):
        if not os.path.exists(self.initial_voice_path):
            logger.info("Enrolling user voice.")
            record_voice(self.initial_voice_path)
            logger.info(f"User voice enrolled and saved to {self.initial_voice_path}.")
        else:
            logger.info(f"User voice already exists at {self.initial_voice_path}.")

    def authenticate_user(self):
        logger.info("Starting authentication process...")
        record_voice(self.new_voice_path)
        initial_features = extract_features(self.initial_voice_path)
        new_features = extract_features(self.new_voice_path)
        distance = euclidean(initial_features, new_features)
        logger.debug(f"Computed distance: {distance}")
        return distance <= self.threshold
