import os
import json
import queue
import signal
import threading
import time
import numpy as np
from typing import List, Optional
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import importlib
import pyttsx3
from dataclasses import dataclass
from config.config import logger, AssistantConfig, Paths, SecurityConfig, LanguageConfig, CustomizationConfig, VoiceConfig
import hashlib
import time
from cryptography.fernet import Fernet
from typing import Dict, Optional
from datetime import datetime, timedelta

@dataclass
class CommandResult:
    success: bool
    message: str
    plugin_name: Optional[str] = None
    error: Optional[Exception] = None

class RateLimiter:
    def __init__(self, max_commands: int, time_window: int):
        self.max_commands = max_commands
        self.time_window = time_window
        self.commands = []

    def can_execute(self) -> bool:
        now = datetime.now()
        self.commands = [t for t in self.commands 
                        if now - t < timedelta(seconds=self.time_window)]
        if len(self.commands) < self.max_commands:
            self.commands.append(now)
            return True
        return False

class SecurityManager:
    def __init__(self):
        # Use the key directly without encoding
        self.cipher_suite = Fernet(SecurityConfig.ENCRYPTION_KEY)
        self.rate_limiter = RateLimiter(
            SecurityConfig.MAX_COMMANDS_PER_MINUTE, 60
        )

    def encrypt_data(self, data: str) -> bytes:
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, data: bytes) -> str:
        return self.cipher_suite.decrypt(data).decode()

class CommandProcessor:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.plugins = self.load_plugins()
        self.running = True
        self.health_check_interval = 60  # seconds
        self.command_history = []
        self.max_history = 100
        self.plugin_stats = {}
        self.security_manager = SecurityManager()
        self.last_command = None
        self.command_confirmed = False

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

    def requires_confirmation(self, command: str) -> bool:
        return any(cmd in command.lower() 
                  for cmd in SecurityConfig.SENSITIVE_COMMANDS)

    def process_command(self, command: str) -> CommandResult:
        try:
            if not self.security_manager.rate_limiter.can_execute():
                return CommandResult(False, "Rate limit exceeded. Please wait.")

            # Add command to history
            self.command_history.append({
                'timestamp': datetime.now(),
                'command': command
            })
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)

            # Handle command confirmation
            if self.requires_confirmation(command):
                if not self.command_confirmed:
                    self.last_command = command
                    return CommandResult(True, "Please say 'confirm' to proceed.")
                self.command_confirmed = False

            # Process command through plugins
            for plugin_name, plugin in self.plugins.items():
                try:
                    response = plugin.execute(command)
                    if response:
                        self._update_stats(plugin_name)
                        return CommandResult(True, response, plugin_name)
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_name}: {e}")

            return CommandResult(False, "Command not recognized", None)
        except Exception as e:
            return CommandResult(False, "Error processing command", None, e)

    def _update_stats(self, plugin_name: str):
        if plugin_name not in self.plugin_stats:
            self.plugin_stats[plugin_name] = 0
        self.plugin_stats[plugin_name] += 1

    def confirm_command(self) -> Optional[str]:
        if self.last_command:
            cmd = self.last_command
            self.last_command = None
            self.command_confirmed = True
            return cmd
        return None

    def get_stats(self):
        """Get usage statistics for plugins"""
        return self.plugin_stats

    def get_command_history(self):
        """Get command history"""
        return self.command_history

class SpeechHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.audio_queue = queue.Queue()
        self.command_processor = CommandProcessor()
        self.setup_voice_recognition()
        self.running = True
        self.current_language = LanguageConfig.DEFAULT_LANGUAGE
        self.custom_wake_words = set(CustomizationConfig.WAKE_WORDS["custom"])
        self.wake_word = CustomizationConfig.WAKE_WORDS["default"].lower()
        self._setup_stream()

    def setup_voice_recognition(self):
        if not os.path.exists(Paths.VOSK_MODEL_PATH):
            raise RuntimeError(f"Vosk model not found at {Paths.VOSK_MODEL_PATH}")
        
        self.model = Model(Paths.VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, VoiceConfig.SAMPLE_RATE)

    def _setup_stream(self):
        """Initialize audio stream with proper parameters"""
        self.stream = sd.InputStream(
            samplerate=VoiceConfig.SAMPLE_RATE,
            blocksize=VoiceConfig.BLOCK_SIZE,
            dtype=np.int16,
            channels=VoiceConfig.CHANNELS,
            callback=self._audio_callback
        )
        self.stream.start()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        try:
            self.audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            logger.warning("Audio queue is full, dropping data")

    def speak_text(self, text: str):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")

    def set_language(self, language_code: str):
        if language_code in LanguageConfig.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            self.engine.setProperty(
                'voice', 
                LanguageConfig.TTS_VOICES[language_code]
            )

    def listen_for_wake_word(self) -> bool:
        try:
            while self.running:
                try:
                    data = self.audio_queue.get(timeout=0.5)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").lower().strip()
                        if text:  # Only log if there's actual text
                            logger.debug(f"Heard: '{text}'")
                            if self.wake_word in text:
                                logger.info(f"Wake word detected: {text}")
                                return True
                except queue.Empty:
                    continue
            return False
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            return False

    def get_command(self) -> Optional[str]:
        try:
            self.recognizer.Reset()
            timeout = 0
            
            while timeout < AssistantConfig.COMMAND_TIMEOUT and self.running:
                try:
                    data = self.audio_queue.get(timeout=0.5)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        command_text = result.get("text", "").lower().strip()
                        if command_text:
                            logger.debug(f"Command heard: '{command_text}'")
                            return command_text
                except queue.Empty:
                    timeout += 1
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting command: {e}")
            return None

    def cleanup(self):
        self.running = False
        try:
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
            if hasattr(self, 'engine'):
                self.engine.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class Assistant:
    def __init__(self):
        self.speech_handler = SpeechHandler()
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.stats_thread = threading.Thread(target=self._log_stats, daemon=True)
        self.stats_thread.start()

    def signal_handler(self, signum, frame):
        logger.info("Shutdown signal received")
        self.running = False
        self.speech_handler.cleanup()

    def _log_stats(self):
        """Periodically log plugin usage statistics"""
        while self.running:
            stats = self.speech_handler.command_processor.get_stats()
            logger.info(f"Plugin usage stats: {stats}")
            time.sleep(3600)  # Log every hour

    def run(self):
        logger.info("Canopus started. Waiting for wake word...")
        self.speech_handler.speak_text("Canopus is ready")

        try:
            while self.running:
                if self.speech_handler.listen_for_wake_word():
                    self.speech_handler.speak_text("How can I help?")
                    
                    command = self.speech_handler.get_command()
                    
                    if command == "confirm":
                        command = self.speech_handler.command_processor.confirm_command()
                        if not command:
                            self.speech_handler.speak_text(
                                "No command to confirm"
                            )
                            continue

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
