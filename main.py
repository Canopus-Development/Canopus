import os
import json
import queue
import signal
import threading
import time
from typing import List, Optional
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import importlib
import pyttsx3
from dataclasses import dataclass
from config.config import logger, AssistantConfig, Paths, VoiceConfig

@dataclass
class CommandResult:
    success: bool
    message: str
    plugin_name: Optional[str] = None
    error: Optional[Exception] = None

class CommandProcessor:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.plugins = self.load_plugins()
        self.running = True
        self.health_check_interval = 60  # seconds

    def load_plugins(self) -> dict:
        plugins = {}
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    module = importlib.import_module(f"plugins.{filename[:-3]}")
                    if hasattr(module, "execute"):
                        plugins[filename[:-3]] = module
                        logger.info(f"Loaded plugin: {filename[:-3]}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {filename}: {e}")
        return plugins

    def process_command(self, command: str) -> CommandResult:
        try:
            # Priority plugins (e.g., SOS)
            priority_plugins = ["sos_command"]
            for plugin_name in priority_plugins:
                if plugin_name in self.plugins:
                    try:
                        response = self.plugins[plugin_name].execute(command)
                        if response:
                            return CommandResult(True, response, plugin_name)
                    except Exception as e:
                        logger.error(f"Error in priority plugin {plugin_name}: {e}")

            # Then try other plugins
            for plugin_name, plugin in self.plugins.items():
                if plugin_name not in priority_plugins:
                    try:
                        response = plugin.execute(command)
                        if response:
                            return CommandResult(True, response, plugin_name)
                    except Exception as e:
                        logger.error(f"Error in plugin {plugin_name}: {e}")

            return CommandResult(False, "Command not recognized", None)
        except Exception as e:
            return CommandResult(False, "Error processing command", None, e)

class SpeechHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.audio_queue = queue.Queue()
        self.command_processor = CommandProcessor()
        self.setup_voice_recognition()
        self.running = True

    def setup_voice_recognition(self):
        if not os.path.exists(Paths.VOSK_MODEL_PATH):
            raise RuntimeError(f"Vosk model not found at {Paths.VOSK_MODEL_PATH}")
        
        self.model = Model(Paths.VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, VoiceConfig.SAMPLE_RATE)
        
        self.stream = sd.RawInputStream(
            samplerate=VoiceConfig.SAMPLE_RATE,
            blocksize=AssistantConfig.BLOCK_SIZE,
            dtype="int16",
            channels=VoiceConfig.CHANNELS,
            callback=self._audio_callback
        )

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(bytes(indata))

    def speak_text(self, text: str):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")

    def listen_for_wake_word(self) -> bool:
        try:
            with self.stream:
                while self.running:
                    data = self.audio_queue.get(timeout=1)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").lower()
                        if AssistantConfig.WAKE_WORD in text:
                            return True
            return False
        except queue.Empty:
            return False
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            return False

    def get_command(self) -> Optional[str]:
        try:
            with self.stream:
                self.recognizer.Reset()
                command_text = ""
                timeout = 0
                
                while timeout < AssistantConfig.COMMAND_TIMEOUT and self.running:
                    data = self.audio_queue.get(timeout=1)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        command_text = result.get("text", "").lower()
                        if command_text:
                            return command_text
                    timeout += 1
                
                return None
        except Exception as e:
            logger.error(f"Error getting command: {e}")
            return None

    def cleanup(self):
        self.running = False
        try:
            self.stream.stop()
            self.stream.close()
            self.engine.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class Assistant:
    def __init__(self):
        self.speech_handler = SpeechHandler()
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        logger.info("Shutdown signal received")
        self.running = False
        self.speech_handler.cleanup()

    def run(self):
        logger.info("AI Assistant started. Waiting for wake word...")
        self.speech_handler.speak_text("AI Assistant is ready")

        try:
            while self.running:
                if self.speech_handler.listen_for_wake_word():
                    self.speech_handler.speak_text("How can I help?")
                    
                    command = self.speech_handler.get_command()
                    if not command:
                        continue

                    logger.info(f"Command received: {command}")

                    if command in ["exit", "quit", "shutdown"]:
                        self.speech_handler.speak_text("Goodbye!")
                        break

                    result = self.speech_handler.command_processor.process_command(command)
                    if result.success:
                        self.speech_handler.speak_text(result.message)
                    else:
                        self.speech_handler.speak_text("I didn't understand that command")

        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        logger.info("Cleaning up resources...")
        self.speech_handler.cleanup()
        logger.info("Cleanup complete")

def main():
    try:
        assistant = Assistant()
        assistant.run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
