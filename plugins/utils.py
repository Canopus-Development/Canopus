import cv2
import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
from config.config import logger

def record_voice(file_path, duration=5):
    logger.info(f"Recording voice for {duration} seconds.")
    samplerate = 44100
    data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='float64')
    sd.wait()  # Wait until recording is finished
    sf.write(file_path, data, samplerate)
    logger.info(f"Voice recorded and saved to {file_path}.")

def extract_features(file_path):
    logger.info(f"Extracting features from {file_path}.")
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

def capture_image():
    logger.info("Capturing image from camera.")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        image_path = "user_image.jpg"
        cv2.imwrite(image_path, frame)
        logger.info(f"Image captured and saved to {image_path}.")
        return image_path
    logger.error("Failed to capture image.")
    return None
