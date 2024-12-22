<<<<<<< HEAD
import os
import sys
import contextlib

# Redirect ALSA errors to /dev/null
with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stderr(devnull):
        import pyaudio
        import numpy as np
        import whisper
        import webrtcvad
from scipy.signal import butter, lfilter
import queue
=======
import numpy as np
import webrtcvad
from scipy.signal import butter, lfilter
import queue
import whisper
import pyaudio
>>>>>>> origin/main
import threading
import logging
import torch
import time

class AudioProcessor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        try:
            self.vad = webrtcvad.Vad(2)  # Reduced aggressiveness to 2
        except Exception as e:
            self.logger.error(f"Failed to initialize VAD: {e}")
            self.vad = None
        self.buffer = []
        self.is_speech = False
        self.logger = logging.getLogger('canopus.stt.processor')
        self.frame_duration = 30  # ms
        self.frame_length = int(sample_rate * self.frame_duration / 1000)
        
    def _butter_bandpass(self, lowcut=100.0, highcut=3000.0, order=5):
        try:
            nyq = 0.5 * self.sample_rate
            low = lowcut / nyq
            high = highcut / nyq
            b, a = butter(order, [low, high], btype='band')
            return b, a
        except Exception as e:
            self.logger.error(f"Error in filter design: {e}")
            return None, None
            
    def _apply_noise_reduction(self, data):
        b, a = self._butter_bandpass()
        if b is None or a is None:
            return data
        try:
            return lfilter(b, a, data)
        except Exception as e:
            self.logger.error(f"Error in noise reduction: {e}")
            return data
        
    def process_frame(self, frame_data):
        try:
            # Ensure correct frame size for VAD
            if len(frame_data) != self.frame_length * 2:  # *2 for 16-bit audio
                return None
                
            # Convert to float32 for processing
            audio_data = np.frombuffer(frame_data, dtype=np.int16)
            float_data = audio_data.astype(np.float32) / 32768.0
            
            # Apply noise reduction
            cleaned_data = self._apply_noise_reduction(float_data)
            
            # Check for speech if VAD is available
            is_speech = False
            if self.vad:
                try:
                    is_speech = self.vad.is_speech(frame_data, self.sample_rate)
                except Exception:
                    is_speech = True  # Fall back to assuming speech on VAD error
            else:
                # Simple energy-based detection as fallback
                energy = np.mean(np.abs(float_data))
                is_speech = energy > 0.01
            
            if is_speech:
                self.buffer.append(cleaned_data)
                self.is_speech = True
            elif self.is_speech and len(self.buffer) > 0:
                complete_audio = np.concatenate(self.buffer)
                self.buffer = []
                self.is_speech = False
                return (complete_audio * 32768.0).astype(np.int16).tobytes()
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return None

class SpeechToText:
    SUPPORTED_RATES = [8000, 16000, 44100, 48000]
    
    def __init__(self, model_size="base"):
        self.logger = logging.getLogger('canopus.stt')
        try:
<<<<<<< HEAD
            # Redirect ALSA errors during audio initialization
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull):
                    self.model = whisper.load_model(model_size, device="cpu")
                    torch.set_grad_enabled(False)
=======
            self.model = whisper.load_model(model_size, device="cpu")
            torch.set_grad_enabled(False)
>>>>>>> origin/main
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise
        
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.sample_rate = 16000  # Default rate for Whisper
        self.audio_processor = AudioProcessor(self.sample_rate)
        self._stream_lock = threading.Lock()
        self._is_stream_active = False
        self._stream = None
        self.setup_audio()

    def setup_audio(self):
        try:
<<<<<<< HEAD
            # Redirect ALSA errors during audio initialization
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull):
                    self.audio = pyaudio.PyAudio()
                    device_index = self._find_input_device()
                    if device_index is None:
                        raise RuntimeError("No suitable input device found")
                    
                    device_info = self.audio.get_device_info_by_index(device_index)
                    self.logger.info(f"Using audio device: {device_info['name']}")
                    
                    supported_rate = self._get_supported_rate(device_info)
                    if supported_rate != self.sample_rate:
                        self.logger.warning(f"Adjusting sample rate from {self.sample_rate} to {supported_rate}")
                        self.sample_rate = supported_rate
                    
                    with self._stream_lock:
                        self._stream = self.audio.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=self.sample_rate,
                            input=True,
                            frames_per_buffer=int(self.sample_rate * 0.03),
                            input_device_index=device_index,
                            start=False  # Don't start immediately
                        )
                        self.chunk = int(self.sample_rate * 0.03)
                        self._is_stream_active = False
