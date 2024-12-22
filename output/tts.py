import pyttsx3
from threading import Thread
import queue

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self._setup_voice()
        
    def _setup_voice(self):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        
    def start(self):
        self.is_speaking = True
        Thread(target=self._speech_loop).start()
        
    def stop(self):
        self.is_speaking = False
        self.engine.stop()
        
    def speak(self, text: str):
        self.speech_queue.put(text)
        
    def _speech_loop(self):
        while self.is_speaking:
            try:
                text = self.speech_queue.get(timeout=1)
                self.engine.say(text)
                self.engine.runAndWait()
            except queue.Empty:
                continue