=======
            self.audio = pyaudio.PyAudio()
            device_index = self._find_input_device()
            if device_index is None:
                raise RuntimeError("No suitable input device found")
            
            device_info = self.audio.get_device_info_by_index(device_index)
            self.logger.info(f"Using audio device: {device_info['name']}")
            
            supported_rate = self._get_supported_rate(device_info)
            if supported_rate != self.sample_rate:
                self.logger.warning(f"Adjusting sample rate from {self.sample_rate} to {supported_rate}")
                self.sample_rate = supported_rate
            
            with self._stream_lock:
                self._stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=int(self.sample_rate * 0.03),
                    input_device_index=device_index,
                    start=False  # Don't start immediately
                )
                self.chunk = int(self.sample_rate * 0.03)
                self._is_stream_active = False
>>>>>>> origin/main
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self._cleanup_audio()
            raise

    def _find_input_device(self):
        """Find the best available input device"""
        try:
            default_device = self.audio.get_default_input_device_info()
            if self._is_device_suitable(default_device):
                return default_device['index']
        except:
            pass

        # Fall back to searching all devices
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if self._is_device_suitable(device_info):
                return i
        return None

    def _is_device_suitable(self, device_info):
        """Check if a device is suitable for our needs"""
        try:
            return (
                device_info['maxInputChannels'] > 0 and
                device_info['hostApi'] == 0 and  # Prefer default host API
                any(abs(rate - self.sample_rate) < 100 
                    for rate in self.SUPPORTED_RATES)
            )
        except:
            return False

    def _get_supported_rate(self, device_info):
        """Get the closest supported sample rate"""
        try:
            default_rate = int(device_info.get('defaultSampleRate', 44100))
            if abs(default_rate - self.sample_rate) < 100:
                return self.sample_rate
            
            # Find closest supported rate
            rates = sorted(self.SUPPORTED_RATES, 
                         key=lambda x: abs(x - default_rate))
            return rates[0]
        except:
            return 44100  # Safe fallback

    def start_listening(self):
        try:
            with self._stream_lock:
                if self._stream and not self._is_stream_active:
                    self._stream.start_stream()
                    self._is_stream_active = True
            
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._audio_processing_loop)
            self.listen_thread.daemon = True
            self.listen_thread.start()
        except Exception as e:
            self.logger.error(f"Error starting audio stream: {e}")
            self._cleanup_audio()

    def stop_listening(self):
        self.is_listening = False
        try:
            if hasattr(self, 'listen_thread'):
                self.listen_thread.join(timeout=2.0)  # Wait up to 2 seconds
            self._cleanup_audio()
        except Exception as e:
            self.logger.error(f"Error stopping audio stream: {e}")

    def _cleanup_audio(self):
        """Safely cleanup audio resources"""
        with self._stream_lock:
            if self._stream:
                if self._is_stream_active:
                    try:
                        self._stream.stop_stream()
                    except Exception as e:
                        self.logger.debug(f"Error stopping stream: {e}")
                try:
                    self._stream.close()
                except Exception as e:
                    self.logger.debug(f"Error closing stream: {e}")
                self._stream = None
                self._is_stream_active = False
            
            if hasattr(self, 'audio') and self.audio:
                try:
                    self.audio.terminate()
                except Exception as e:
                    self.logger.debug(f"Error terminating PyAudio: {e}")
                self.audio = None

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Handle audio data in callback mode"""
        try:
            processed_data = self.audio_processor.process_frame(in_data)
            if processed_data:
                self.audio_queue.put(processed_data)
            return (in_data, pyaudio.paContinue)
        except Exception as e:
            self.logger.error(f"Audio callback error: {e}")
            return (in_data, pyaudio.paContinue)

    def _audio_processing_loop(self):
        while self.is_listening:
            try:
                with self._stream_lock:
                    if not (self._stream and self._is_stream_active):
                        time.sleep(0.1)
                        continue
                    
                    data = self._stream.read(self.chunk, exception_on_overflow=False)
                
                processed_data = self.audio_processor.process_frame(data)
                if processed_data:
                    self.audio_queue.put(processed_data)
                    self.logger.debug("Audio frame processed and queued")
                    
            except IOError as e:
                if e.errno == -9988:  # Stream closed
                    break
                self.logger.error(f"IO Error in audio processing: {e}")
            except Exception as e:
                self.logger.error(f"Error in audio processing: {e}")
                if not self.is_listening:
                    break

    def transcribe(self):
        while not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            result = self.model.transcribe(audio_data)
            print(result["text"])

    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.stop_listening()
